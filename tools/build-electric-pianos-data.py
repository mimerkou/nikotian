#!/usr/bin/env python3
"""Nikotian — build the «Ηλεκτρικά πιάνα» data from the supplied model folder.

Usage:  python3 -I tools/build-electric-pianos-data.py <electric-folder> <project-root>

<electric-folder> = images/pianos/electric/ as supplied: one TXT per model («DYNATONE SLP-175.txt»)
and its photographs («DYNATONE SLP-175_01.jpg» … «_08.jpg»).

Writes:
  data/electric-pianos.js     window.NIKOTIAN_ELECTRIC_PIANOS = [...]  (used by the page; works on file://)
  data/electric-pianos.json   the same records                         (future Product Detail Template / WP import)
  assets/photos/pianos/electric/source/<slug>-NN.jpg   byte-for-byte copies of the supplied files
  assets/photos/pianos/electric/<slug>-<role>.jpg      exact rectangular crops of the photographic areas

Why crops: the supplied files are the manufacturer's product sheets (photographs with English headings,
logos, badges and captions printed on them). The page only shows pure photographic areas, cut out at
their native pixels: no scaling, no retouching, no background change, no AI. The originals stay in
`gallery` for the future product page.

Decided by hand (MANUAL): display names, the crop boxes and roles, alt texts, and which facts are shown.
Facts come only from the TXT or from the manufacturer's own sheets in the same folder (source noted per
fact). No prices, availability, dimensions or finishes are added.

Record shape = the shared product model (data/PRODUCT-MODEL.md).
"""
import json, re, shutil, sys
from pathlib import Path
from PIL import Image

SRC = Path(sys.argv[1])
ROOT = Path(sys.argv[2])
OUT_IMG = ROOT / 'assets/photos/pianos/electric'
OUT_SRC = OUT_IMG / 'source'

CATEGORY = {'category': 'electric', 'categoryLabel': 'Ηλεκτρικό πιάνο', 'categoryUrl': '/pianos/digital/'}

MANUAL = {
    'DYNATONE SLP-175': {
        'manufacturer': 'Dynatone', 'manufacturerSlug': 'dynatone', 'model': 'SLP-175',
        # role: primary (featured photograph / card image) · detail (featured details) ·
        #       editorial (used by the page outside the product block) · hero (page hero)
        'crops': [
            ('primary', '01', (0, 200, 836, 778),
             'Dynatone SLP-175 σε σκούρο φινίρισμα, σε δωμάτιο με ξύλινο πάτωμα'),
            ('detail', '07', (3, 110, 395, 338),
             'Λεπτομέρεια: ο πίνακας χειρισμού δίπλα στα πλήκτρα του Dynatone SLP-175'),
            ('detail', '07', (466, 110, 857, 338),
             'Λεπτομέρεια: τα τρία πεντάλ του Dynatone SLP-175'),
            ('editorial', '05', (0, 64, 700, 378),
             'Κοντινό στο πληκτρολόγιο του Dynatone SLP-175, σε λευκό φινίρισμα'),
            ('hero', '02', (0, 350, 860, 722),
             'Το Dynatone SLP-175 στη γωνία ενός φωτεινού δωματίου, δίπλα σε βιβλιοθήκη'),
        ],
        'gallery_alt': {
            '01': 'Φυλλάδιο κατασκευαστή: Dynatone SLP-175, κεντρική φωτογραφία και βασικά χαρακτηριστικά (στα αγγλικά)',
            '02': 'Φυλλάδιο κατασκευαστή: φωτογραφίες του SLP-175 σε σκούρο και λευκό φινίρισμα',
            '03': 'Φυλλάδιο κατασκευαστή: ήχος, πληκτρολόγιο, πίνακας χειρισμού και υποδοχές (στα αγγλικά)',
            '04': 'Φυλλάδιο κατασκευαστή: ήχος και ηχεία (στα αγγλικά)',
            '05': 'Φυλλάδιο κατασκευαστή: πληκτρολόγιο NHA με μηχανισμό σφυριών (στα αγγλικά)',
            '06': 'Φυλλάδιο κατασκευαστή: πίνακας χειρισμού και υποδοχές (στα αγγλικά)',
            '07': 'Φυλλάδιο κατασκευαστή: λειτουργίες και πεντάλ (στα αγγλικά)',
            '08': 'Φυλλάδιο κατασκευαστή: πιστοποιήσεις και αυτόματη απενεργοποίηση (στα αγγλικά)',
        },
        # Facts. show=True → listed in the featured block (max 3); the rest are kept for the product page.
        'specs': [
            ('Ήχοι', '23 επιλεγμένοι ήχοι', 'TXT', True),
            ('Πληκτρολόγιο', '88 πλήκτρα με μηχανισμό σφυριών', 'Φυλλάδιο κατασκευαστή 01, 03, 05: «88-Hammer action keyboard», «NHA hammer-action keyboard»', True),
            ('Λειτουργίες', 'Εγγραφή, διαχωρισμός πληκτρολογίου, μετρονόμος', 'TXT', True),
            ('Πεντάλ', 'Τρία πεντάλ', 'Φυλλάδιο κατασκευαστή 07: «3-pedal system»', False),
            ('Ηχεία', '13 W + 13 W', 'Φυλλάδιο κατασκευαστή 04: «13W+13W speakers»', False),
            ('Άλλες λειτουργίες', 'Layer (δύο ήχοι μαζί), Twin Piano (δύο παίκτες), αυτόματη απενεργοποίηση', 'Φυλλάδιο κατασκευαστή 01, 07, 08', False),
        ],
        'notes': [
            'Οι φωτογραφίες είναι φυλλάδια του κατασκευαστή (860 px πλάτος) με τυπωμένο αγγλικό κείμενο· η σελίδα δείχνει μόνο καθαρές φωτογραφικές περιοχές τους.',
            'Τα φυλλάδια δείχνουν σκούρο και λευκό φινίρισμα· η διαθεσιμότητα φινιρισμάτων δεν επιβεβαιώνεται από το υλικό.',
            'Το TXT αναφέρει «διαχωρισμό του πληκτρολογίου» (Split στο φυλλάδιο 07).',
        ],
    },
}


def slugify(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def main():
    OUT_SRC.mkdir(parents=True, exist_ok=True)
    records = []
    for order, txt in enumerate(sorted(SRC.glob('*.txt')), start=1):
        key = txt.stem
        m = MANUAL[key]
        slug = slugify(f"{m['manufacturer']} {m['model']}")
        lines = [l.strip() for l in txt.read_text(encoding='utf-8').splitlines()]
        paras = [l for l in lines if l]
        assert paras[0] == key, f'first TXT line should be the name: {paras[0]!r}'
        body = paras[1:]

        photos = sorted(SRC.glob(f'{key}_*.jpg'))
        gallery = []
        for ph in photos:
            nn = ph.stem.rsplit('_', 1)[1]
            dst = OUT_SRC / f'{slug}-{nn}.jpg'
            shutil.copyfile(ph, dst)
            w, h = Image.open(ph).size
            gallery.append({'src': dst.relative_to(ROOT).as_posix(), 'width': w, 'height': h,
                            'alt': m['gallery_alt'][nn], 'source': ph.name})

        images, page_images = [], {}
        counts = {}
        for role, nn, box, alt in m['crops']:
            counts[role] = counts.get(role, 0) + 1
            suffix = role if counts[role] == 1 else f'{role}-{counts[role]}'
            ph = SRC / f'{key}_{nn}.jpg'
            im = Image.open(ph).convert('RGB').crop(box)
            dst = OUT_IMG / f'{slug}-{suffix}.jpg'
            im.save(dst, 'JPEG', quality=90, subsampling=0, optimize=True, progressive=True)
            entry = {'src': dst.relative_to(ROOT).as_posix(), 'width': im.width, 'height': im.height,
                     'alt': alt, 'role': role, 'source': ph.name, 'crop': list(box)}
            # hero / editorial crops belong to the page, not to the product presentation
            (images if role in ('primary', 'detail') else page_images.setdefault('list', [])).append(entry)

        records.append({
            'id': f'electric-{order:02d}',
            'slug': slug,
            'url': f"{CATEGORY['categoryUrl']}{slug}/",
            'detailPage': None,
            **CATEGORY,
            'condition': 'new',
            'manufacturer': m['manufacturer'],
            'manufacturerSlug': m['manufacturerSlug'],
            'model': m['model'],
            'name': f"{m['manufacturer']} {m['model']}",
            'originalName': key,
            'type': None,
            'typeLabel': None,
            'description': body,          # every TXT paragraph, verbatim (product page)
            'summary': body[:2],          # the short presentation shown in the featured block
            'specs': [{'label': l, 'value': v, 'source': s, 'show': show} for l, v, s, show in m['specs']],
            'images': images,
            'pageImages': page_images.get('list', []),
            'gallery': gallery,
            'pdf': None,
            'source': {'txt': txt.name, 'photos': [p.name for p in photos]},
            'raw': txt.read_text(encoding='utf-8'),
            'notes': m['notes'],
            'order': order,
        })

    (ROOT / 'data').mkdir(exist_ok=True)
    js = json.dumps(records, ensure_ascii=False, indent=2)
    (ROOT / 'data/electric-pianos.json').write_text(js + '\n', encoding='utf-8')
    (ROOT / 'data/electric-pianos.js').write_text(
        '/* Nikotian — Ηλεκτρικά πιάνα: product data.\n'
        '   Generated by tools/build-electric-pianos-data.py from images/pianos/electric/ — do not edit by hand;\n'
        '   change the MANUAL table and rebuild. Same records as data/electric-pianos.json.\n'
        '   Shape: data/PRODUCT-MODEL.md. */\n'
        f'window.NIKOTIAN_ELECTRIC_PIANOS = {js};\n', encoding='utf-8')
    print(f'{len(records)} record(s)')


if __name__ == '__main__':
    main()
