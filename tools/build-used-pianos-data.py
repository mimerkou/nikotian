#!/usr/bin/env python3
"""Nikotian — build the «Μεταχειρισμένα πιάνα» data from the supplied used-pianos.zip.

Usage:  python3 -I tools/build-used-pianos-data.py <extracted-zip-dir> <project-root>

Reads used-piano_NN.txt / .jpg. Every TXT holds one line: the name of the instrument as it
appears on the current nikotian.gr. The name is kept verbatim (originalName) and split into
manufacturer + model. Writes:
  data/used-pianos.js     window.NIKOTIAN_USED_PIANOS = [...]   (used by the page; works on file://)
  data/used-pianos.json   the same records                       (future Product Detail Template / WP import)
  assets/photos/pianos/used/used-piano-NN.jpg   byte-for-byte copies of the originals (no re-encoding,
                                                no background removal, no retouching)

Decided by hand (MANUAL): the real manufacturer name, the model (TXT minus manufacturer), the
piano type with its evidence, and the photo framing in the card (fit + object-position).
Nothing else is added: the ZIP has no descriptions, specifications, prices or availability.
"""
import hashlib, json, re, shutil, sys, unicodedata
from pathlib import Path
from PIL import Image

SRC = Path(sys.argv[1])
ROOT = Path(sys.argv[2])

# Manufacturer display names (proper case; spelling as on the instrument where it is legible).
MAKERS = {
    'HOFMANN & CERNY': 'Hofmann & Černý',   # fallboard decal in used-piano_01.jpg reads «HOFMANN & ČERNÝ»
    'IBACH': 'Ibach', 'SCHIMMEL': 'Schimmel', 'KAPS': 'Kaps', 'KRAUSS': 'Krauss',
    'YAMAHA': 'Yamaha', 'YOUNG CHANG': 'Young Chang', 'PLEYEL': 'Pleyel', 'RAMEAU': 'Rameau',
    'SAUTER': 'Sauter', 'KAWAI': 'Kawai', 'ATLAS': 'Atlas', 'PETROF': 'Petrof', 'WEINBACH': 'Weinbach',
}

U = 'upright'; G = 'grand'
PH_U = 'Φωτογραφία: όρθιο σώμα, πλήκτρα μπροστά από κατακόρυφο ηχείο'
PH_G = 'Φωτογραφία: οριζόντιο σώμα με ουρά'
# n: (type, evidence, fit, object-position)  — fit «cover» crops to the 3:2 card frame at the given
# position; «contain» shows the whole photograph inside the frame (tall photos, where a 3:2 crop
# would cut the keyboard, the painted panel or the lid).
MANUAL = {
    1:  (U, PH_U + ' (κοντινό, υπό γωνία)', 'cover', '50% 50%'),
    2:  (U, PH_U, 'cover', '50% 50%'),
    3:  (G, PH_G + ', κλειστό καπάκι, τρία πόδια, λύρα πεντάλ', 'cover', '50% 50%'),
    4:  (G, PH_G + ', ανοιχτό αναλόγιο, τρία πόδια', 'cover', '50% 70%'),
    5:  (U, PH_U, 'cover', '50% 30%'),
    6:  (U, PH_U + ' (κοντινό, υπό γωνία)', 'cover', '60% 50%'),
    7:  (U, PH_U, 'cover', '41% 50%'),
    8:  (U, PH_U, 'cover', '57% 50%'),
    9:  (U, PH_U, 'cover', '47% 50%'),
    10: (U, PH_U, 'cover', '38% 50%'),
    11: (U, PH_U + ' (το ανοιχτό καπάκι πίσω του ανήκει σε άλλο πιάνο της έκθεσης)', 'cover', '59% 50%'),
    12: (U, PH_U, 'cover', '50% 50%'),
    13: (U, PH_U, 'cover', '38% 50%'),
    14: (U, PH_U + ' (κοντινό, υπό γωνία)', 'cover', '60% 50%'),
    15: (U, PH_U, 'cover', '52% 50%'),
    16: (U, PH_U, 'cover', '56% 50%'),
    17: (U, PH_U, 'cover', '52% 50%'),
    18: (U, PH_U + ' (κοντινό)', 'cover', '50% 50%'),
    19: (U, PH_U, 'cover', '52% 50%'),
    20: (U, PH_U, 'cover', '50% 50%'),
    21: (U, PH_U + ', με σκαμπό', 'contain', '50% 50%'),
    22: (U, PH_U, 'cover', '50% 50%'),
    23: (U, PH_U, 'cover', '55% 50%'),
    24: (G, PH_G + ', ανοιχτό καπάκι', 'contain', '50% 50%'),
    25: (U, PH_U + ', ζωγραφισμένο πάνελ', 'contain', '50% 50%'),
    26: (G, PH_G + ', ανοιχτό καπάκι', 'contain', '50% 50%'),
    27: (U, PH_U + ', ζωγραφισμένο πάνελ', 'contain', '50% 50%'),
}
TYPE_LABEL = {U: 'Όρθιο πιάνο', G: 'Πιάνο με ουρά'}
NOTES = {
    1: ['Το TXT γράφει «HOFMANN & CERNY»· στο καπάκι των πλήκτρων διαβάζεται «HOFMANN & ČERNÝ». Εμφανίζεται με τα διακριτικά· προς επιβεβαίωση.'],
}


def slugify(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def split_name(raw):
    up = raw.upper()
    for key in sorted(MAKERS, key=len, reverse=True):
        if up == key or up.startswith(key + ' '):
            return MAKERS[key], raw[len(key):].strip() or None
    raise SystemExit(f'Unknown manufacturer in «{raw}»')


def natural(s):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', s or '')]


def main():
    txts = sorted(SRC.glob('used-piano_*.txt'))
    jpgs = sorted(SRC.glob('used-piano_*.jpg'))
    assert [t.stem for t in txts] == [j.stem for j in jpgs], 'TXT and JPG files do not pair 1:1'
    hashes = [hashlib.md5(j.read_bytes()).hexdigest() for j in jpgs]
    assert len(set(hashes)) == len(hashes), 'duplicate photograph'

    out_img = ROOT / 'assets/photos/pianos/used'
    out_img.mkdir(parents=True, exist_ok=True)
    recs = []
    for t, j in zip(txts, jpgs):
        n = int(t.stem.split('_')[1])
        raw = t.read_text(encoding='utf-8-sig').strip()
        maker, model = split_name(raw)
        typ, evidence, fit, pos = MANUAL[n]
        dest = out_img / f'used-piano-{n:02d}.jpg'
        shutil.copyfile(j, dest)                       # unchanged bytes
        w, h = Image.open(dest).size
        name = f'{maker} {model}' if model else maker
        slug = f'{slugify(name)}-{n:02d}'              # the number keeps same-name instruments apart
        recs.append({
            'id': f'used-{n:02d}',
            'slug': slug,
            'url': f'/pianos/used/{slug}/',
            'detailPage': None,
            'condition': 'used',
            'manufacturer': maker,
            'manufacturerSlug': slugify(maker),
            'model': model,
            'name': name,
            'originalName': raw,
            'type': typ,
            'typeLabel': TYPE_LABEL[typ],
            'typeEvidence': evidence,
            'images': [{
                'src': f'assets/photos/pianos/used/used-piano-{n:02d}.jpg',
                'width': w, 'height': h,
                'fit': fit, 'position': pos,
                'alt': f'{name}, {TYPE_LABEL[typ].lower()}, στην έκθεση Nikotian',
            }],
            'source': {'txt': t.name, 'image': j.name, 'zip': 'used-pianos.zip'},
            # Optional, for the future Product Detail Template. Empty on purpose: the ZIP has no such data.
            'description': [], 'specs': {}, 'finish': None, 'features': [],
            'notes': NOTES.get(n, []),
        })

    # Same-name instruments stay separate records; they get a group key and a position in it.
    groups = {}
    for r in recs:
        groups.setdefault(slugify(r['name']), []).append(r)
    for key, members in groups.items():
        for i, r in enumerate(sorted(members, key=lambda r: r['id']), 1):
            r['sameNameGroup'] = key if len(members) > 1 else None
            r['sameNameIndex'] = [i, len(members)] if len(members) > 1 else None

    # Display order: manufacturers alphabetically (no ranking implied), then model, then file number.
    recs.sort(key=lambda r: (r['manufacturer'].lower(), natural(r['model']), r['id']))
    for i, r in enumerate(recs, 1):
        r['order'] = i

    (ROOT / 'data').mkdir(exist_ok=True)
    js = json.dumps(recs, ensure_ascii=False, indent=2)
    (ROOT / 'data/used-pianos.json').write_text(js + '\n', encoding='utf-8')
    (ROOT / 'data/used-pianos.js').write_text(
        '/* Nikotian — Μεταχειρισμένα πιάνα: product data.\n'
        '   Generated by tools/build-used-pianos-data.py from used-pianos.zip — do not edit by hand;\n'
        '   change the MANUAL table and rebuild. Same records as data/used-pianos.json. */\n'
        f'window.NIKOTIAN_USED_PIANOS = {js};\n', encoding='utf-8')

    from collections import Counter
    print(len(recs), 'records;', Counter(r['type'] for r in recs))
    print(Counter(r['manufacturer'] for r in recs))
    for r in recs:
        print(r['order'], r['id'], r['originalName'], '→', r['manufacturer'], '|', r['model'], '|', r['type'], r['images'][0]['fit'], r['sameNameIndex'])


main()
