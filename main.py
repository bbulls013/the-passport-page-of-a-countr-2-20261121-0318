#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Invented passport spread - Republic of Virelai. Stdlib only."""
import os, zlib, struct, math

W, H = 1024, 1024

# 5x7 bitmap font: 7 rows, bits 4..0 left to right
FONT = {
'A':[0x0E,0x11,0x11,0x1F,0x11,0x11,0x11],
'B':[0x1E,0x11,0x11,0x1E,0x11,0x11,0x1E],
'C':[0x0E,0x11,0x10,0x10,0x10,0x11,0x0E],
'D':[0x1C,0x12,0x11,0x11,0x11,0x12,0x1C],
'E':[0x1F,0x10,0x10,0x1E,0x10,0x10,0x1F],
'F':[0x1F,0x10,0x10,0x1E,0x10,0x10,0x10],
'G':[0x0E,0x11,0x10,0x17,0x11,0x11,0x0F],
'H':[0x11,0x11,0x11,0x1F,0x11,0x11,0x11],
'I':[0x0E,0x04,0x04,0x04,0x04,0x04,0x0E],
'J':[0x07,0x02,0x02,0x02,0x02,0x12,0x0C],
'K':[0x11,0x12,0x14,0x18,0x14,0x12,0x11],
'L':[0x10,0x10,0x10,0x10,0x10,0x10,0x1F],
'M':[0x11,0x1B,0x15,0x15,0x11,0x11,0x11],
'N':[0x11,0x19,0x15,0x13,0x11,0x11,0x11],
'O':[0x0E,0x11,0x11,0x11,0x11,0x11,0x0E],
'P':[0x1E,0x11,0x11,0x1E,0x10,0x10,0x10],
'Q':[0x0E,0x11,0x11,0x11,0x15,0x12,0x0D],
'R':[0x1E,0x11,0x11,0x1E,0x14,0x12,0x11],
'S':[0x0F,0x10,0x10,0x0E,0x01,0x01,0x1E],
'T':[0x1F,0x04,0x04,0x04,0x04,0x04,0x04],
'U':[0x11,0x11,0x11,0x11,0x11,0x11,0x0E],
'V':[0x11,0x11,0x11,0x11,0x11,0x0A,0x04],
'W':[0x11,0x11,0x11,0x15,0x15,0x15,0x0A],
'X':[0x11,0x0A,0x04,0x04,0x04,0x0A,0x11],
'Y':[0x11,0x0A,0x04,0x04,0x04,0x04,0x04],
'Z':[0x1F,0x01,0x02,0x04,0x08,0x10,0x1F],
'0':[0x0E,0x11,0x13,0x15,0x19,0x11,0x0E],
'1':[0x04,0x0C,0x04,0x04,0x04,0x04,0x0E],
'2':[0x0E,0x11,0x01,0x02,0x04,0x08,0x1F],
'3':[0x1F,0x02,0x04,0x02,0x01,0x11,0x0E],
'4':[0x02,0x06,0x0A,0x12,0x1F,0x02,0x02],
'5':[0x1F,0x10,0x1E,0x01,0x01,0x11,0x0E],
'6':[0x06,0x08,0x10,0x1E,0x11,0x11,0x0E],
'7':[0x1F,0x01,0x02,0x04,0x04,0x04,0x04],
'8':[0x0E,0x11,0x11,0x0E,0x11,0x11,0x0E],
'9':[0x0E,0x11,0x11,0x0F,0x01,0x02,0x0C],
' ':[0,0,0,0,0,0,0],
'.':[0,0,0,0,0,0x0C,0x0C],
',':[0,0,0,0,0x0C,0x04,0x08],
'-':[0,0,0,0x1F,0,0,0],
':':[0,0x0C,0x0C,0,0x0C,0x0C,0],
'/':[0x01,0x02,0x02,0x04,0x08,0x08,0x10],
"'":[0x04,0x04,0x08,0,0,0,0],
'(':[0x02,0x04,0x08,0x08,0x08,0x04,0x02],
')':[0x08,0x04,0x02,0x02,0x02,0x04,0x08],
'<':[0x02,0x04,0x08,0x10,0x08,0x04,0x02],
'>':[0x08,0x04,0x02,0x01,0x02,0x04,0x08],
'&':[0x0C,0x12,0x14,0x08,0x15,0x12,0x0D],
'*':[0,0x04,0x15,0x0E,0x15,0x04,0],
'+':[0,0x04,0x04,0x1F,0x04,0x04,0],
'#':[0x0A,0x1F,0x0A,0x0A,0x1F,0x0A,0],
'!':[0x04,0x04,0x04,0x04,0x04,0,0x04],
'?':[0x0E,0x11,0x01,0x02,0x04,0,0x04],
'=':[0,0,0x1F,0,0x1F,0,0],
'_':[0,0,0,0,0,0,0x1F],
}

PAPER=(244,241,230); INK=(28,34,52); INK_SOFT=(72,80,102)
RULE=(150,148,128); GOLD=(138,112,52); NAVY=(24,42,84)
TEAL=(22,92,96); RUST=(146,58,38); GREEN=(46,96,58); PLUM=(92,48,88)
SKIN=(222,184,150); HAIR=(62,44,34); SHIRT=(44,66,110); PBG=(206,214,224)

class Canvas:
    def __init__(self,w,h,bg):
        self.w=w; self.h=h; self.px=bytearray(w*h*3)
        r,g,b=bg
        for i in range(w*h):
            self.px[i*3]=r; self.px[i*3+1]=g; self.px[i*3+2]=b
    def set(self,x,y,c):
        if 0<=x<self.w and 0<=y<self.h:
            i=(y*self.w+x)*3; self.px[i]=c[0]; self.px[i+1]=c[1]; self.px[i+2]=c[2]
    def rect(self,x0,y0,x1,y1,c):
        x0=max(0,x0); y0=max(0,y0); x1=min(self.w-1,x1); y1=min(self.h-1,y1)
        for y in range(y0,y1+1):
            base=y*self.w*3
            for x in range(x0,x1+1):
                i=base+x*3; self.px[i]=c[0]; self.px[i+1]=c[1]; self.px[i+2]=c[2]
    def box(self,x0,y0,x1,y1,c,t=1):
        for k in range(t):
            self.rect(x0+k,y0+k,x1-k,y0+k,c); self.rect(x0+k,y1-k,x1-k,y1-k,c)
            self.rect(x0+k,y0+k,x0+k,y1-k,c); self.rect(x1-k,y0+k,x1-k,y1-k,c)
    def line(self,x0,y0,x1,y1,c,t=1):
        dx=abs(x1-x0); dy=-abs(y1-y0)
        sx=1 if x0<x1 else -1; sy=1 if y0<y1 else -1
        err=dx+dy; x,y=x0,y0
        while True:
            for a in range(t):
                for b in range(t): self.set(x+a,y+b,c)
            if x==x1 and y==y1: break
            e2=2*err
            if e2>=dy: err+=dy; x+=sx
            if e2<=dx: err+=dx; y+=sy
    def ellipse(self,cx,cy,rx,ry,c,fill=True):
        for y in range(cy-ry,cy+ry+1):
            for x in range(cx-rx,cx+rx+1):
                v=((x-cx)/max(1,rx))**2+((y-cy)/max(1,ry))**2
                if fill:
                    if v<=1.0: self.set(x,y,c)
                else:
                    if 0.85<v<=1.05: self.set(x,y,c)
    def circle(self,cx,cy,r,c,fill=True): self.ellipse(cx,cy,r,r,c,fill)
    def text_w(self,s,scale): return len(s)*(5*scale+scale)-scale if s else 0
    def text(self,x,y,s,scale,c):
        s=s.upper(); cx=x
        for ch in s:
            g=FONT.get(ch,FONT['?'])
            for row in range(7):
                bits=g[row]
                for col in range(5):
                    if bits>>(4-col)&1:
                        self.rect(cx+col*scale,y+row*scale,cx+col*scale+scale-1,y+row*scale+scale-1,c)
            cx+=5*scale+scale
        return cx
    def text_c(self,cx,y,s,scale,c):
        self.text(cx-self.text_w(s,scale)//2,y,s,scale,c)

def png_bytes(cv):
    raw=bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw.extend(cv.px[y*cv.w*3:(y+1)*cv.w*3])
    comp=zlib.compress(bytes(raw),6)
    def chunk(typ,data):
        c=struct.pack('>I',len(data))+typ+data
        c+=struct.pack('>I',zlib.crc32(typ+data)&0xffffffff)
        return c
    ihdr=struct.pack('>IIBBBBB',cv.w,cv.h,8,2,0,0,0)
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',ihdr)+chunk(b'IDAT',comp)+chunk(b'IEND',b'')

def border(cv,x0,y0,x1,y1,c):
    for i in range(3): cv.box(x0+i*3,y0+i*3,x1-i*3,y1-i*3,c,1)
    pale=tuple(min(255,v+18) for v in c)
    cv.box(x0+10,y0+10,x1-10,y1-10,pale,1)
    for cx,cy in [(x0+14,y0+14),(x1-14,y0+14),(x0+14,y1-14),(x1-14,y1-14)]:
        for r in (12,9,6,3): cv.circle(cx,cy,r,pale if r==12 else c,False)

def field(cv,x,y,label,value,vs=2):
    cv.text(x,y,label,1,INK_SOFT); cv.text(x,y+10,value,vs,INK); return y+10+7*vs+8

def portrait(cv,x0,y0,x1,y1):
    cv.rect(x0,y0,x1,y1,PBG); cv.box(x0,y0,x1,y1,INK,2)
    cx=(x0+x1)//2
    cv.rect(x0+18,y1-62,x1-18,y1,SHIRT)
    cv.rect(cx-14,y1-62,cx+14,y1-34,(240,240,238))
    cv.rect(cx-12,y0+108,cx+12,y0+134,SKIN)
    cv.ellipse(cx,y0+70,42,48,SKIN,True)
    cv.ellipse(cx,y0+70,42,48,HAIR,False)
    # hair cap: top half ellipse
    for yy in range(y0+14,y0+62):
        for xx in range(cx-44,cx+45):
            if ((xx-cx)/44)**2+((yy-(y0+48))/34)**2<=1.0 and yy<y0+58:
                cv.set(xx,yy,HAIR)
    cv.rect(cx-44,y0+52,cx-34,y0+102,HAIR); cv.rect(cx+34,y0+52,cx+44,y0+102,HAIR)
    for ex in (cx-18,cx+18):
        cv.ellipse(ex,y0+74,5,4,INK,True); cv.rect(ex-8,y0+62,ex+8,y0+64,HAIR)
    cv.line(cx,y0+78,cx-3,y0+92,(170,128,96),2)
    cv.line(cx-12,y0+102,cx+12,y0+102,(150,84,70),2)
    cv.circle(x1-27,y1-27,17,GOLD,False); cv.circle(x1-27,y1-27,9,GOLD,False)

def stamp(cv,cx,cy,c,lines,w=210,h=110):
    x0,y0,x1,y1=cx-w//2,cy-h//2,cx+w//2,cy+h//2
    cv.box(x0,y0,x1,y1,c,3); cv.box(x0+5,y0+5,x1-5,y1-5,c,1)
    ty=y0+12
    for i,ln in enumerate(lines):
        if not ln: continue
        sc=2 if i in (0,2) else 1
        if cv.text_w(ln,sc)>w-16: sc=1
        cv.text_c(cx,ty,ln,sc,c); ty+=20 if sc==2 else 14

def main():
    cv=Canvas(W,H,(58,54,48))
    cv.rect(28,44,996,980,(40,38,34))
    cv.rect(20,36,1004,972,PAPER); cv.box(20,36,1004,972,(120,116,100),1)
    cv.rect(512,36,1004,972,(248,246,236))
    for i in range(14):
        s=232-i*3
        cv.line(512-i,36,512-i,972,(s,s-4,s-16)); cv.line(512+i,36,512+i,972,(s+6,s+2,s-10))
    cv.rect(511,36,512,972,(196,192,172))
    for px0 in (44,536):
        for row in range(9):
            yy=96+row*96
            for xx in range(px0,px0+444,6):
                cv.set(xx,yy+int(7*math.sin((xx-px0)/26.0+row)),(222,218,196))
    border(cv,40,56,492,952,(176,168,132)); border(cv,532,56,984,952,(176,168,132))
    # LEFT
    cv.text_c(266,72,"REPUBLIC OF VIRELAI",3,NAVY)
    cv.text_c(266,100,"PASSPORT - PASSEPORT - PASAPORTE",1,INK_SOFT)
    cv.rect(76,116,456,117,GOLD)
    sx,sy=266,128
    cv.box(sx-26,sy,sx+26,sy+30,NAVY,2)
    cv.line(sx-26,sy+30,sx,sy+48,NAVY,2); cv.line(sx+26,sy+30,sx,sy+48,NAVY,2)
    cv.text_c(sx,sy+6,"*",2,GOLD); cv.rect(sx-16,sy+22,sx+16,sy+24,TEAL)
    portrait(cv,72,216,232,412)
    cv.text(72,418,"HOLDER PORTRAIT",1,INK_SOFT)
    for i in range(47):
        cv.set(82+i*3,448+int(7*math.sin(i/3.2))-(6 if 18<i<26 else 0),INK)
        cv.set(82+i*3,449+int(7*math.sin(i/3.2))-(6 if 18<i<26 else 0),INK)
    cv.line(84,456,216,452,INK,1); cv.text(72,462,"SIGNATURE OF HOLDER",1,INK_SOFT)
    y=214
    y=field(cv,252,y,"TYPE / TYPE","P")
    y=field(cv,252,y,"COUNTRY CODE","VRL")
    y=field(cv,252,y,"PASSPORT NO.","VRL 4829106",2)
    y=field(cv,252,y,"SURNAME","MARREN")
    y=field(cv,252,y,"GIVEN NAMES","SELLA ANA")
    y=486; cv.rect(72,y-6,460,y-5,RULE)
    y=field(cv,72,y,"DATE OF BIRTH","04 JUN 1991")
    y=field(cv,72,y,"PLACE OF BIRTH","PORT SAREN, VIRELAI",2)
    y=field(cv,72,y,"SEX / HEIGHT","F - 168 CM")
    y=field(cv,72,y,"DATE OF ISSUE","12 MAR 2022")
    y=field(cv,72,y,"DATE OF EXPIRY","11 MAR 2032")
    y=field(cv,72,y,"ISSUING AUTHORITY","HARBOUR REGISTRY, PORT SAREN",1)
    y+=2; cv.text(72,y,"LANGUAGES / LANGUES:",1,INK_SOFT)
    cv.text(72,y+10,"VIRELAIAN / ENGLISH / FRENCH",1,INK)
    mrz=820; cv.rect(60,mrz,472,mrz+92,(238,236,224)); cv.box(60,mrz,472,mrz+92,RULE,1)
    cv.text(72,mrz+10,"P<VRLMARREN<<SELLA<ANA<<<<<<<<<<<<<<<<<<<<",1,INK)
    cv.text(72,mrz+26,"4829106<7VRL9106048F3203112<<<<<<<<<<<<<<04",1,INK)
    cv.text(72,mrz+44,"MACHINE-READABLE ZONE - DO NOT FOLD",1,INK_SOFT)
    cv.text_c(266,928,"2",2,INK_SOFT)
    # RIGHT
    cv.text_c(758,72,"VISAS & STAMPS",3,NAVY)
    cv.text_c(758,100,"VISAS ET TAMPONS - VISADOS Y SELLOS",1,INK_SOFT)
    cv.rect(568,116,948,117,GOLD)
    cv.text(560,128,"VALID FOR TRAVEL TO ALL COUNTRIES.",1,INK)
    cv.text(560,140,"REGISTER WITH HARBOUR MASTER IN 24H",1,INK)
    cv.text(560,152,"OF ARRIVAL BY ISLAND FERRY.",1,INK)
    cv.box(828,146,956,198,RUST,2)
    cv.text_c(892,152,"FEE PAID",1,RUST); cv.text_c(892,164,"24 KR - PORT SAREN",1,RUST)
    cv.text_c(892,176,"12 MAR 2022",1,RUST)
    stamp(cv,658,268,TEAL,["KORVIA - ARRIVAL","PORT TELM - FERRY 7","18 JUN 2023","30 DAYS"])
    stamp(cv,858,368,NAVY,["KORVIA - DEPARTURE","PORT TELM","02 JUL 2023",""])
    stamp(cv,658,468,GREEN,["OSTRAVA - ENTRY","LUMEN AIRFIELD","09 OCT 2024","90 DAYS"])
    stamp(cv,858,568,PLUM,["OSTRAVA - EXIT","LUMEN AIRFIELD","27 OCT 2024",""])
    stamp(cv,658,668,RUST,["BRIN ISLES - ARRIVAL","HARBOUR MASTER, CAY BRIN","14 MAY 2025","FERRY ONLY"])
    vy=742; cv.box(560,vy,956,vy+104,NAVY,2)
    cv.text(574,vy+10,"BRIN ISLES TRANSIT VISA B-1187",2,NAVY)
    cv.text(574,vy+34,"ISLAND FERRIES ONLY - REGISTER WITH",1,INK)
    cv.text(574,vy+46,"HARBOUR MASTER WITHIN 24H OF LANDING",1,INK)
    cv.text(574,vy+58,"AND SURRENDER THIS PAGE ON EXIT.",1,INK)
    cv.text(574,vy+74,"ISSUED CAY BRIN, 14 MAY 2025 - FEE 6 SHELLS",1,INK_SOFT)
    for i,ch in enumerate("4829106"): cv.text(966,300+i*26,ch,1,(168,164,146))
    cv.text_c(758,928,"3",2,INK_SOFT)
    data=png_bytes(cv)
    out="/output/entry.png"
    try:
        os.makedirs("/output",exist_ok=True)
        with open(out,"wb") as f: f.write(data)
    except OSError:
        out=os.path.join(os.path.dirname(os.path.abspath(__file__)),"entry.png")
        with open(out,"wb") as f: f.write(data)
    print(out)

if __name__=="__main__":
    main()
