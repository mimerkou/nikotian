# Nikotian — Κοινό product data model (μουσικά όργανα: πιάνα και κιθάρες)

Ένα μοντέλο εγγραφής για όλα τα πιάνα (Καινούργια / Μεταχειρισμένα / Ηλεκτρικά), έτοιμο να γίνει
WordPress Custom Post Type. Ο ίδιος renderer (`js/new-pianos.js`) εμφανίζει κάθε συλλογή από αυτά τα δεδομένα:
featured παρουσίαση όταν η συλλογή έχει ένα μοντέλο (`data-layout="auto"`), αλλιώς το κοινό grid 3/2/1,
και τη μπάρα φίλτρων μόνο από `data-min-items` μοντέλα και πάνω.

Αναφορά: `data/electric-pianos.json` (v1.0). Τα `new-pianos.json` και `used-pianos.json` χρησιμοποιούν ήδη
τα ίδια βασικά πεδία (id, slug, url, detailPage, manufacturer, manufacturerSlug, model, type, typeLabel,
description, images, pdf, order)· στο import προς WordPress αντιστοιχίζονται στον ίδιο CPT όπως παρακάτω.

## Πεδία

| Πεδίο | Υποχρ. | Περιγραφή | WordPress (CPT `piano`) |
|---|---|---|---|
| `id` | ναι | Μοναδικό ID (`electric-01`) | post ID (το παλιό ID σε meta `legacy_id`) |
| `slug` | ναι | `dynatone-slp-175` | post slug |
| `url` | ναι | Μελλοντικό URL της σελίδας μοντέλου | permalink `/pianos/<κατηγορία>/<slug>/` |
| `detailPage` | — | Πραγματικός σύνδεσμος όταν η σελίδα μοντέλου είναι δημοσιευμένη (`piano.html?model=<slug>`)· `null` = «σελίδα σε προετοιμασία» | — (post status «Δημοσιευμένο») |
| `category` | ναι | `new` · `used` · `electric` (πιάνα) · `guitar` (κλασικές κιθάρες, v1.0) | taxonomy `instrument_category` (Καινούργιο πιάνο / Μεταχειρισμένο πιάνο / Ηλεκτρικό πιάνο / Κλασική κιθάρα) |
| `manufacturer`, `manufacturerSlug` | ναι | Κατασκευαστής (εμφάνιση + φίλτρο) | taxonomy `piano_manufacturer` |
| `model` | — | Ονομασία μοντέλου (χωρίς κατασκευαστή) | ACF `model` |
| `name` | ναι | Πλήρης ονομασία | post title |
| `type`, `typeLabel` | — | `upright` / `grand` όπου εφαρμόζεται· `null` στα ηλεκτρικά | taxonomy `piano_type` (προαιρετική) |
| `images[0]` | ναι | Βασική φωτογραφία (`role: primary`)· `fit: contain` (αποκομμένο όργανο σε λευκό) ή `cover` (φωτογραφία χώρου) | featured image |
| `images[0].large` | — | Μεγαλύτερη έκδοση της ίδιας φωτογραφίας για τη σελίδα μοντέλου (`src, width, height, alt, fit, source`) | featured image (πλήρες μέγεθος) |
| `images[1…]` | — | Λεπτομέρειες για την featured παρουσίαση (`role: detail`, έως 3) | ACF gallery `detail_images` |
| `gallery` | — | Πρόσθετες φωτογραφίες της σελίδας μοντέλου, με τη σειρά τους (`src, width, height, alt, fit, source`) | ACF gallery `gallery` |
| `description` | — | Παράγραφοι κειμένου (TXT) | post content |
| `summary` | — | Σύντομη παρουσίαση: featured θέση και κύρια παρουσίαση της σελίδας μοντέλου | excerpt |
| `lead` | — | Κείμενο κύριας παρουσίασης μόνο για τη σελίδα μοντέλου, όταν διαφέρει από το `summary` της συλλογής (Ηλεκτρικά) | excerpt (override) |
| `ref` | — | Εσωτερικός αριθμός φυσικού οργάνου (μεταχειρισμένα, αριθμός αρχείου του ZIP)· μόνο στο προσυμπληρωμένο email, δεν εμφανίζεται στη σελίδα (v2.1) | ACF `ref` (ιδιωτικό) |
| `images[0].pageFit` | — | `photo`: φωτογραφία έκθεσης, εμφανίζεται ολόκληρη· το πλαίσιο παίρνει τις αναλογίες της | ACF / αυτόματο ανά κατηγορία |
| `body`, `bodySource` | — | Αναλυτικό κείμενο της σελίδας μοντέλου (ενότητα «Περιγραφή») και η πηγή του | post content / ιδιωτικό meta |
| `specs[]` | — | `{label, value, source, show}` — επιμελημένα τεχνικά χαρακτηριστικά (ελληνικά, με πηγή)· `show:true` = στη featured θέση (έως 3) | ACF repeater `specs` (label, value, show) |
| `specsOriginal[]` | — | Ο πίνακας του κατασκευαστή όπως δόθηκε (Petrof, αγγλικά) | ιδιωτικό meta |
| `pdf` | — | Τεχνικό φυλλάδιο: `src, label, language, bytes` | ACF file `pdf` (+ `pdf_language`) |
| `order` | ναι | Σειρά στη συλλογή | `menu_order` |
| `source`, `raw`, `notes` | — | Ιχνηλασιμότητα υλικού, εσωτερικές σημειώσεις | ιδιωτικά meta (όχι στο front) |

## Κανόνες

- Κενά προαιρετικά πεδία δεν παράγουν markup: χωρίς `summary` → `description`· χωρίς λεπτομέρειες ή
  `specs` με `show` → δεν εμφανίζονται οι αντίστοιχες ζώνες· χωρίς `pdf` → κανένας σύνδεσμος.
- Κανένα χειροκίνητο HTML ανά όργανο. Νέο πιάνο = νέα εγγραφή.
- Στο WordPress: ο Ρομπέρ προσθέτει «Νέο πιάνο», επιλέγει κατηγορία και κατασκευαστή, ανεβάζει φωτογραφία,
  γράφει περιγραφή — και το όργανο εμφανίζεται αυτόματα στη σωστή συλλογή. Η σελίδα κατηγορίας μετρά τις
  εγγραφές: 1 → featured, ≥2 → grid, ≥6 (και >1 κατασκευαστής) → φίλτρα.

## Σελίδα μοντέλου — Product Detail Template v1.0

Ένα αρχείο, `piano.html`, για κάθε όργανο: `piano.html?model=<slug>`. Το `js/product.js` βρίσκει την εγγραφή
στα δεδομένα της συλλογής (πρώτα `data/new-pianos.js`, τα άλλα φορτώνονται μόνο αν χρειαστεί) και παράγει:

| Ζώνη | Από τα πεδία | Όταν λείπουν |
|---|---|---|
| Breadcrumb «Συλλογή / Κατασκευαστής / Μοντέλο» | συλλογή, `manufacturer(Slug)`, `model` | Ο κατασκευαστής γίνεται link (φίλτρο της συλλογής) μόνο όπου η συλλογή φιλτράρει κατασκευαστές· αλλιώς απλό κείμενο. Χωρίς `model`: δύο επίπεδα |
| Gallery | `images[0]` (ή `.large`) + `gallery[]` | Μία φωτογραφία: χωρίς thumbnails |
| Κατασκευαστής, μοντέλο, τύπος | `manufacturer`, `model`/`name`, `typeLabel` + κατάσταση συλλογής | Χωρίς τύπο: μόνο η κατάσταση |
| Σύντομο κείμενο | `summary`, αλλιώς `description` | Κανένα markup |
| «Ρωτήστε για το μοντέλο» | `name` + συλλογή → `mailto:` με θέμα/κείμενο, `encodeURIComponent` | Πάντα (κάθε όργανο έχει όνομα) |
| Περιγραφή | `body[]` | Η ενότητα παραλείπεται· το κείμενο μένει στην κύρια παρουσίαση |
| Τεχνικά χαρακτηριστικά | `specs[]` `{label, value}`, αλλιώς `facts[]` | Η ενότητα παραλείπεται |
| Τεχνικό φυλλάδιο | `pdf` | Η ενότητα παραλείπεται |
| «Πίσω στα …» | συλλογή | Πάντα |

Μόνο εγγραφές με `detailPage` εμφανίζονται· οι υπόλοιπες δίνουν «Το μοντέλο δεν βρέθηκε» με links στις
συλλογές. `&preview=1` εμφανίζει οποιαδήποτε εγγραφή, μόνο για εσωτερικό έλεγχο (όχι link από κανένα σημείο).

WordPress: `single-piano.php` παράγει το ίδιο markup server-side από το CPT `piano`· taxonomies
`piano_category`, `piano_manufacturer`, `piano_type`· ACF `model`, `summary` (excerpt), `gallery`,
`specs` (repeater label/value), `pdf`. Για κιθάρες: ίδιο template, CPT/κατηγορία `guitar`, άλλο λεκτικό
breadcrumb/επιστροφής και `fit: cover` στις φωτογραφίες.

## v2.0 — Πρωτότυπα και επιμελημένα δεδομένα (όλα τα πιάνα)

Δύο στρώματα, πάντα χωριστά:

1. **Πρωτότυπα** — `tools/build-new|used|electric-pianos-data.py` διαβάζουν τα ZIP του πελάτη και γράφουν
   `description[]` (TXT αυτούσιο), `raw`, `facts[]`, `drawing[]`, `finishes[]`, τις φωτογραφίες και τα PDF.
2. **Επιμελημένα** — `data/editorial/product-details.json` (ένα αντικείμενο ανά `id`) και
   `tools/build-product-details.py`: `summary`/`lead`/`body` (+ `bodySource`, `editNote`), `specs[]` στα ελληνικά
   με την πηγή κάθε γραμμής, `detailPage`, `ref`, φωτογραφίες από τα PDF. Ο αρχικός πίνακας μένει στο `specsOriginal`.

Σειρά εκτέλεσης: οι τρεις builders, μετά `python3 -I tools/build-product-details.py . <new-pianos-dir>`.
Ασφαλές να ξανατρέξει. Κανένα HTML ανά προϊόν: και οι 56 σελίδες είναι το ίδιο `piano.html`.

Κανόνες περιεχομένου: TXT έως ~450 χαρακτήρες → όλο στην κύρια παρουσίαση· μεγαλύτερο → πρώτη παράγραφος
εκεί, οι υπόλοιπες στην «Περιγραφή». Γραμμή «Τύπος» στα χαρακτηριστικά μόνο όταν υπάρχουν και άλλα στοιχεία.
Πίνακας προδιαγραφών άλλης έκδοσης (π.χ. P 131 M1 για το P 131 E1) δεν εμφανίζεται.

WordPress: τα δύο στρώματα γίνονται ένα — ο Ρομπέρ γράφει απευθείας τα επιμελημένα πεδία στο CPT `piano`·
τα πρωτότυπα μεταφέρονται μία φορά ως ιδιωτικά meta για ιχνηλασιμότητα.


## Κλασικές κιθάρες (Guitar Collection v1.0)
`data/guitars.json` / `.js` (window.NIKOTIAN_GUITARS), από το `tools/build-guitars-data.py`. Χρησιμοποιεί τα ίδια πεδία με τα πιάνα, ώστε ένας ενιαίος CPT `instrument` να καλύπτει όλα τα όργανα. Ο Ρομπέρ προσθέτει κιθάρα επιλέγοντας κατηγορία και κατασκευαστή, χωρίς να αγγίξει τον σχεδιασμό.

| Πεδίο | Κιθάρες |
|---|---|
| `id` | `guitar-jh-01`, `guitar-az-01` κ.λπ. |
| `slug` / `url` | `juan-hernandez-sonata` → `/kitheres/juan-hernandez-sonata/` |
| `detailPage` | `guitar.html?model=<slug>` (Guitar Product Details v1.0)· όλες οι κάρτες ανοίγουν τη σελίδα του μοντέλου |
| `instrument` | `guitar` (v1.0). Στα πιάνα το πεδίο λείπει και σημαίνει `piano` → στο WordPress: ένας CPT `instrument`, taxonomy `instrument_type` (Πιάνο / Κιθάρα) |
| `category` / `categoryLabel` / `categoryUrl` | `guitar` / «Κλασική κιθάρα» / `/kitheres/` |
| `condition` | `null` (δεν αναφέρεται στο υλικό) |
| `manufacturer`, `manufacturerSlug` | `Juan Hernández` / `juan-hernandez` · `Azahar` / `azahar` → taxonomy `instrument_manufacturer` |
| `type`, `typeLabel` | `null` (ένας τύπος· καμία γραμμή τύπου στην κάρτα) |
| `images[0]` | κύρια φωτογραφία, `fit: contain`· `backdrop` = χρώμα φόντου στούντιο της φωτογραφίας (το πλαίσιο της κάρτας), `null` = Warm Beige + multiply· `derived` όταν το αρχείο δεν είναι αυτούσιο |
| `images[1…]` | πρόσθετες φωτογραφίες (`role: gallery`), π.χ. μπροστινή + πίσω όψη του Estudio Clasica |
| `description` | παράγραφοι του TXT, αυτούσιες |
| `descriptionQuestioned` | παράγραφοι του TXT που φαίνονται λανθασμένες (δεν δημοσιεύονται μέχρι να επιβεβαιωθούν) |
| `specs` / `specsOriginal` | μόνο όπου το TXT δίνει πεδία με ετικέτα (Sonata: Top / Body / Fingerboard → Καπάκι / Πλάτη και πλευρές / Ταστιέρα, τιμές αυτούσιες). Κανένα επινοημένο στοιχείο |
| `pdf` | `null` (δεν υπάρχει PDF στο υλικό) |
| `pageImages` | φωτογραφίες της σελίδας συλλογής που προέρχονται από το ίδιο όργανο (v1.1: το hero της Sonata, `role: hero`) |
| `source`, `notes`, `raw`, `order` | όπως στα πιάνα |

Renderer: `js/new-pianos.js` με `#np-grid[data-source="NIKOTIAN_GUITARS"][data-noun="κιθάρα|κιθάρες"]`. Δεν υπάρχουν radios τύπου, οπότε εμφανίζεται μόνο το φίλτρο κατασκευαστή.

**Σελίδα μοντέλου (Guitar Product Details v1.0):** `guitar.html?model=<slug>` → ίδιο `js/product.js` και `css/product.css` με το `piano.html`. Το `#pd[data-family="guitar"]` περιορίζει την αναζήτηση στη συλλογή κιθάρων (ρυθμίσεις στο `ALL_COLLECTIONS` του `product.js`: breadcrumb «Κιθάρες», «Πίσω στις Κιθάρες», θέμα email «Ενδιαφέρον για κιθάρα …», `portrait: true`). Από τα δεδομένα:
- `images[0]` → κύρια φωτογραφία· `images[]` με `role: gallery` → thumbnails (μόνο όταν υπάρχουν 2+).
- `backdrop` → χρώμα του πορτρέτου πλαισίου (ίδιο με την κάρτα)· η φωτογραφία εμφανίζεται ολόκληρη, χωρίς blend και χωρίς μεγέθυνση πέρα από τα pixels της.
- `description` → κείμενο δίπλα στη φωτογραφία (όπως η σύντομη περιγραφή των πιάνων)· `specs` → «Τεχνικά χαρακτηριστικά»· `pdf` → «Τεχνικό φυλλάδιο». Χωρίς δεδομένα, η ενότητα δεν εμφανίζεται.
- `descriptionQuestioned`, `notes`, `raw` δεν εμφανίζονται ποτέ.
