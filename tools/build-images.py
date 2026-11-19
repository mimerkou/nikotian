#!/usr/bin/env python3
"""Nikotian — responsive images (performance v2, 19/11/2026).

1. For every JPEG in assets/photos/ writes WebP variants next to it:  name-480.webp, name-800.webp, …
   Widths: every step of STEPS smaller than the photograph, plus the photograph's own width (max 2400).
   The same rule lives in js/main.js (NIKOTIAN_PICTURE), which builds <picture> for the catalogue
   images rendered by JavaScript — keep the two in step.
2. In the Greek HTML pages (the English ones are built from them by tools/build-en-pages.py) every
   <img src="assets/photos/…jpg"> outside a <dialog> is wrapped in
       <picture><source type="image/webp" srcset="…" sizes="…"><img …></picture>
   The JPEG stays as the fallback. `sizes` comes from data/img-sizes.json: the width each image actually
   occupies at 390 / 900 / 1440 / 1920 px (measured in the browser; for object-fit: cover, the width the
   photograph needs to fill its frame). Re-running the script is safe (it rewrites existing <picture>s).
   CSS: picture { display: contents } (style.css), so layouts and selectors see the <img> as before.
Usage: python3 tools/build-images.py [--html-only]
"""
import json, re, sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
STEPS = (480, 800, 1200, 1600, 2000)
MAXW = 2400
QUALITY = 78
PAGES = ['index.html', 'about.html', 'contact.html', 'services.html', 'new-pianos.html', 'used-pianos.html',
         'electric-pianos.html', 'guitars.html', 'privacy.html', '404.html', 'piano.html', 'guitar.html']

def widths(w):
    return [s for s in STEPS if s < w] + [min(w, MAXW)]

def variant(src, w):
    return re.sub(r'\.(jpe?g|png)$', f'-{w}.webp', src, flags=re.I)

def build_variants():
    n = 0
    for p in sorted((ROOT / 'assets/photos').rglob('*')):
        if p.suffix.lower() not in ('.jpg', '.jpeg', '.png'):
            continue
        im = Image.open(p); im.load()
        if im.mode not in ('RGB', 'RGBA'):
            im = im.convert('RGB')
        for w in widths(im.width):
            out = Path(variant(str(p), w))
            if out.exists() and out.stat().st_mtime >= p.stat().st_mtime:
                continue
            h = round(im.height * w / im.width)
            (im if w == im.width else im.resize((w, h), Image.LANCZOS)).save(out, 'WEBP', quality=QUALITY, method=6)
            n += 1
    print('webp variants written:', n)

def vw(px, vp):
    return f'{max(1, round(px / vp * 100))}vw'

def sizes_attr(m):
    """m: {'390': px, '900': px, '1440': px, '1920': px} (0 when hidden at that width)."""
    a, b, c, d = (int(m.get(k) or 0) for k in ('390', '900', '1440', '1920'))
    parts = []
    if a: parts.append(f'(max-width: 47.9375rem) {vw(a, 390)}')
    if b: parts.append(f'(max-width: 67.5rem) {vw(b, 900)}')
    big = max(c, d)
    if not big:
        return ', '.join(parts + ['100vw'])
    parts.append(f'{big}px' if d <= c * 1.06 else vw(c, 1440))
    return ', '.join(parts)

PIC = re.compile(r'<picture>\s*<source type="image/webp"[^>]*>\s*(<img\b[^>]*>)\s*</picture>', re.S)
IMG = re.compile(r'<img\b[^>]*\bsrc="(assets/photos/[^"]+\.(?:jpe?g|png))"[^>]*>', re.I)

def rewrite_html():
    sizes = json.loads((ROOT / 'data/img-sizes.json').read_text(encoding='utf-8'))
    for page in PAGES:
        f = ROOT / page
        s = f.read_text(encoding='utf-8')
        s = PIC.sub(lambda m: m.group(1), s)          # idempotent: unwrap, then wrap again
        dialogs = [(m.start(), m.end()) for m in re.finditer(r'<dialog\b.*?</dialog>', s, re.S)]
        def wrap(m):
            if any(a <= m.start() < b for a, b in dialogs) or 'data-no-picture' in m.group(0):
                return m.group(0)
            src = m.group(1)
            w = Image.open(ROOT / src).width
            srcset = ', '.join(f'{variant(src, x)} {x}w' for x in widths(w))
            sz = sizes.get(f'{page}|{src}') or '100vw'
            return f'<picture><source type="image/webp" srcset="{srcset}" sizes="{sz}">{m.group(0)}</picture>'
        s2 = IMG.sub(wrap, s)
        # the hero preload must ask for exactly the file the <picture> will choose (else it is fetched twice)
        def preload(m):
            src = m.group(1) or m.group(2)
            pm = re.search(r'<picture><source type="image/webp" srcset="([^"]+)" sizes="([^"]+)"><img\b[^>]*\bsrc="' + re.escape(src) + '"', s2)
            if not pm:
                return m.group(0)
            return (f'<link rel="preload" as="image" type="image/webp" imagesrcset="{pm.group(1)}" '
                    f'imagesizes="{pm.group(2)}" fetchpriority="high" data-for="{src}">')
        s2 = re.sub(r'<link rel="preload" as="image" (?:href="(assets/photos/[^"]+)"|[^>]*data-for="(assets/photos/[^"]+)")[^>]*>', preload, s2)
        if s2 != s or PIC.search(s2):
            f.write_text(s2, encoding='utf-8')
        print(page, len(PIC.findall(s2)), 'pictures')

if __name__ == '__main__':
    if '--measure' in sys.argv:
        m = json.load(open(sys.argv[sys.argv.index('--measure') + 1]))
        out = {}
        for k, v in m.items():
            page, src, _cls = k.split('|')
            if v.get('dialog'): continue
            key = f'{page}|{src}'
            prev = out.get(key)
            out[key] = sizes_attr(v) if not prev else prev
        (ROOT / 'data/img-sizes.json').write_text(json.dumps(dict(sorted(out.items())), ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
        print('sizes:', len(out))
        sys.exit()
    if '--html-only' not in sys.argv:
        build_variants()
    rewrite_html()
