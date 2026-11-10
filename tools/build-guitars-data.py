#!/usr/bin/env python3
"""Nikotian — Κλασικές κιθάρες: product data + photographs.

Usage:  python3 tools/build-guitars-data.py <path to images/guitars>

Reads the two manufacturer folders («01. juan hernandez», «02. azahar»): one JPG + one TXT per model,
matched by file name (juan-hernandez-NN.jpg <-> juan-hernandez-NN.txt). Writes:
  data/guitars.json  · data/guitars.js (window.NIKOTIAN_GUITARS, works on file://)
  assets/photos/guitars/*.jpg

Photographs: copied byte-for-byte, except derived files (documented in images[].derived):
  - juan-hernandez-01 (v1.1): card photograph — the light studio background (234,234,232) and the floor shadow
    are replaced by the rust backdrop of the other Juan Hernández photographs (tools/guitar_backdrop.py).
    The instrument pixels are not touched (only JPEG re-encoding, q98).
  - juan-hernandez-01, hero (v1.0, unchanged): the near-white background lifted to white, so the photograph is
    multiplied onto Warm Beige in the hero. Kept in pageImages.
  - juan-hernandez-05: the photograph shows front and back. The card uses the front view only
    (left half, cut in the empty gap between the two views); the whole photograph is kept as images[1].
Nothing is invented: names, descriptions and specs come from the TXT only. Only MANUAL below is hand-set.
"""
import json, re, shutil, sys
from pathlib import Path
from PIL import Image, ImageChops

sys.path.insert(0, str(Path(__file__).resolve().parent))
from guitar_backdrop import replace_backdrop  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT_IMG = ROOT / 'assets/photos/guitars'
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else None

MAKERS = {
    'juan-hernandez': {'name': 'Juan Hernández', 'folder': '01. juan hernandez', 'short': 'jh'},
    'azahar': {'name': 'Azahar', 'folder': '02. azahar', 'short': 'az'},
}

# Backdrop of each photograph (uniform studio colour; mean of its pixels, σ ≈ 3). The card frame takes this
# colour, so the photograph is shown whole, uncropped and unaltered, with no visible edge.
BACKDROP_RUST = '#983302'   # Juan Hernández 02–05: mean of the backdrop pixels (152,51,2)
BACKDROP_NAVY = '#394761'   # Azahar 01–04: mean of the backdrop pixels (57,71,97)

MANUAL = {
    # file stem: view description (alt) + card treatment
    'juan-hernandez-01': {'view': 'μπροστινή όψη', 'backdrop': BACKDROP_RUST, 'rebackdrop': True, 'hero_whiten': True},
    'juan-hernandez-02': {'view': 'μπροστινή όψη', 'backdrop': BACKDROP_RUST},
    'juan-hernandez-03': {'view': 'μπροστινή όψη', 'backdrop': BACKDROP_RUST},
    'juan-hernandez-04': {'view': 'μπροστινή όψη', 'backdrop': BACKDROP_RUST},
    'juan-hernandez-05': {'view': 'μπροστινή όψη', 'backdrop': BACKDROP_RUST, 'front_crop': (0, 0, 201, 484)},
    'azahar-01': {'view': 'όψη υπό γωνία', 'backdrop': BACKDROP_NAVY},
    'azahar-02': {'view': 'όψη υπό γωνία', 'backdrop': BACKDROP_NAVY},
    'azahar-03': {'view': 'όψη υπό γωνία', 'backdrop': BACKDROP_NAVY},
    'azahar-04': {'view': 'όψη υπό γωνία', 'backdrop': BACKDROP_NAVY},
}

# Specs only where the TXT gives them as labelled fields (Juan Hernández Sonata). Labels in Greek,
# values exactly as written in the TXT.
SPEC_LABELS = {'Top': 'Καπάκι', 'Body': 'Πλάτη και πλευρές', 'Fingerboard': 'Ταστιέρα'}

NOTES = {
    'azahar-04': [
        'Η δεύτερη παράγραφος του TXT («Πλάτη και πλευρές από τριανταφυλλιά Αμαζονίου. Ταστιέρα παραδοσιακή ή '
        'αυξημένη.») είναι αυτούσια η περιγραφή του Juan Hernández Maestro και έρχεται σε αντίφαση με την '
        'πρώτη («ξύλο etimoe»). Πιθανό λάθος επικόλλησης: δεν μπαίνει στο description· κρατιέται στο raw '
        'και στο descriptionQuestioned μέχρι να επιβεβαιωθεί.'
    ],
    'juan-hernandez-05': [
        'Η φωτογραφία δείχνει μπροστινή και πίσω όψη. Η κάρτα δείχνει την μπροστινή όψη· ολόκληρη η φωτογραφία '
        'είναι στο images[1] (και στην ενότητα 03 της σελίδας).',
        'Το TXT γράφει «Estudio Clasica» (χωρίς τόνο). Διατηρείται όπως είναι.',
    ],
    'juan-hernandez-01': [
        'Το TXT γράφει «Body: Ovengkol»: στις κλασικές κιθάρες αυτό συνήθως αφορά πλάτη και πλευρές. '
        'Ετικέτα «Πλάτη και πλευρές» — προς επιβεβαίωση.'
    ],
}


def slugify(s):
    s = s.lower().replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')


def parse_txt(text):
    lines = [l.strip() for l in text.replace('\r', '').split('\n')]
    title = lines[0]
    m = re.match(r'^(Juan Hernandez|Azahar)\s*(?:\||-)?\s*(.+)$', title)
    if not m:
        raise SystemExit(f'Unexpected title line: {title!r}')
    model = m.group(2).strip()
    body = '\n'.join(lines[1:]).strip()
    paras = [re.sub(r'\s+', ' ', p).strip() for p in re.split(r'\n\s*\n', body) if p.strip()]
    specs_original, description = [], []
    i = 0
    while i < len(paras):
        p = paras[i]
        lab = re.match(r'^(%s):\s*(.+)$' % '|'.join(SPEC_LABELS), p)
        if lab:
            specs_original.append({'label': lab.group(1), 'value': lab.group(2)})
            i += 1
            continue
        if p.endswith(':') and p[:-1] in SPEC_LABELS and i + 1 < len(paras):
            specs_original.append({'label': p[:-1], 'value': paras[i + 1]})
            i += 2
            continue
        description.append(p)
        i += 1
    return title, model, description, specs_original


def whiten(src, dst):
    """Lift the near-white studio background to white; pixels far from it (the guitar) are unchanged."""
    im = Image.open(src).convert('RGB')
    bg = im.getpixel((3, im.height // 2))
    diff = ImageChops.difference(im, Image.new('RGB', im.size, bg)).convert('L')
    # 0..8 → background (white), 8..24 → soft ramp, >24 → original
    mask = diff.point(lambda v: 255 if v <= 8 else (0 if v >= 24 else int(255 * (24 - v) / 16)))
    out = Image.composite(Image.new('RGB', im.size, (255, 255, 255)), im, mask)
    out.save(dst, quality=95, subsampling=0, optimize=True)
    return list(bg)


def main():
    if not SRC or not SRC.is_dir():
        raise SystemExit(__doc__)
    OUT_IMG.mkdir(parents=True, exist_ok=True)
    records, order = [], 0
    for maker_slug, mk in MAKERS.items():
        folder = SRC / mk['folder']
        jpgs = sorted(folder.glob('*.jpg'))
        txts = sorted(folder.glob('*.txt'))
        if [p.stem for p in jpgs] != [p.stem for p in txts]:
            raise SystemExit(f'JPG/TXT mismatch in {folder}')
        for jpg in jpgs:
            stem = jpg.stem
            n = stem.rsplit('-', 1)[1]
            man = MANUAL[stem]
            raw = (folder / f'{stem}.txt').read_text(encoding='utf-8')
            title, model, description, specs_original = parse_txt(raw)
            questioned = []
            if stem == 'azahar-04':
                questioned = description[1:]
                description = description[:1]
            name = f"{mk['name']} {model}"
            slug = slugify(f"{maker_slug} {model}")
            w, h = Image.open(jpg).size
            order += 1

            # photographs
            full_name = f'{slug}.jpg'
            images = []
            page_images = []
            if man.get('rebackdrop'):
                card_name = f'{slug}-backdrop.jpg'
                rgb = tuple(int(man['backdrop'][i:i + 2], 16) for i in (1, 3, 5))
                st = replace_backdrop(jpg, OUT_IMG / card_name, rgb)
                primary = {'src': f'assets/photos/guitars/{card_name}', 'width': w, 'height': h,
                           'derived': (f"Φόντο στούντιο {tuple(st['oldBackdrop'])} και σκιά δαπέδου → {man['backdrop']}, "
                                       'όπως οι υπόλοιπες Juan Hernández· το όργανο αμετάβλητο (v1.1)')}
                if man.get('hero_whiten'):
                    bg = whiten(jpg, OUT_IMG / full_name)
                    page_images.append({'src': f'assets/photos/guitars/{full_name}', 'width': w, 'height': h,
                                        'role': 'hero', 'fit': 'contain', 'source': jpg.name,
                                        'alt': 'Κλασική κιθάρα Juan Hernández Sonata: καπάκι σε φυσικό ξύλο, ροζέτα γύρω από το στόμα και σκούρα ταστιέρα',
                                        'derived': f'Φόντο {tuple(bg)} → λευκό, για multiply σε Warm Beige (hero)· το όργανο αμετάβλητο'})
            elif man.get('front_crop'):
                shutil.copyfile(jpg, OUT_IMG / full_name)
                box = man['front_crop']
                front = f'{slug}-front.jpg'
                Image.open(jpg).convert('RGB').crop(box).save(OUT_IMG / front, quality=95, subsampling=0, optimize=True)
                primary = {'src': f'assets/photos/guitars/{front}', 'width': box[2] - box[0], 'height': box[3] - box[1],
                           'crop': list(box), 'derived': 'Μπροστινή όψη από τη φωτογραφία μπροστινής και πίσω όψης'}
            else:
                shutil.copyfile(jpg, OUT_IMG / full_name)
                primary = {'src': f'assets/photos/guitars/{full_name}', 'width': w, 'height': h}
            primary.update({
                'alt': f"{name}, κλασική κιθάρα, {man['view']}",
                'role': 'primary',
                'fit': 'contain',
                'backdrop': man['backdrop'],
                'source': jpg.name,
            })
            images.append(primary)
            if man.get('front_crop'):
                images.append({'src': f'assets/photos/guitars/{full_name}', 'width': w, 'height': h,
                               'alt': f'{name}, κλασική κιθάρα, μπροστινή και πίσω όψη', 'role': 'gallery',
                               'fit': 'contain', 'backdrop': man['backdrop'], 'source': jpg.name})

            specs = [{'label': SPEC_LABELS[s['label']], 'value': s['value'], 'source': f'TXT («{s["label"]}»)', 'show': True}
                     for s in specs_original]
            records.append({
                'id': f"guitar-{mk['short']}-{n}",
                'slug': slug,
                'url': f'/kitheres/{slug}/',
                'detailPage': f'guitar.html?model={slug}',   # Guitar Product Details v1.0
                'instrument': 'guitar',
                'category': 'guitar',
                'categoryLabel': 'Κλασική κιθάρα',
                'categoryUrl': '/kitheres/',
                'condition': None,
                'manufacturer': mk['name'],
                'manufacturerSlug': maker_slug,
                'model': model,
                'name': name,
                'originalName': title,
                'type': None,
                'typeLabel': None,
                'images': images,
                'description': description,
                'descriptionQuestioned': questioned,
                'specs': specs,
                'specsOriginal': specs_original,
                'pdf': None,
                **({'pageImages': page_images} if page_images else {}),
                'source': {'txt': f'{stem}.txt', 'image': jpg.name, 'folder': mk['folder']},
                'notes': NOTES.get(stem, []),
                'raw': raw.replace('\r', ''),
                'order': order,
            })

    ids = [r['id'] for r in records]; slugs = [r['slug'] for r in records]
    assert len(set(ids)) == len(ids) and len(set(slugs)) == len(slugs), 'duplicate id/slug'
    js = json.dumps(records, ensure_ascii=False, indent=2)
    (ROOT / 'data/guitars.json').write_text(js + '\n', encoding='utf-8')
    (ROOT / 'data/guitars.js').write_text(
        '/* Nikotian — Κλασικές κιθάρες: product data.\n'
        '   Generated by tools/build-guitars-data.py from images/guitars (one JPG + one TXT per model) —\n'
        '   do not edit by hand; change MANUAL / NOTES and rebuild. Same records as data/guitars.json. */\n'
        f'window.NIKOTIAN_GUITARS = {js};\n', encoding='utf-8')
    for r in records:
        print(r['order'], r['id'], r['slug'], '|', r['name'], '|', r['source']['txt'], '↔', r['source']['image'])


if __name__ == '__main__':
    main()
