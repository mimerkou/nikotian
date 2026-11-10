#!/usr/bin/env python3
"""Nikotian — Product Details v2.0: publish every piano on the shared product page (piano.html?model=<slug>).

Usage (after the three collection builders):
    python3 -I tools/build-new-pianos-data.py      <new-pianos-dir>  .
    python3 -I tools/build-used-pianos-data.py     <used-pianos-dir> .
    python3 -I tools/build-electric-pianos-data.py <electric-dir>    .
    python3 -I tools/build-product-details.py      . <new-pianos-dir>

The builders write the ORIGINAL data (TXT verbatim, manufacturer tables, photos). This script applies the
EDITED layer from data/editorial/product-details.json on top, and keeps the two apart:
  original  description[], raw, specsOriginal[] (manufacturer table as supplied), drawing[], finishes[], facts[]
  edited    summary[] / lead[] / body[] (+ bodySource, editNote), specs[] (Greek, each with its source)
Every record gets detailPage = piano.html?model=<slug>. Grotrian models with a PDF also get the two
photographs embedded in that PDF (extracted with poppler's pdfimages, not retouched).
Re-running is safe: the script always starts from the original fields.
"""
import json, re, subprocess, sys, tempfile
from pathlib import Path
from PIL import Image, ImageChops

ROOT = Path(sys.argv[1])
NEW_SRC = Path(sys.argv[2]) if len(sys.argv) > 2 else None
EDIT = json.loads((ROOT / 'data/editorial/product-details.json').read_text(encoding='utf-8'))['records']
PDF_LANG = 'Γερμανικά, αγγλικά, γαλλικά'

# ------------------------------------------------------------------------------------------
# Petrof manufacturer table → Greek. Labels and values are translated, never changed in substance.
# ------------------------------------------------------------------------------------------
LABELS = {
    'Soundboard material': 'Ηχείο — υλικό', 'Sound board material': 'Ηχείο — υλικό',
    'Active area of soundboard (m2)': 'Ενεργή επιφάνεια ηχείου', 'Sound board active area': 'Ενεργή επιφάνεια ηχείου',
    'Ribs - number, shape': 'Νευρώσεις ηχείου', 'Ribs (number, shape)': 'Νευρώσεις ηχείου',
    'Soundboard construction': 'Κατασκευή ηχείου',
    'Cast iron plate': 'Χυτοσίδηρη πλάκα', 'Surfacing of iron plate': 'Φινίρισμα χυτοσίδηρης πλάκας',
    'Pin block - material': 'Βάση κουρδιστηριών (pin block)',
    'Wooden frame construction, material': 'Ξύλινος σκελετός', 'Wooden frame posts': 'Δοκοί ξύλινου σκελετού',
    'Cut off bar (corner cross rib) - material, number': 'Γωνιακή εγκάρσια νεύρωση',
    'Cut off bar (corner cross rib)': 'Γωνιακή εγκάρσια νεύρωση',
    'Cabinet material': 'Κέλυφος — υλικό',
    'Inner rim material': 'Εσωτερικό στεφάνι — υλικό', 'Inner rim thickness': 'Εσωτερικό στεφάνι — πάχος',
    'Outer rim - material': 'Εξωτερικό στεφάνι — υλικό', 'Descant post material': 'Δοκός πρίμων — υλικό',
    'Bridge - treble': 'Καβαλάρης πρίμων', 'Bridge - bass': 'Καβαλάρης μπάσων', 'Bridge pins': 'Καρφιά καβαλάρη',
    'Agraffes - material, number': 'Αγκράφες', 'Agraffes (material, number)': 'Αγκράφες',
    'Duplexes - front': 'Duplex — εμπρός', 'Duplexes - rear': 'Duplex — πίσω',
    'Strings - material': 'Χορδές', 'Hitching of plain strings': 'Στερέωση απλών χορδών',
    'Dampers - number': 'Αποσβεστήρες', 'Action': 'Μηχανισμός', 'Hammer heads': 'Κεφαλές σφυριών',
    'Keyboard': 'Πληκτρολόγιο', 'Black keys': 'Μαύρα πλήκτρα', 'Keys balancing, touch weight': 'Βάρος αφής',
    'Pedals': 'Πεντάλ', 'Castors': 'Ροδάκια', 'Felts colour': 'Χρώμα τσόχας',
    'Hydraulic slow close fallboard mech.': 'Υδραυλικό αργό κλείσιμο καπακιού πλήκτρων',
    'PETROF sign on right side wall': 'Λογότυπο στο δεξί πλευρικό τοίχωμα',
}
VALUES = {
    'solid resonance spruce wood': 'μασίφ ηχητικό ξύλο ελάτης',
    'wedgewise tapered': 'σφηνοειδής λέπτυνση', 'diaphragmatic': 'διαφραγματική',
    'wet sand casting': 'χύτευση σε υγρή άμμο', 'Wet sand casting': 'χύτευση σε υγρή άμμο',
    'paint with bronze dust': 'βαφή με σκόνη μπρούντζου',
    'light gold metallic paint, diamond effekt': 'ανοιχτόχρυση μεταλλική βαφή, εφέ διαμαντιού',
    'Multiplex beech plywood, density 800 - 850 kg/m3': 'πολυστρωματικό κόντρα πλακέ οξιάς, πυκνότητα 800–850 kg/m³',
    'multiplex beech plywood': 'πολυστρωματικό κόντρα πλακέ οξιάς',
    'beech, frame construction': 'οξιά, κατασκευή πλαισίου', 'spruce wood, 3+2 posts': 'έλατο, 3 + 2 δοκοί',
    'beech, 1': 'οξιά, 1', 'round shaped, multiple birch or beech': 'καμπύλη, πολυστρωματική σημύδα ή οξιά',
    'MDF, plywood, solid wood': 'MDF, κόντρα πλακέ, μασίφ ξύλο',
    'beech wood': 'ξύλο οξιάς', 'solid maple wood': 'μασίφ ξύλο σφενδάμου',
    'steel-round tips': 'χάλυβας, στρογγυλεμένες άκρες', 'steel-ground tips': 'χάλυβας, λειασμένες άκρες',
    'brass, 88': 'ορείχαλκος, 88', 'brass, 1-50': 'ορείχαλκος, 1–50', 'brass, 1-53': 'ορείχαλκος, 1–53',
    'steel wire, copper winding': 'χαλύβδινο σύρμα, περιέλιξη χαλκού',
    'double': 'διπλή', 'single': 'μονή', '1 - 70': '1–70', '1-69': '1–69',
    'top quality european action': 'ευρωπαϊκός μηχανισμός κορυφαίας ποιότητας',
    'top quality felt hammer heads': 'τσόχα κορυφαίας ποιότητας',
    'spruce wood, individually balanced keys': 'ξύλο ελάτης, πλήκτρα ζυγισμένα ένα προς ένα',
    '52g in bass - 48g in treble': '52 g στα μπάσα – 48 g στα πρίμα',
    '55g in bass - 50g in treble': '55 g στα μπάσα – 50 g στα πρίμα',
    'left - Unacorda, middle - Muffler (moderator), right - Forte': 'αριστερό: una corda · μεσαίο: σουρντίνα (moderator) · δεξί: forte',
    'Unacorda (Piano) pedal, Sostenuto (Prolongement) pedal, Forte pedal': 'una corda · sostenuto · forte',
    'yes': 'ναι', 'on demand': 'κατόπιν παραγγελίας', 'brass, braked castors': 'ορειχάλκινα, με φρένο',
    'red': 'κόκκινο', 'red+ black': 'κόκκινο και μαύρο', 'Ebony wood': 'έβενος', 'PETROF': 'PETROF',
    'beech, birch': 'οξιά, σημύδα', '5 longitudinal': '5 διαμήκεις',
    'spruce, 5 longitudinal + 2 cross': 'έλατο, 5 διαμήκεις + 2 εγκάρσιες',
    'birch plywood sandwich, inner veneer  Ebony Makassar': 'πολυστρωματικό σημύδας, εσωτερικός καπλαμάς Ebony Makassar',
}
COLOURS = {'White': 'Λευκό', 'Ivory white': 'Ιβουάρ', 'Black': 'Μαύρο', 'Walnut': 'Καρυδιά',
           'Mahogany': 'Μαόνι', 'Beech': 'Οξιά', 'Cherry': 'Κερασιά', 'Alder': 'Σκλήθρο'}
SURFACE = {'high polish': 'γυαλιστερό', 'satin': 'σατινέ'}


def num(v):
    """'2100 mm (82,68 inch)' → '2100'; '542' → '542'."""
    return re.match(r'\s*([\d.,]+)', v).group(1)


def finish_gr(f):
    m = re.match(r'(.+?), (high polish|satin) (\d{4})$', f)
    return f'{COLOURS[m.group(1)]} {SURFACE[m.group(2)]} ({m.group(3)})' if m else f


def petrof_table(rec):
    grand = rec['type'] == 'grand'
    out = []
    for s in rec['specsOriginal']:
        L, V = s['label'], s['value']
        src = f"Πίνακας κατασκευαστή στο TXT ({rec['specModel']}): «{L}: {V}»"
        if L.startswith('Length'):
            out.append({'label': 'Μήκος' if grand else 'Βάθος', 'value': f'{num(V)} mm', 'source': src})
        elif L.startswith('Width'):
            out.append({'label': 'Πλάτος', 'value': f'{num(V)} mm', 'source': src})
        elif L.startswith('Height'):
            out.append({'label': 'Ύψος', 'value': f'{num(V)} mm', 'source': src})
        elif L.startswith('Weight'):
            out.append({'label': 'Βάρος', 'value': f'{num(V)} kg', 'source': src})
        elif 'active area' in L.lower():
            out.append({'label': LABELS[L], 'value': f'{num(V)} m²', 'source': src})
        elif L.startswith('Ribs'):
            n, shape = [x.strip() for x in V.split(',')]
            out.append({'label': LABELS[L], 'value': f"{n}, {'σφαιρικές' if shape == 'spherical' else 'ασύμμετρες'}", 'source': src})
        else:
            out.append({'label': LABELS[L], 'value': VALUES.get(V, V), 'source': src})
    return out


def petrof_drawing(rec):
    """Dimensions from the manufacturer's drawing of THIS model (a = depth, b = height for uprights)."""
    out, src = [], 'Σχέδιο κατασκευαστή στο TXT'
    for d in rec['drawing']:
        mm = re.search(r'([\d.]+)\s*mm', d['value']); kg = re.search(r'([\d.]+)\s*kg', d['value'])
        if d['label'] == 'a':
            out.append({'label': 'Βάθος', 'value': f'{mm.group(1)} mm', 'source': f"{src}: a = {d['value']}"})
        elif d['label'] == 'b':
            out.append({'label': 'Ύψος', 'value': f'{mm.group(1)} mm', 'source': f"{src}: b = {d['value']}"})
        elif d['label'] == 'height' and 'Width' in d['value']:
            out.append({'label': 'Πλάτος', 'value': f'{mm.group(1)} mm', 'source': f"{src}: {d['value']}"})
        elif d['label'] == 'weight':
            out.append({'label': 'Βάρος', 'value': f'{kg.group(1)} kg', 'source': f"{src}: {d['value']}"})
    order = ['Πλάτος', 'Βάθος', 'Ύψος', 'Βάρος']
    return sorted(out, key=lambda s: order.index(s['label']))


def trim_white(im, pad_ratio=0.03, thresh=22):
    im = im.convert('RGB')
    px = im.load()
    for y in range(im.size[1]):
        for x in range(im.size[0]):
            r, g, b = px[x, y]
            if min(r, g, b) >= 232 and max(r, g, b) - min(r, g, b) <= 10:
                px[x, y] = (255, 255, 255)
    box = ImageChops.difference(im, Image.new('RGB', im.size, (255, 255, 255))).convert('L').point(lambda p: 255 if p > thresh else 0).getbbox()
    if not box:
        return im
    pad = round(max(im.size) * pad_ratio)
    return im.crop((max(0, box[0] - pad), max(0, box[1] - pad), min(im.width, box[2] + pad), min(im.height, box[3] + pad)))


def pdf_photo(pdf, page, dst, max_w, trim):
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(['pdfimages', '-j', '-f', str(page), '-l', str(page), str(pdf), f'{tmp}/im'], check=True)
        src = sorted(Path(tmp).glob('im-*.jpg'))[0]
        im = Image.open(src); orig = im.size
        im = trim_white(im) if trim else im.convert('RGB')
        if im.width > max_w:
            im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
        im.save(dst, quality=86, optimize=True, progressive=True)
        return orig, im.size


def write(name, records):
    js_path, json_path = ROOT / f'data/{name}.js', ROOT / f'data/{name}.json'
    head = js_path.read_text(encoding='utf-8').split('window.', 1)[0].rstrip()
    if 'build-product-details.py' not in head:
        head = head[:-2].rstrip() + '\n   Product pages: detailPage + edited fields applied by tools/build-product-details.py. */'
    var = re.search(r'window\.(\w+)\s*=', js_path.read_text(encoding='utf-8')).group(1)
    text = json.dumps(records, ensure_ascii=False, indent=2)
    json_path.write_text(text + '\n', encoding='utf-8')
    js_path.write_text(f'{head}\nwindow.{var} = {text};\n', encoding='utf-8')


def base(r):
    r['detailPage'] = f"piano.html?model={r['slug']}"
    r['name'] = r.get('name') or ' '.join(x for x in (r['manufacturer'], r.get('model')) if x)


def main():
    # ---------------- Καινούργια ----------------
    new = json.loads((ROOT / 'data/new-pianos.json').read_text(encoding='utf-8'))
    photo_dir = ROOT / 'assets/photos/pianos/new'
    for r in new:
        e = EDIT.get(r['id'], {})
        base(r)
        r.setdefault('specsOriginal', r['specs'])
        r['specs'] = []
        for k in ('summary', 'body', 'bodySource', 'editNote'):
            if e.get(k):
                r[k] = e[k]
        curated = []
        if e.get('specs'):
            curated = e['specs']
        elif e.get('petrofTable'):
            curated = petrof_table(r)
            if e.get('specModelRow'):
                curated.insert(0, {'label': 'Έκδοση πίνακα προδιαγραφών', 'value': r['specModel'],
                                   'source': 'TXT: ο πίνακας του κατασκευαστή αναγράφει αυτή την έκδοση'})
        elif e.get('petrofDrawingOnly'):
            curated = petrof_drawing(r)
        if curated and r['finishes'] and (e.get('petrofTable') or e.get('petrofDrawingOnly')):
            curated.append({'label': 'Φινιρίσματα κατασκευαστή', 'value': ', '.join(finish_gr(f) for f in r['finishes']),
                            'source': 'TXT: λίστα «Finish/ΤΕΛΕΙΩΜΑ» του κατασκευαστή (κωδικός χρώματος σε παρένθεση)'})
        if curated:
            if r['typeLabel']:
                curated.insert(0, {'label': 'Τύπος', 'value': r['typeLabel'], 'source': f"Τεκμηρίωση τύπου: {r['typeEvidence']}"})
            r['specs'] = curated
        # PDF: label, language, size + the two photographs in it
        if r['pdf']:
            src_pdf = NEW_SRC / r['pdf']['source'] if NEW_SRC else None
            r['pdf'].update({'label': 'Φυλλάδιο κατασκευαστή', 'language': PDF_LANG,
                             'bytes': (ROOT / r['pdf']['src']).stat().st_size})
            if e.get('pdfPhotos') and src_pdf and src_pdf.exists():
                large = photo_dir / f"{r['slug']}-large.jpg"
                orig, size = pdf_photo(src_pdf, 2, large, 1400, True)
                r['images'][0]['large'] = {'src': large.relative_to(ROOT).as_posix(), 'width': size[0], 'height': size[1],
                                           'alt': f"{r['name']}, {r['typeLabel'].lower()} σε μαύρο γυαλιστερό φινίρισμα",
                                           'fit': 'contain', 'source': f"{src_pdf.name}, σελ. 2", 'sourceSize': list(orig)}
                det = photo_dir / f"{r['slug']}-detail.jpg"
                orig, size = pdf_photo(src_pdf, 1, det, 1600, False)
                r['gallery'] = [{'src': det.relative_to(ROOT).as_posix(), 'width': size[0], 'height': size[1],
                                 'alt': e['galleryAlt'], 'fit': 'cover', 'role': 'gallery',
                                 'source': f"{src_pdf.name}, σελ. 1 (εξώφυλλο)", 'sourceSize': list(orig)}]
    write('new-pianos', new)

    # ---------------- Μεταχειρισμένα: name, photo, type, internal reference — nothing else ----------------
    used = json.loads((ROOT / 'data/used-pianos.json').read_text(encoding='utf-8'))
    for r in used:
        base(r)
        r['ref'] = r['id'].split('-')[1]          # number of the instrument in used-pianos.zip
        r['images'][0]['pageFit'] = 'photo'       # showroom photograph: shown whole on the product page
    write('used-pianos', used)

    # ---------------- Ηλεκτρικά: the eight supplied photographs, whole ----------------
    el = json.loads((ROOT / 'data/electric-pianos.json').read_text(encoding='utf-8'))
    for r in el:
        e = EDIT.get(r['id'], {})
        base(r)
        if e.get('lead'):
            r['lead'] = e['lead']
        if e.get('allPhotos'):
            src = r.get('galleryOriginal') or r['gallery']
            r['galleryOriginal'] = src
            first, rest = src[0], src[1:]
            r['images'][0]['large'] = {**first, 'fit': 'contain'}
            r['gallery'] = [{**g, 'fit': 'contain', 'role': 'gallery'} for g in rest]
    write('electric-pianos', el)

    print('new', len(new), 'used', len(used), 'electric', len(el))


if __name__ == '__main__':
    main()
