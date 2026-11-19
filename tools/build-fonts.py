#!/usr/bin/env python3
"""Nikotian — build the WOFF2 font subsets in assets/fonts/ and css/fonts.css (performance v2, 19/11/2026).

Sources: tools/font-sources/*.woff (the earlier per-script WOFF subsets of Literata / Commissioner, OFL).
Output: one WOFF2 per family × style × range, with non-overlapping unicode-ranges, so that a Greek page
never downloads a Latin file only for spaces, digits or punctuation.

Needs fontTools + Brotli. Where `pip install brotli` is not possible, a tiny shim module named `brotli`
that calls Node's zlib.brotliCompressSync (MODE_FONT, quality 11) works the same.
Usage: python3 tools/build-fonts.py   (then check css/fonts.css)
"""
import os, sys
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools import subset

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR, OUT_DIR = ROOT / 'tools/font-sources', ROOT / 'assets/fonts'
R = {
    'common': list(range(0x20, 0x41)) + list(range(0x5B, 0x61)) + list(range(0x7B, 0x7F)) + list(range(0xA0, 0xC0)) + [0xD7, 0xF7]
              + list(range(0x2000, 0x2070)) + [0x20AC, 0x2122, 0x2190, 0x2191, 0x2192, 0x2193, 0x2212, 0x2215, 0xFEFF, 0xFFFD],
    'greek': list(range(0x370, 0x400)),
    'latin': list(range(0x41, 0x5B)) + list(range(0x61, 0x7B)) + [c for c in range(0xC0, 0x100) if c not in (0xD7, 0xF7)]
             + [0x131, 0x152, 0x153, 0x2BB, 0x2BC, 0x2C6, 0x2DA, 0x2DC],
    'latin-ext': list(range(0x100, 0x131)) + list(range(0x132, 0x152)) + list(range(0x154, 0x250)) + list(range(0x1E00, 0x1F00)) + list(range(0x2C60, 0x2C80)),
    'greek-ext': list(range(0x1F00, 0x2000)),
}
SRC = {'common': 'latin', 'latin': 'latin', 'greek': 'greek', 'greek-ext': 'greek', 'latin-ext': 'latin-ext'}
META = {'literata': ('Literata', 'normal', '300 600'), 'literata-italic': ('Literata', 'italic', '300 500'), 'commissioner': ('Commissioner', 'normal', '300 700')}
FEAT = ['ccmp', 'locl', 'liga', 'kern', 'case', 'lnum', 'tnum', 'pnum', 'onum', 'mark', 'mkmk', 'calt', 'rlig']

def ranges(cps):
    cps = sorted(cps); out = []; s = p = cps[0]
    for c in cps[1:]:
        if c == p + 1: p = c; continue
        out.append((s, p)); s = p = c
    out.append((s, p))
    return ', '.join(f'U+{a:04X}' if a == b else f'U+{a:04X}-{b:04X}' for a, b in out)

# Literata italic: the lower-case Roman numerals of the homepage services (i, ii, iii, iv, v…) live in the
# italic «common» file, so a Greek page does not download the whole Latin italic (~50 KB) for them.
ROMAN = [ord(c) for c in 'ivxlcdm']

faces = []
for fam in META:
    for part, cps in R.items():
        if fam == 'literata-italic' and part == 'common': cps = cps + ROMAN
        if fam == 'literata-italic' and part == 'latin': cps = [c for c in cps if c not in ROMAN]
        f = TTFont(SRC_DIR / f'{fam}-{SRC[part]}.woff'); cm = f.getBestCmap()
        keep = [c for c in cps if c in cm]
        if not keep: continue
        o = subset.Options(); o.flavor = 'woff2'; o.layout_features = FEAT; o.name_IDs = ['*']; o.name_languages = ['*']
        o.notdef_outline = True; o.glyph_names = False
        s = subset.Subsetter(o); s.populate(unicodes=keep); s.subset(f); f.flavor = 'woff2'
        f.save(OUT_DIR / f'{fam}-{part}.woff2')
        faces.append((fam, part, ranges(keep)))
        print(f'{fam}-{part}.woff2', os.path.getsize(OUT_DIR / f'{fam}-{part}.woff2'))
css = (ROOT / 'css/fonts.css').read_text(encoding='utf-8')
head = css[:css.index('@font-face')]
blocks = ''.join(f'''@font-face {{
  font-family: "{META[fam][0]}";
  font-style: {META[fam][1]};
  font-weight: {META[fam][2]};
  font-display: swap;
  src: url("../assets/fonts/{fam}-{part}.woff2") format("woff2");
  unicode-range: {rng};
}}
''' for fam, part, rng in faces)
(ROOT / 'css/fonts.css').write_text(head + blocks, encoding='utf-8')
print('faces:', len(faces), '→ css/fonts.css')
