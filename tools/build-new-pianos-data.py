#!/usr/bin/env python3
"""Nikotian — build the «Καινούργια πιάνα» data from the supplied new-pianos.zip.

Usage:  python3 -I tools/build-new-pianos-data.py <extracted-zip-dir> <project-root>

Reads new-piano_NN.txt / .jpg / *.pdf, keeps every TXT verbatim (raw) and parses it into
description / additional info / drawing / finishes / specs. Writes:
  data/new-pianos.js    window.NIKOTIAN_NEW_PIANOS = [...]   (used by the page; works on file://)
  data/new-pianos.json  the same records                      (for the future Product Detail Template / WP import)
  assets/photos/pianos/new/<slug>.jpg   white margins trimmed only (no scaling, nothing of the piano cut)
  assets/docs/pianos/new/<slug>.pdf     Grotrian brochures, unchanged

Only two things are decided by hand below (MANUAL): the piano type with its evidence, and the
display order. Nothing is invented: a type is set only when the TXT or the PDF states it.
"""
import json, re, shutil, sys, unicodedata
from pathlib import Path
from PIL import Image, ImageChops

SRC = Path(sys.argv[1])
ROOT = Path(sys.argv[2])

# --------------------------------------------------------------------------------------------
# MANUAL — type ('upright' | 'grand' | None) and the evidence for it.
# --------------------------------------------------------------------------------------------
MANUAL = {
    1:  ('grand',   'TXT: «Στυλ: Baby Grand», «πιάνων με ουρά Young Chang»'),
    2:  ('grand',   'TXT: όνομα «Salon Grand»'),
    3:  ('upright', 'TXT: όνομα «Professional Concert Upright»'),
    4:  ('upright', 'TXT: όνομα «Professional Upright», «επαγγελματικού όρθιου»'),
    5:  (None,      'Δεν αναφέρεται στο TXT· «Friedrich Grotrian» είναι όνομα σειράς, όχι μοντέλου. Η φωτογραφία δείχνει όρθιο — προς επιβεβαίωση.'),
    6:  ('upright', 'PDF: «…das beste Klavier der Welt» (Klavier = όρθιο), όνομα αρχείου kl_classic· διαστάσεις 124 × 148 × 57'),
    7:  ('upright', 'PDF: «You see an upright, you hear a grand piano», όνομα αρχείου kl_concertino'),
    8:  ('grand',   'PDF: όνομα αρχείου fl_chambre (Flügel), διαστάσεις 165 × 150 × 100'),
    9:  ('grand',   'PDF: «Measuring 192 cm in length», όνομα αρχείου fl_cabinet'),
    10: ('grand',   'PDF: «Ein Flügel…», «A grand…», όνομα αρχείου fl_charis'),
    11: ('grand',   'TXT: «συναυλιακό Grotrian πιάνο μήκους 225» (μήκος = πιάνο με ουρά)'),
    12: ('grand',   'TXT: «Ένα πιάνο με ουρά», PDF: «one of the best grand pianos»'),
    13: ('upright', 'TXT: «αυτού του χαμηλότερου όρθιου»'),
    14: ('upright', 'TXT: ίδιος τόνος με το Model 115 (όρθιο), «καμπίνας ενός υψηλότερου πιάνου»'),
    15: (None,      'Δεν αναφέρεται στο TXT. Η φωτογραφία δείχνει όρθιο — προς επιβεβαίωση.'),
    16: ('upright', 'TXT: «του πιο ψηλού όρθιου πιάνου της Rönisch»'),
    17: ('grand',   'TXT: «Grand πιάνο», «Στυλ: Classic Grand»'),
    18: ('upright', 'TXT: «Το όρθιο πιάνο P 118 P1»'),
    19: ('upright', 'TXT: «είναι ένα όρθιο πιάνο»'),
    20: ('upright', 'TXT: «Το P 131 E1 όρθιο πιάνο»'),
    21: ('upright', 'TXT: «Το P 135 K1 όρθιο πιάνο»'),
    22: ('grand',   'TXT: «πιάνο με ούρα», «Standard Grand Series»'),
    23: ('grand',   'TXT: «πιάνο με ουρά», «GRAND PIANO GROUND VIEW»'),
    24: ('grand',   'TXT: όνομα «Mistral Grand», «GRAND PIANO GROUND VIEW»'),
    25: ('grand',   'TXT: «ΣΤΥΛ: Professional Grand»'),
    26: ('grand',   'TXT: «πιάνο με ουρά», «ΣΤΥΛ: Professional Grand»'),
    27: ('upright', 'TXT: «ΣΤΥΛ: Professional Upright»'),
    28: ('upright', 'TXT: «ΣΤΥΛ: Professional Upright»'),
}

# Notes on ambiguities / inconsistencies found in the material (kept with the record, never shown on the page).
NOTES = {
    1:  ['Η πρώτη γραμμή δεν έχει «|»: «Young Chang Y-150».',
         'Το TXT αναφέρει «υπέροχη τιμή» / «χαμηλή τιμή»: εμπορική διατύπωση, δεν χρησιμοποιείται στη σελίδα.',
         'Γραφή ονόματος «Y-150» (με παύλα)· τα υπόλοιπα Young Chang γράφονται «Y 157» κ.λπ.'],
    2:  ['Ο τύπος προκύπτει μόνο από το όνομα («Salon Grand»).'],
    5:  ['«Friedrich Grotrian» είναι σειρά, όχι συγκεκριμένο μοντέλο· δεν δίνεται μέγεθος.', 'Τύπος μη τεκμηριωμένος.'],
    10: ['Τυπογραφικό λάθος στο TXT: «μι απηγή» (= μια πηγή). Διατηρείται αυτούσιο στο raw.'],
    11: ['Δεν υπάρχει PDF για το Concert 225 (υπάρχουν για 06, 07, 08, 09, 10, 12).'],
    15: ['Τύπος μη τεκμηριωμένος.'],
    17: ['Γραφή ονόματος «Y 157» στον τίτλο, «Y-157» στο κείμενο.'],
    18: ['Πίνακας προδιαγραφών στα αγγλικά (από τον κατασκευαστή), ενδιάμεσες λέξεις «nákres» (τσεχικά: σχέδιο).'],
    19: ['Τίτλος «P 125», πίνακας προδιαγραφών «P 125 G1»: να επιβεβαιωθεί η ακριβής έκδοση.'],
    20: ['Τίτλος «P 131 E1», πίνακας προδιαγραφών «P 131 M1»· διαστάσεις σχεδίου (602/1316) ≠ πίνακα (604/1314).'],
    21: ['Το περιγραφικό κείμενο είναι διπλοεπικολλημένο και αναφέρει και το «P 131 E1»· χρειάζεται επιμέλεια πριν από τη σελίδα προϊόντος.',
         'Ύψος σχεδίου 1341 mm ≠ πίνακα 1351 mm.'],
    22: ['Μοναδικό καινούργιο με τελείωμα «Μαόνι γυαλιστερό» στη φωτογραφία.'],
    23: ['Ύψος σχεδίου 1006 mm ≠ πίνακα 1025 mm.'],
    24: ['Ύψος σχεδίου 1014 mm ≠ πίνακα 1030 mm· μήκος 111,42″ ≠ 112″.'],
    25: ['Γραφή «Y 185» στον τίτλο, «Y-185» στο κείμενο.'],
    26: ['Γραφή «Y 175» στον τίτλο, «Y-175» στο κείμενο.'],
    28: ['Γραφή «Y 121» στον τίτλο, «Y-121» στο κείμενο.'],
}

# Display order: manufacturers alphabetically (no ranking implied); within a manufacturer
# uprights, then grands, each by size; unknown type last.
SIZE = {1: 150, 2: 191, 3: 132, 4: 124, 5: None, 6: 124, 7: 132, 8: 165, 9: 192, 10: 208, 11: 225, 12: 277,
        13: 115, 14: 118, 15: 123, 16: 132, 17: 157, 18: 118, 19: 125, 20: 131, 21: 135, 22: 172, 23: 210,
        24: 284, 25: 185, 26: 175, 27: 131, 28: 121}

FACT_LABEL = {'ΜΕΓΕΘΟΣ': 'Μέγεθος', 'ΣΤΥΛ': 'Στυλ', 'ΤΕΛΕΙΩΜΑ': 'Τελείωμα', 'ΜΟΝΤΕΛΟ': 'Μοντέλο'}
TYPE_LABEL = {'upright': 'Όρθιο πιάνο', 'grand': 'Πιάνο με ουρά', None: None}


def unaccent(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s) if not unicodedata.combining(c))


def slugify(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def dedupe_half(s):
    """'White, high polish 0001White, high polish 0001' -> 'White, high polish 0001'"""
    s = s.strip()
    n = len(s)
    if n % 2 == 0 and s[: n // 2] == s[n // 2:]:
        return s[: n // 2]
    return s


INFO_HEAD = re.compile(r'^Πρόσθετες πληροφορίες:?$')
CLASSIC = re.compile(r'^-?\s*Κλασικό πιάνο$')
DRAW_HEAD = {'Side view', 'GRAND PIANO GROUND VIEW', 'ground view', 'nákres'}
FINISH_HEAD = {'Finish', 'ΤΕΛΕΙΩΜΑ'}


def parse(n, text):
    lines = [l.rstrip() for l in text.replace('\r\n', '\n').replace('\r', '\n').split('\n')]
    title = lines[0].strip()
    if ' | ' in title:
        manufacturer, model = [p.strip() for p in title.split(' | ', 1)]
    else:  # 01: «Young Chang Y-150»
        manufacturer, model = 'Young Chang', title[len('Young Chang'):].strip()

    body = lines[1:]
    # description = paragraphs before the first info marker
    stop = next((i for i, l in enumerate(body) if INFO_HEAD.match(l.strip()) or CLASSIC.match(l.strip())), len(body))
    paras, cur = [], []
    for l in body[:stop]:
        if l.strip():
            cur.append(l.strip())
        elif cur:
            paras.append(' '.join(cur)); cur = []
    if cur:
        paras.append(' '.join(cur))

    rest = body[stop:]
    additional, drawing, finishes, specs = [], [], [], []
    spec_model = None
    mode = 'info'
    for l in rest:
        s = l.strip()
        if not s:
            if mode == 'finish' and finishes:
                mode = 'after-finish'
            continue
        if INFO_HEAD.match(s):
            continue
        if s in DRAW_HEAD:
            mode = 'draw'; continue
        if s in FINISH_HEAD:
            mode = 'finish'; continue
        if mode == 'info':
            additional.append(s.lstrip('- ').strip())
        elif mode == 'draw':
            parts = [p.strip() for p in l.split('\t') if p.strip()]
            if len(parts) >= 2:
                drawing.append({'label': parts[0], 'value': ' '.join(parts[1:])})
        elif mode == 'finish':
            finishes.append(dedupe_half(s))
        elif mode in ('after-finish', 'spec'):
            parts = [p.strip() for p in l.split('\t') if p.strip()]
            if len(parts) >= 2:
                mode = 'spec'
                specs.append({'label': re.sub(r'\s+', ' ', parts[0]), 'value': ' '.join(parts[1:])})
            elif mode == 'after-finish':
                spec_model = s; mode = 'spec'

    # «Μέγεθος / Στυλ / Τελείωμα» lines -> key/value (kept also verbatim in additional)
    facts = []
    for a in additional:
        m = re.match(r'^(Μέγεθος|ΜΕΓΕΘΟΣ|Στυλ|ΣΤΥΛ|Τελείωμα|ΤΕΛΕΙΩΜΑ|Μοντέλο)\s*:\s*(.+)$', a)
        if m:
            facts.append({'label': FACT_LABEL[unaccent(m.group(1)).upper()], 'value': m.group(2).strip()})
    return manufacturer, model, paras, additional, facts, drawing, finishes, spec_model, specs


def trim_white(src, dst, pad_ratio=0.02, thresh=22):
    """Crop only the empty white margin around the piano (nothing of the instrument is removed)."""
    im = Image.open(src).convert('RGB')
    # off-white studio backgrounds (e.g. 242,248,244) -> white, so that mix-blend-mode: multiply
    # dissolves them into the card colour. Only light, almost neutral pixels are touched.
    px = im.load()
    for y in range(im.size[1]):
        for x in range(im.size[0]):
            r, g, b = px[x, y]
            if min(r, g, b) >= 232 and max(r, g, b) - min(r, g, b) <= 10:
                px[x, y] = (255, 255, 255)
    bg = Image.new('RGB', im.size, (255, 255, 255))
    diff = ImageChops.difference(im, bg).convert('L').point(lambda p: 255 if p > thresh else 0)
    box = diff.getbbox()
    if not box:
        shutil.copy(src, dst); return im.size, im.size
    w, h = im.size
    pad = round(max(w, h) * pad_ratio)
    box = (max(0, box[0] - pad), max(0, box[1] - pad), min(w, box[2] + pad), min(h, box[3] + pad))
    out = im.crop(box)
    out.save(dst, quality=92, optimize=True, progressive=True, subsampling=0)
    return im.size, out.size


def main():
    photo_dir = ROOT / 'assets/photos/pianos/new'
    doc_dir = ROOT / 'assets/docs/pianos/new'
    photo_dir.mkdir(parents=True, exist_ok=True)
    doc_dir.mkdir(parents=True, exist_ok=True)

    records = []
    for n in range(1, 29):
        nn = f'{n:02d}'
        txt = SRC / f'new-piano_{nn}.txt'
        jpg = SRC / f'new-piano_{nn}.jpg'
        raw = txt.read_text(encoding='utf-8')
        manufacturer, model, paras, additional, facts, drawing, finishes, spec_model, specs = parse(n, raw)
        slug = slugify(f'{manufacturer} {model}')
        ptype, evidence = MANUAL[n]

        orig_size, out_size = trim_white(jpg, photo_dir / f'{slug}.jpg')
        pdfs = sorted(SRC.glob(f'new-piano_{nn}[-_]*.pdf'))
        pdf = None
        if pdfs:
            shutil.copy(pdfs[0], doc_dir / f'{slug}.pdf')
            pdf = {'src': f'assets/docs/pianos/new/{slug}.pdf', 'source': pdfs[0].name,
                   'label': f'Φυλλάδιο κατασκευαστή — {model} (PDF)', 'language': 'de/en/fr'}

        records.append({
            'id': f'new-{nn}',
            'slug': slug,
            'url': f'/pianos/new/{slug}/',     # future product page (WordPress)
            'detailPage': None,                # set to a real path when the page exists
            'manufacturer': manufacturer,
            'manufacturerSlug': slugify(manufacturer),
            'model': model,
            'type': ptype,
            'typeLabel': TYPE_LABEL[ptype],
            'typeEvidence': evidence,
            'category': 'Κλασικό πιάνο' if re.search(r'Κλασικό πιάνο', raw) else None,
            'sizeCm': SIZE[n],
            'description': paras,              # original text, verbatim
            'additional': additional,          # «Πρόσθετες πληροφορίες», verbatim lines
            'facts': facts,                    # Μέγεθος / Στυλ / Τελείωμα as key-value
            'drawing': drawing,                # Petrof: a / b / height / weight from the drawing
            'finishes': finishes,              # Petrof: finish list (copy-paste doubling removed)
            'specModel': spec_model,           # Petrof: model named on the spec table
            'specs': specs,                    # Petrof: technical specification table
            'images': [{
                'src': f'assets/photos/pianos/new/{slug}.jpg',
                'width': out_size[0], 'height': out_size[1],
                'alt': f'{manufacturer} {model}' + (f', {TYPE_LABEL[ptype].lower()}' if ptype else '') + ', σε ουδέτερο φόντο',
                'source': jpg.name, 'sourceSize': list(orig_size),
            }],
            'pdf': pdf,
            'source': {'txt': txt.name, 'photo': jpg.name},
            'notes': NOTES.get(n, []),
            'raw': raw.replace('\r\n', '\n'),
            '_order': None,
        })

    # order
    mf = sorted({r['manufacturer'] for r in records}, key=lambda s: unicodedata.normalize('NFKD', s))
    trank = {'upright': 0, 'grand': 1, None: 2}
    records.sort(key=lambda r: (mf.index(r['manufacturer']), trank[r['type']], r['sizeCm'] or 9999))
    for i, r in enumerate(records, 1):
        r['_order'] = i
        r['order'] = r.pop('_order')

    (ROOT / 'data').mkdir(exist_ok=True)
    js = json.dumps(records, ensure_ascii=False, indent=2)
    (ROOT / 'data/new-pianos.json').write_text(js + '\n', encoding='utf-8')
    (ROOT / 'data/new-pianos.js').write_text(
        '/* Nikotian — Καινούργια πιάνα: product data.\n'
        '   Generated by tools/build-new-pianos-data.py from new-pianos.zip — do not edit by hand;\n'
        '   change the TXT/MANUAL table and rebuild. Same records as data/new-pianos.json. */\n'
        'window.NIKOTIAN_NEW_PIANOS = ' + js + ';\n', encoding='utf-8')

    for r in records:
        print(f"{r['order']:>2} {r['id']} {r['manufacturer']:<18} {r['model']:<34} {str(r['type']):<8} "
              f"pdf={'Y' if r['pdf'] else '-'} desc={len(r['description'])} add={len(r['additional'])} "
              f"specs={len(r['specs'])} fin={len(r['finishes'])} img={r['images'][0]['sourceSize']}->{r['images'][0]['width']}x{r['images'][0]['height']}")


if __name__ == '__main__':
    main()
