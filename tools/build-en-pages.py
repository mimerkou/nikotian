#!/usr/bin/env python3
"""Nikotian — English pages (/en/) from the Greek pages (prototype).

    python3 -I tools/build-en-pages.py .

For every Greek page at the root:
  · Greek page: EN link in the language switch (→ en/<page>), hreflang alternates in <head>.
  · en/<page>: same markup, text and labels from data/i18n/en-pages.json (Greek → English, one entry per
    distinct text node / alt / aria-label / meta content), lang="en", paths to the shared files one level up
    (../css, ../js, ../assets, ../data), Open Graph for /en/, and js/i18n.js for the scripts (catalogue + UI).
Links between pages stay relative, so /en/ pages link to /en/ pages. Any Greek left in an English page is
reported (comments and scripts excluded). Re-running is safe.
WordPress: the same structure maps to Polylang / WPML (one translation per page, /en/ prefix).
"""
import html, json, re, sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
BASE = 'https://nikotian.netlify.app/'
MAP = json.loads((ROOT / 'data/i18n/en-pages.json').read_text(encoding='utf-8'))
GR = re.compile('[Ͱ-Ͽἀ-῿]')
TEXT_ATTRS = ('alt', 'aria-label', 'title', 'content', 'placeholder', 'data-pending', 'data-noun', 'aria-roledescription', 'label')
PATH_ATTRS = ('href', 'src', 'srcset', 'poster', 'data-src')
TOKEN = re.compile(r'(<!--.*?-->|<script\b.*?</script>|<style\b.*?</style>|<[^>]+>)', re.S)
missing = {}


def tr(text, page):
    key = ' '.join(html.unescape(text).split())
    if not key or not GR.search(key):
        return None
    if key in MAP:
        return MAP[key]
    missing.setdefault(key, set()).add(page)
    return None


def en_tag(tag, page):
    def attr(m):
        name, val = m.group(1), m.group(2)
        if name in TEXT_ATTRS:
            t = tr(val, page)
            if t is not None:
                return f'{name}="{html.escape(t, quote=True)}"'
        if name in PATH_ATTRS and re.match(r'(css|js|assets|data)/', val):
            return f'{name}="../{val}"'
        return m.group(0)
    return re.sub(r'\b([\w:-]+)="([^"]*)"', attr, tag)


def to_english(src, page):
    out = []
    for i, part in enumerate(TOKEN.split(src)):
        if i % 2 == 1:      # comment / script / style / tag
            if part.startswith('<!--'):
                out.append(part)
            elif part.startswith('<script'):
                out.append(re.sub(r'src="((?:js|data)/[^"]*)"', r'src="../\1"', part))
            elif part.startswith('<style'):
                out.append(part)
            else:
                out.append(en_tag(part, page))
        else:               # text
            t = tr(part, page)
            if t is None:
                out.append(part)
            else:
                lead = part[:len(part) - len(part.lstrip())]
                trail = part[len(part.rstrip()):]
                out.append(lead + html.escape(t, quote=False) + trail)
    return ''.join(out)


def page_url(page, en):
    p = '' if page == 'index.html' else page
    return BASE + ('en/' if en else '') + p


def alternates(page):
    return ('  <!-- Language versions (hreflang) -->\n'
            f'  <link rel="alternate" hreflang="el" href="{page_url(page, False)}">\n'
            f'  <link rel="alternate" hreflang="en" href="{page_url(page, True)}">\n'
            f'  <link rel="alternate" hreflang="x-default" href="{page_url(page, False)}">\n')


LANG_NAV = re.compile(r'(<nav class="lang" aria-label="[^"]*">)(.*?)(</nav>)', re.S)


def greek(page, src):
    if 'hreflang="x-default"' not in src:
        src = src.replace('  <meta name="twitter:card"', alternates(page) + '  <meta name="twitter:card"', 1)
    def nav(m):
        el = re.search(r'<a class="lang__item"[^>]*>EL</a>', m.group(2)).group(0)
        en = f'<a class="lang__item" href="en/{page}" data-lang-switch="en/{page}" lang="en" hreflang="en">EN</a>'
        return f'{m.group(1)}\n          {el}\n          <span class="lang__sep" aria-hidden="true">|</span>\n          {en}\n        {m.group(3)}'
    return LANG_NAV.sub(nav, src, count=1)


def english(page, src):
    s = to_english(src, page)
    s = s.replace('<html lang="el" class="no-js">', '<html lang="en" class="no-js" data-root="../">', 1)
    s = s.replace('<meta property="og:locale" content="el_GR">', '<meta property="og:locale" content="en_GB">\n  <meta property="og:locale:alternate" content="el_GR">', 1)
    s = re.sub(r'(<meta property="og:url" content=")[^"]*(">)', lambda m: m.group(1) + page_url(page, True) + m.group(2), s, count=1)
    s = s.replace(f'content="{BASE}assets/og/og-image.jpg"', f'content="{BASE}assets/og/og-image-en.jpg"')
    s = s.replace('<script src="../js/main.js" defer></script>', '<script src="../js/main.js" defer></script>\n  <script src="../js/i18n.js" defer></script>', 1)
    def nav(m):
        self_attr = ' data-lang-self' if 'data-lang-self' in m.group(2) else ''
        here = '#top' if page == 'index.html' else page
        el = f'<a class="lang__item" href="../{page}" data-lang-switch="../{page}" lang="el" hreflang="el">EL</a>'
        en = f'<a class="lang__item" href="{here}"{self_attr} lang="en" hreflang="en" aria-current="page">EN</a>'
        return f'{m.group(1)}\n          {el}\n          <span class="lang__sep" aria-hidden="true">|</span>\n          {en}\n        {m.group(3)}'
    s = LANG_NAV.sub(nav, s, count=1)
    return s


ABS = re.compile(r'\b(href|src|data-lang-switch)="(?!https?:|mailto:|tel:|#|/|data:)([^"]*)"')


def not_found(src, en):
    """404.html / en/404.html: Netlify serves them at any missing URL, at any depth, so every path is made
    root-absolute. No hreflang (noindex page); the language switch goes to the other language's home page."""
    src = re.sub(r'  <!-- Language versions \(hreflang\) -->\n(  <link rel="alternate"[^\n]*\n)+', '', src)
    def fix(m):
        val = m.group(2)
        if val.startswith('../'):
            val = val[3:]
        elif en and not val.startswith(('css/', 'js/', 'assets/', 'data/')):
            val = 'en/' + val
        return f'{m.group(1)}="/{val}"'
    src = ABS.sub(fix, src)
    src = src.replace('data-root="../"', 'data-root="/"')
    def nav(m):
        el = '<a class="lang__item" href="/" lang="el" hreflang="el"' + (' aria-current="page"' if not en else '') + '>EL</a>'
        en_ = '<a class="lang__item" href="/en/" lang="en" hreflang="en"' + (' aria-current="page"' if en else '') + '>EN</a>'
        return f'{m.group(1)}\n          {el}\n          <span class="lang__sep" aria-hidden="true">|</span>\n          {en_}\n        {m.group(3)}'
    return LANG_NAV.sub(nav, src, count=1)


def main():
    (ROOT / 'en').mkdir(exist_ok=True)
    pages = sorted(p.name for p in ROOT.glob('*.html'))
    for page in pages:
        path = ROOT / page
        raw = path.read_text(encoding='utf-8')
        if page == '404.html':   # start again from relative paths; not_found() makes them absolute
            raw = re.sub(r'\b(href|src|data-lang-switch)="/(?!/)([^"]+)"', r'\1="\2"', raw)
        src = greek(page, raw)
        en_src = english(page, src)
        if page == '404.html':
            src, en_src = not_found(src, False), not_found(en_src, True)
        path.write_text(src, encoding='utf-8')
        (ROOT / 'en' / page).write_text(en_src, encoding='utf-8')
    leftovers = {}
    for page in pages:
        body = (ROOT / 'en' / page).read_text(encoding='utf-8')
        visible = TOKEN.sub(lambda m: '' if m.group(0).startswith(('<!--', '<script', '<style')) else m.group(0), body)
        hits = sorted({w for w in GR.findall(visible)})
        if hits:
            leftovers[page] = len(hits)
    print('pages', len(pages), '| untranslated strings:', len(missing), '| pages with Greek left:', leftovers)
    for k, v in missing.items():
        print('  MISSING:', k[:90], sorted(v))


if __name__ == '__main__':
    main()
