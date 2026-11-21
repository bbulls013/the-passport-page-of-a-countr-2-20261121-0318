#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Invented passport spread — Republic of Virelai.

Writes a deterministic 1024x1024 PNG to /output/entry.png
(falls back to ./entry.png when /output is unavailable).
Stdlib + Pillow only. No network. No randomness.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

# --- fonts -------------------------------------------------------------
def load_font(paths, size):
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                continue
    return ImageFont.load_default()

SERIF = ["/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
         "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"]
SERIF_B = ["/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
           "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"]
SANS = ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"]
SANS_B = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
          "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]
MONO = ["/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf"]
MONO_B = ["/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
          "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"]

F_TITLE = load_font(SERIF_B, 30)
F_SUB = load_font(SANS, 13)
F_LABEL = load_font(SANS_B, 11)
F_VALUE = load_font(SANS_B, 17)
F_VALUE_S = load_font(SANS, 14)
F_SMALL = load_font(SANS, 11)
F_TINY = load_font(SANS, 9)
F_MRZ = load_font(MONO, 15)
F_MRZ_B = load_font(MONO_B, 15)
F_STAMP_B = load_font(SANS_B, 13)
F_STAMP = load_font(SANS, 11)
F_PAGE = load_font(SERIF, 13)
F_FEE = load_font(SANS_B, 10)

# --- palette -----------------------------------------------------------
PAPER = (244, 241, 230)
PAPER_D = (232, 227, 208)
INK = (28, 34, 52)
INK_SOFT = (72, 80, 102)
RULE = (150, 148, 128)
GOLD = (138, 112, 52)
NAVY = (24, 42, 84)
TEAL = (22, 92, 96)
RUST = (146, 58, 38)
GREEN = (46, 96, 58)
PLUM = (92, 48, 88)
SKIN = (222, 184, 150)
HAIR = (62, 44, 34)
SHIRT = (44, 66, 110)
PORTRAIT_BG = (206, 214, 224)


def text_w(draw, s, font):
    box = draw.textbbox((0, 0), s, font=font)
    return box[2] - box[0]


def draw_centred(draw, cx, y, s, font, fill):
    w = text_w(draw, s, font)
    draw.text((cx - w // 2, y), s, font=font, fill=fill)


def guilloche_border(draw, box, colour):
    x0, y0, x1, y1 = box
    for i in range(3):
        draw.rectangle([x0 + i * 3, y0 + i * 3, x1 - i * 3, y1 - i * 3],
                       outline=colour, width=1)
    # subtle second guilloche ring: one extra inner frame, slightly paler,
    # so the border reads as layered security printing rather than a single rule
    pale = tuple(min(255, c + 18) for c in colour)
    draw.rectangle([x0 + 10, y0 + 10, x1 - 10, y1 - 10], outline=pale, width=1)
    # corner rosettes: small concentric circles (outer ring added for the
    # second-guilloche effect, matching the extra inner frame)
    for cx, cy in [(x0 + 14, y0 + 14), (x1 - 14, y0 + 14),
                   (x0 + 14, y1 - 14), (x1 - 14, y1 - 14)]:
        for r in (12, 9, 6, 3):
            ring = pale if r == 12 else colour
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=ring, width=1)


def field(draw, x, y, label, value, value_font=F_VALUE):
    draw.text((x, y), label, font=F_LABEL, fill=INK_SOFT)
    draw.text((x, y + 15), value, font=value_font, fill=INK)
    return y + 42


def draw_portrait(draw, box):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=PORTRAIT_BG, outline=INK, width=2)
    cx = (x0 + x1) // 2
    # shoulders / shirt
    draw.polygon([(x0 + 18, y1), (cx - 52, y1 - 62), (cx + 52, y1 - 62),
                  (x1 - 18, y1)], fill=SHIRT)
    draw.polygon([(cx - 14, y1 - 62), (cx + 14, y1 - 62), (cx, y1 - 34)],
                 fill=(240, 240, 238))
    # neck
    draw.rectangle([cx - 12, y0 + 108, cx + 12, y0 + 134], fill=SKIN)
    # head
    draw.ellipse([cx - 42, y0 + 22, cx + 42, y0 + 118], fill=SKIN, outline=HAIR, width=1)
    # hair cap with soft side fall
    draw.pieslice([cx - 44, y0 + 14, cx + 44, y0 + 82], 180, 360, fill=HAIR)
    draw.polygon([(cx - 44, y0 + 52), (cx - 34, y0 + 52), (cx - 36, y0 + 102),
                  (cx - 44, y0 + 96)], fill=HAIR)
    draw.polygon([(cx + 44, y0 + 52), (cx + 34, y0 + 52), (cx + 36, y0 + 102),
                  (cx + 44, y0 + 96)], fill=HAIR)
    draw.arc([cx - 30, y0 + 24, cx + 30, y0 + 62], 190, 350, fill=(96, 72, 52), width=2)
    # eyes, brows, nose, mouth
    for ex in (cx - 18, cx + 18):
        draw.ellipse([ex - 5, y0 + 70, ex + 5, y0 + 78], fill=INK)
        draw.line([ex - 8, y0 + 62, ex + 8, y0 + 62], fill=HAIR, width=2)
    draw.line([cx, y0 + 78, cx - 3, y0 + 92], fill=(170, 128, 96), width=2)
    draw.arc([cx - 12, y0 + 94, cx + 12, y0 + 108], 15, 165, fill=(150, 84, 70), width=2)
    # faint hologram circle
    draw.ellipse([x1 - 44, y1 - 44, x1 - 10, y1 - 10], outline=GOLD, width=2)
    draw.ellipse([x1 - 36, y1 - 36, x1 - 18, y1 - 18], outline=GOLD, width=1)


def draw_stamp(draw, cx, cy, colour, lines, w=196, h=104, angle_rect=True):
    x0, y0, x1, y1 = cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2
    draw.rounded_rectangle([x0, y0, x1, y1], radius=10, outline=colour, width=3)
    draw.rounded_rectangle([x0 + 5, y0 + 5, x1 - 5, y1 - 5], radius=7,
                           outline=colour, width=1)
    ty = y0 + 10
    for i, line in enumerate(lines):
        f = F_STAMP_B if i in (0, 2) else F_STAMP
        draw_centred(draw, cx, ty, line, f, colour)
        ty += 19 if i != 1 else 21


def main():
    img = Image.new("RGB", (W, H), (58, 54, 48))
    d = ImageDraw.Draw(img)

    # desk shadow + open spread
    d.rectangle([28, 44, 996, 980], fill=(40, 38, 34))
    d.rectangle([20, 36, 1004, 972], fill=PAPER, outline=(120, 116, 100), width=1)
    # page halves
    d.rectangle([20, 36, 512, 972], fill=PAPER)
    d.rectangle([512, 36, 1004, 972], fill=(248, 246, 236))
    # centre fold shading
    for i in range(14):
        shade = 232 - i * 3
        d.line([512 - i, 36, 512 - i, 972], fill=(shade, shade - 4, shade - 16))
        d.line([512 + i, 36, 512 + i, 972], fill=(shade + 6, shade + 2, shade - 10))
    d.line([512, 36, 512, 972], fill=(196, 192, 172), width=2)

    # faint guilloche waves (deterministic sine rows)
    import math
    for page_x0 in (44, 536):
        for row in range(9):
            yy = 96 + row * 96
            pts = []
            for xx in range(page_x0, page_x0 + 444, 6):
                pts.append((xx, yy + int(7 * math.sin((xx - page_x0) / 26.0 + row))))
            d.line(pts, fill=(222, 218, 196), width=1)

    guilloche_border(d, (40, 56, 492, 952), (176, 168, 132))
    guilloche_border(d, (532, 56, 984, 952), (176, 168, 132))

    # ---------------- LEFT: data page ----------------
    draw_centred(d, 266, 76, "REPUBLIC OF VIRELAI", F_TITLE, NAVY)
    draw_centred(d, 266, 112, "PASSPORT  ·  PASSEPORT  ·  PASAPORTE", F_SUB, INK_SOFT)
    d.line([76, 136, 456, 136], fill=GOLD, width=2)
    # coat-of-arms mark: shield with wave + star
    sx, sy = 266, 150
    d.polygon([(sx - 26, sy), (sx + 26, sy), (sx + 26, sy + 30),
               (sx, sy + 48), (sx - 26, sy + 30)], outline=NAVY, width=2)
    d.arc([sx - 18, sy + 18, sx + 18, sy + 38], 0, 180, fill=TEAL, width=2)
    d.text((sx - 6, sy + 2), "*", font=F_VALUE, fill=GOLD)

    draw_portrait(d, (72, 216, 232, 412))
    d.text((72, 418), "Holder's portrait", font=F_TINY, fill=INK_SOFT)
    # flowing signature under portrait (fixed sine stroke, no randomness)
    import math as _m
    sig_pts = [(82 + i * 3, 448 + int(7 * _m.sin(i / 3.2)) - (6 if 18 < i < 26 else 0))
               for i in range(47)]
    d.line(sig_pts, fill=INK, width=2)
    d.line([(84, 456), (216, 452)], fill=INK, width=1)
    d.text((72, 458), "Signature of holder", font=F_TINY, fill=INK_SOFT)

    x = 252
    y = 214
    y = field(d, x, y, "TYPE / TYPE", "P")
    y = field(d, x, y, "COUNTRY CODE", "VRL")
    y = field(d, x, y, "PASSPORT No.", "VRL 4829106", F_VALUE_S)
    y = field(d, x, y, "SURNAME", "MARREN")
    y = field(d, x, y, "GIVEN NAMES", "Sella Ana")
    # full-width fields below portrait block
    y = 486
    d.line([72, y - 6, 460, y - 6], fill=RULE, width=1)
    y = field(d, 72, y, "DATE OF BIRTH", "04 JUN 1991", F_VALUE_S)
    y = field(d, 72, y, "PLACE OF BIRTH", "Port Saren, Virelai", F_VALUE_S)
    y = field(d, 72, y, "SEX / HEIGHT", "F  ·  168 cm", F_VALUE_S)
    y = field(d, 72, y, "DATE OF ISSUE", "12 MAR 2022", F_VALUE_S)
    y = field(d, 72, y, "DATE OF EXPIRY", "11 MAR 2032", F_VALUE_S)
    y = field(d, 72, y, "ISSUING AUTHORITY", "Harbour Registry, Port Saren", F_VALUE_S)
    # bilingual language column (telling detail, part 1)
    y += 2
    d.text((72, y), "Languages / Langues:", font=F_LABEL, fill=INK_SOFT)
    d.text((72, y + 15), "Virelaian · English · French", font=F_SMALL, fill=INK)

    # MRZ
    mrz_y = 820
    d.rectangle([60, mrz_y, 472, mrz_y + 92], fill=(238, 236, 224), outline=RULE, width=1)
    d.text((72, mrz_y + 10), "P<VRLMARREN<<SELLA<ANA<<<<<<<<<<<<<<<<<<<<", font=F_MRZ, fill=INK)
    d.text((72, mrz_y + 38), "4829106<7VRL9106048F3203112<<<<<<<<<<<<<<04", font=F_MRZ, fill=INK)
    d.text((72, mrz_y + 66), "Machine-readable zone — do not fold", font=F_TINY, fill=INK_SOFT)
    draw_centred(d, 266, 928, "2", F_PAGE, INK_SOFT)

    # ---------------- RIGHT: visas / stamps ----------------
    draw_centred(d, 758, 76, "VISAS & STAMPS", F_TITLE, NAVY)
    draw_centred(d, 758, 112, "VISAS ET TAMPONS  ·  VISADOS Y SELLOS", F_SUB, INK_SOFT)
    d.line([568, 136, 948, 136], fill=GOLD, width=2)
    d.text((560, 148), "This passport is valid for travel to all countries.",
           font=F_SMALL, fill=INK)
    d.text((560, 166), "Bearer must register with the harbour master", font=F_SMALL, fill=INK)
    d.text((560, 182), "within 24 hours of arrival by island ferry.", font=F_SMALL, fill=INK)

    # fee stamp (telling detail, part 2)
    d.rounded_rectangle([828, 146, 956, 198], radius=6, outline=RUST, width=2)
    draw_centred(d, 892, 154, "FEE PAID", F_FEE, RUST)
    draw_centred(d, 892, 168, "24 KR · PORT SAREN", F_TINY, RUST)
    draw_centred(d, 892, 180, "12 MAR 2022", F_TINY, RUST)

    # stamps in chronological order, all after 12 MAR 2022, before expiry
    draw_stamp(d, 658, 268, TEAL,
               ["KORVIA — ARRIVAL", "Port Telm  ·  Ferry 7", "18 JUN 2023", "30 DAYS"])
    draw_stamp(d, 858, 368, NAVY,
               ["KORVIA — DEPARTURE", "Port Telm", "02 JUL 2023", ""])
    draw_stamp(d, 658, 468, GREEN,
               ["OSTRAVA — ENTRY", "Lumen Airfield", "09 OCT 2024", "90 DAYS"])
    draw_stamp(d, 858, 568, PLUM,
               ["OSTRAVA — EXIT", "Lumen Airfield", "27 OCT 2024", ""])
    draw_stamp(d, 658, 668, RUST,
               ["BRIN ISLES — ARRIVAL", "Harbour Master, Cay Brin", "14 MAY 2025", "FERRY ONLY"])

    # visa condition box (the one telling paperwork detail)
    vy = 742
    d.rectangle([560, vy, 956, vy + 104], outline=NAVY, width=2)
    d.text((574, vy + 10), "BRIN ISLES — TRANSIT VISA  No. B-1187", font=F_STAMP_B, fill=NAVY)
    d.text((574, vy + 32), "Valid for island ferries only. Bearer must", font=F_SMALL, fill=INK)
    d.text((574, vy + 48), "register with the harbour master within 24h", font=F_SMALL, fill=INK)
    d.text((574, vy + 64), "of landing and surrender this page on exit.", font=F_SMALL, fill=INK)
    d.text((574, vy + 82), "Issued Cay Brin, 14 MAY 2025 · Fee 6 shells", font=F_TINY, fill=INK_SOFT)

    # perforated passport number down the outer edge (paperwork detail)
    for i, ch in enumerate("4829106"):
        d.text((966, 300 + i * 26), ch, font=F_TINY, fill=(168, 164, 146))

    draw_centred(d, 758, 928, "3", F_PAGE, INK_SOFT)

    out = "/output/entry.png"
    try:
        os.makedirs("/output", exist_ok=True)
        img.save(out, "PNG", optimize=False)
    except OSError:
        out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
        img.save(out, "PNG", optimize=False)
    print(out)


if __name__ == "__main__":
    main()
