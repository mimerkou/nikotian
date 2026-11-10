# Κλασικές Κιθάρες v1.0 — Απογραφή υλικού & εσωτερικές σημειώσεις (όχι για τον πελάτη ως έχει)

## Απογραφή (Documents/Websites/Nikotian/images/guitars)
| # | ID | Slug | Κατασκευαστής | Μοντέλο (TXT) | TXT ↔ JPG | px |
|---|---|---|---|---|---|---|
| 1 | guitar-jh-01 | juan-hernandez-sonata | Juan Hernández | Sonata | juan-hernandez-01 | 400×759 |
| 2 | guitar-jh-02 | juan-hernandez-maestro | Juan Hernández | Maestro | juan-hernandez-02 | 400×935 |
| 3 | guitar-jh-03 | juan-hernandez-concierto | Juan Hernández | Concierto | juan-hernandez-03 | 400×878 |
| 4 | guitar-jh-04 | juan-hernandez-profesor | Juan Hernández | Profesor | juan-hernandez-04 | 400×962 |
| 5 | guitar-jh-05 | juan-hernandez-estudio-clasica | Juan Hernández | Estudio Clasica | juan-hernandez-05 | 400×484 (μπροστινή + πίσω όψη) |
| 6 | guitar-az-01 | azahar-model-142 | Azahar | Model 142 | azahar-01 | 400×1002 |
| 7 | guitar-az-02 | azahar-model-140 | Azahar | Model 140 | azahar-02 | 400×1002 |
| 8 | guitar-az-03 | azahar-model-105 | Azahar | Model 105 | azahar-03 | 400×1002 |
| 9 | guitar-az-04 | azahar-model-102 | Azahar | Model 102 | azahar-04 | 400×1002 |

Σειρά εμφάνισης: όπως η αρίθμηση των φακέλων (01 Juan Hernández, 02 Azahar) και των αρχείων.

## Φωτογραφίες
- Αντίγραφα byte-for-byte. Δύο εξαιρέσεις, καταγεγραμμένες στο `images[].derived`:
  - **Sonata, κάρτα (v1.1):** το φόντο και η σκιά δαπέδου αντικαταστάθηκαν με το κεραμιδί #983302 των υπόλοιπων Juan Hernández (`tools/guitar_backdrop.py`). Το όργανο έμεινε αμετάβλητο. → `juan-hernandez-sonata-backdrop.jpg`.
  - **Sonata, hero (v1.0):** το σχεδόν λευκό φόντο (234,234,232) έγινε λευκό, ώστε να γίνεται Warm Beige με multiply. Τα pixels του οργάνου δεν άλλαξαν. → `juan-hernandez-sonata.jpg`.
  - **Estudio Clasica:** η κάρτα δείχνει μόνο την μπροστινή όψη (crop στο κενό ανάμεσα στις δύο όψεις). Ολόκληρη η φωτογραφία είναι στο `images[1]` και στην ενότητα 03.
- Οι υπόλοιπες έχουν ομοιόμορφο φόντο στούντιο: κεραμιδί #983302 (Juan Hernández) ή μπλε #394761 (Azahar). Το πλαίσιο της κάρτας παίρνει αυτό το χρώμα (`images[0].backdrop`). Δεν έγινε αφαίρεση φόντου.
- **Χαμηλή ανάλυση:** όλες οι φωτογραφίες έχουν πλάτος 400 px. Στο grid η κιθάρα εμφανίζεται περίπου 200 × 420 CSS px, άρα αρκετά καθαρά. Στο hero, σε retina, φαίνεται ελαφρώς μαλακή. Για τις σελίδες μοντέλων χρειάζονται φωτογραφίες ≥ 1200 px.
- Από το v1.1, δύο φόντα: κεραμιδί για όλες τις Juan Hernández και μπλε για όλες τις Azahar. Είναι φωτογραφίες κατασκευαστών, άρα χρειάζεται επιβεβαίωση δικαιωμάτων χρήσης. Αν γίνουν δικές μας λήψεις σε ενιαίο φόντο, το grid θα γίνει πιο ομοιογενές.

## Προς επιβεβαίωση
1. **Azahar Model 102:** η 2η παράγραφος του TXT είναι αυτούσια η περιγραφή του Juan Hernández Maestro («Πλάτη και πλευρές από τριανταφυλλιά Αμαζονίου…») και συγκρούεται με το «ξύλο etimoe». Δεν μπαίνει στο `description`. Κρατιέται στο `descriptionQuestioned` και στο `raw`.
2. **«Estudio Clasica»:** το TXT δεν έχει τόνο (ισπανικά: «Clásica»). Κρατήθηκε όπως είναι.
3. **«Juan Hernández»:** με τόνο, όπως στο brief. Τα TXT και το κείμενο της Homepage γράφουν «Juan Hernandez». Η Homepage δεν άλλαξε· προτείνεται ενιαία γραφή.
4. **Sonata «Body: Ovengkol»:** στα δεδομένα αποδόθηκε ως «Πλάτη και πλευρές». Χρειάζεται επιβεβαίωση.
5. Διαθεσιμότητα, τιμές, φινιρίσματα και μεγέθη δεν υπάρχουν στο υλικό. Η σελίδα δεν δείχνει τίποτα από αυτά.
6. Ορθογραφία των TXT (π.χ. «τριανταφυλιάς» με ένα λ στα Azahar 142/140), μικτά ελληνικά-αγγλικά-ισπανικά («solid in cedar», «sicomoro»). Τα κείμενα διατηρούνται αυτούσια. Θέλουν επιμέλεια πριν από τις σελίδες μοντέλων.

## Τυπογραφία hero
Το brief ζητά «Κλασικές» σε Commissioner. Κράτησα το εγκεκριμένο σύστημα (`.title`: Literata, με έμφαση σε Literata italic Heritage Red), όπως σε όλες τις συλλογές.

## Μελλοντικό URL
guitars.html → /kitheres/ · μοντέλα /kitheres/<slug>/ · φίλτρο ?brand=juan-hernandez|azahar.

---

## Guitar Product Details v1.0
- Σελίδα μοντέλου: `guitar.html?model=<slug>`, ίδιο template με το `piano.html` (`#pd[data-family="guitar"]`).
- Νέα κιθάρα: νέο JPG + TXT στο `images/guitars/<κατασκευαστής>/` → `python tools/build-guitars-data.py`. Δεν χρειάζεται HTML.
- Η σύντομη περιγραφή εμφανίζεται δίπλα στη φωτογραφία, όπως στα πιάνα. Η ενότητα «Περιγραφή» εμφανίζεται μόνο με μεγαλύτερο κείμενο (`body`).

---

## Επικοινωνία v1.0
- **Ενιαία πηγή:** `data/contact.json`. Τα στοιχεία στο `contact.html` έχουν `data-contact="<key>"`.
- **WordPress:** options page «Στοιχεία επικοινωνίας» (ACF ή Customizer): διεύθυνση, Maps URL, repeater τηλεφώνων (ομάδα, όνομα, εμφάνιση, E.164), email, ωράριο. Header, footer, Αρχική και Επικοινωνία διαβάζουν από ένα template part. Ο Ρομπέρ αλλάζει τηλέφωνα χωρίς HTML.
- **Φόρμα (v1.1):** μόνο οπτική παρουσίαση. Στο prototype μια έγκυρη υποβολή απλώς ξαναφορτώνει τη σελίδα· δεν στέλνεται τίποτα. Στο WordPress: ίδιο markup (labels, types, ids), αποστολή στο info@nikotian.gr, ασφάλεια, ενημέρωση απορρήτου στη θέση του σχολίου.
- **Μελλοντικό URL:** `/epikoinonia/` · άγκυρα `#ekthesi` = η γραμμή της διεύθυνσης (v1.1). Η σύνδεση των CTAs «Επισκεφθείτε την έκθεση» θα αποφασιστεί στο fine tuning.

### Για το fine tuning (δεν άλλαξαν αυθαίρετα)
1. **Footer (όλες οι σελίδες):** δείχνει 2 από τα 4 τηλέφωνα (210 380 8836, 697 203 4883), χωρίς ονόματα.
2. **Mobile menu (όλες οι σελίδες):** ίδια 2 τηλέφωνα.
3. **Αρχική «Η μουσική από κοντά»:** 1 σταθερό + 1 κινητό χωρίς όνομα. Το Maps CTA («Οδηγίες στον χάρτη») έχει προορισμό χωρίς «Nikotian» και διαφορετική ετικέτα από το «Οδηγίες πρόσβασης».
4. **Product Details (`js/product.js`):** ένα τηλέφωνο (210 380 8836). Σωστό, αλλά όχι από την κοινή πηγή.
5. **contact-hero:** 818 px πλάτος· στα 1920 εμφανίζεται ~1050 CSS px (μαλακή σε retina). Χρειάζεται ≥ 2000 px. Επίσης δεν φαίνεται να είναι η έκθεση της Σόλωνος· να επιβεβαιωθούν προέλευση και δικαιώματα χρήσης.
6. **Ωράριο λειτουργίας:** δεν υπάρχει στο υλικό. Υπάρχει θέση για μία γραμμή στο ledger.

---

## Site-Wide Fine Tuning v1.0
- **«Πιάνα»:** `<button class="nav__parent">` (WordPress: menu item χωρίς URL / «#» → walker που το αποδίδει ως button). Λογική στο `js/main.js`.
- **Προσυμπλήρωση φόρμας:** `contact.html?interest=<όνομα>&item=<slug>#contact-form` → `js/contact.js`.
  - WordPress / Contact Form 7 ή Gravity Forms: ίδιες παράμετροι. Το `item` → κρυφό πεδίο `product`, ώστε το email να δείχνει ποιο όργανο (μοναδικό slug).
  - Μελλοντικό URL: `/epikoinonia/?interest=…&item=…#contact-form`.
- **Page transitions:** καταργήθηκαν στο v1.3 (μη εγκεκριμένο fade). Η πλοήγηση είναι απλή.
- **Smooth scroll (v1.3):** `js/main.js` → «Smooth scroll to sections». Ισχύει μόνο για same-page anchors. Στο WordPress χρειάζεται το ίδιο script.
- **Motion System v1.2:** τα εγκεκριμένα animations δεν εξαρτώνται από το `prefers-reduced-motion` (απόφαση 2026-11-10). Δεν υπάρχει κανένας τέτοιος έλεγχος σε CSS ή JS.
- **Motion tokens:** `css/tokens.css` (`--ease-soft`, `--dur-underline-*`, `--dur-image`, `--scale-image`, `--dur-page`, `--nav-close-delay`).
