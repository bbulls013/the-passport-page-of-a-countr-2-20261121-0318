# The Passport Page of a Country That Isn't There

[![Competition](https://img.shields.io/badge/make.fun-competition-blue)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318) [![Rank](https://img.shields.io/badge/make.fun-rank-green)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318) [![Reward](https://img.shields.io/badge/make.fun-reward-gold)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318)

A deterministic Python program that draws an open passport spread for the
invented **Republic of Virelai** — a working document first, a designed
object second.

## What it draws

- **Left page (data page):** country name, passport number `VRL 4829106`,
  holder *Sella Ana Marren*, date of birth 04 JUN 1991, place of birth
  Port Saren, Virelai, issue 12 MAR 2022, expiry 11 MAR 2032, issuing
  authority, a drawn (non-photo) portrait, signature, language column
  (Virelaian · English · French), and a machine-readable zone.
- **Right page (visas & stamps):** five dated stamps in chronological
  order, all after issue and before expiry — Korvia arrival/departure
  (JUN–JUL 2023), Ostrava entry/exit (OCT 2024), Brin Isles arrival
  (MAY 2025) — plus a fee-paid stamp and a perforated passport number.
- **The telling detail:** a Brin Isles transit visa valid "for island
  ferries only", requiring the bearer to register with the harbour
  master within 24 hours of landing — the paperwork of an island state.

Typography, margins, rules and the guilloche-style border are kept
consistent across both pages, with centre-fold shading and page numbers.

## How to run

```bash
python3 main.py
```

Writes `/output/entry.png` (1024×1024 PNG). If `/output` is not
writable, it falls back to `./entry.png` next to `main.py`.
Output is deterministic: two runs produce byte-identical files.
Requires Python 3 with Pillow; no network access is used.

## License

MIT — see `LICENSE`.
