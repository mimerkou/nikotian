#!/usr/bin/env python3
"""Nikotian — shared stylesheet bundle (performance v2, 19/11/2026).

Sources stay as they are and are the files to edit: css/fonts.css, css/tokens.css, css/style.css.
This script joins them, in that order, into css/base.min.css (comments and extra whitespace removed),
which is the one render-blocking shared stylesheet every page links. Page stylesheets (about.css, …)
are unchanged. Run after every change to the three sources:   python3 tools/build-css.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ['css/fonts.css', 'css/tokens.css', 'css/style.css']

def minify(css):
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    css = re.sub(r'\s+', ' ', css)
    css = re.sub(r'\s*([{};,>])\s*', r'\1', css)      # never touches + - in calc()
    css = css.replace(';}', '}')
    return css.strip()

if __name__ == '__main__':
    out = '/* Nikotian — built by tools/build-css.py from fonts.css + tokens.css + style.css. Do not edit. */\n'
    out += '\n'.join(minify((ROOT / s).read_text(encoding='utf-8')) for s in SOURCES) + '\n'
    (ROOT / 'css/base.min.css').write_text(out, encoding='utf-8')
    print('css/base.min.css', len(out.encode()), 'bytes')
