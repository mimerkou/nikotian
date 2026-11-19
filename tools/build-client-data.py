#!/usr/bin/env python3
"""Nikotian — lean browser copies of the catalogue (performance v2, 19/11/2026).

data/*.json stay complete: they are the record (sources, raw TXT, original manufacturer tables, notes).
The browser only needs what the pages show, so data/*.js keep their header comment and global name but
drop the internal fields below. Run after any data build:   python3 tools/build-client-data.py
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INTERNAL = {'raw', 'specsOriginal', 'notes', 'typeEvidence', 'galleryOriginal', 'editNote', 'bodySource', 'source'}
FILES = ['new-pianos', 'used-pianos', 'guitars', 'electric-pianos']

def strip(o):
    if isinstance(o, dict):
        return {k: strip(v) for k, v in o.items() if k not in INTERNAL}
    if isinstance(o, list):
        return [strip(v) for v in o]
    return o

for name in FILES:
    js = ROOT / f'data/{name}.js'
    src = js.read_text(encoding='utf-8')
    m = re.match(r'(/\*.*?\*/\s*)(window\.[A-Z_]+)\s*=', src, re.S)
    head, glob = m.group(1), m.group(2)
    if 'lean copy' not in head:
        head = head.rstrip()[:-2].rstrip() + '\n   Browser copy (lean copy, tools/build-client-data.py): internal fields — ' + ', '.join(sorted(INTERNAL)) + ' — are only in the .json. */\n'
    data = strip(json.loads((ROOT / f'data/{name}.json').read_text(encoding='utf-8')))
    out = f'{head}{glob} = {json.dumps(data, ensure_ascii=False, separators=(",", ":"))};\n'
    before = len(src.encode()); js.write_text(out, encoding='utf-8')
    print(name, before, '→', len(out.encode()))
