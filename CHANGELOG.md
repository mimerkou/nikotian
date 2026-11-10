# NIKOTIAN — Navigation Motion Hotfix v1.3 · Changelog (2026-11-10)

Βάση: Motion System v1.2. Αλλαγές μόνο σε `js/main.js`, `css/style.css` και `css/tokens.css`. Κείμενα, design, CTAs, Product Details, φόρμα και τα υπόλοιπα animations δεν άλλαξαν.

## 1. Smooth scroll στα sections (Αρχική και κάθε same-page anchor)
- Νέος scroll controller στο `js/main.js` («Smooth scroll to sections»), με `requestAnimationFrame` και easeInOutCubic.
  - Χωρίς στιγμιαίο άλμα πριν από την κίνηση.
  - Ομαλή αρχή και ομαλό τέλος.
- **Διάρκεια ανάλογα με την απόσταση:**
  - ~640 ms για μία οθόνη (Hero → Ο Οίκος);
  - ~520 ms για μικρές αποστάσεις;
  - 850 ms για μεγάλες (Hero → Πιάνα).
  - Ο χρόνος μετριέται ανά frame: αν ο browser καθυστερήσει στιγμιαία, η κίνηση περιμένει αντί να πηδήξει.
- **Offset:** το section σταματά 16 px κάτω από το sticky Header (`scroll-padding-top` + `scroll-margin-top` του στόχου).
- **URL και ιστορικό:** το `#hash` γράφεται στο URL με `pushState`. Back/Forward περνούν από τα sections και επιστρέφουν στη σωστή θέση.
- Αν ο επισκέπτης κάνει scroll με wheel, touch ή πλήκτρο κατά τη διάρκεια της κίνησης, αναλαμβάνει αμέσως εκείνος.
- **Εκτός controller:**
  - links προς άλλες σελίδες, links με `?query` και εξωτερικά links;
  - `href="#"`, το skip link και clicks με Ctrl/⌘/Shift.
- Αφαιρέθηκε το CSS `scroll-behavior: smooth`, ώστε να μην εκτελείται δεύτερο scroll από τον browser.

## 2. Κατάργηση page transition
- Αφαιρέθηκαν τα `@view-transition { navigation: auto; }`, `view-transition-name: site-header`, `::view-transition-group(*)`, `::view-transition-old(root)` / `::view-transition-new(root)` και το token `--dur-page`.
- Η πλοήγηση μεταξύ σελίδων είναι πλέον απλή και άμεση. Δεν υπάρχει fade, overlay ή JavaScript interception.

---

# NIKOTIAN — Motion System v1.2 · Changelog (2026-11-10)

Βάση: Motion System Fix v1.1. Τα εγκεκριμένα animations δεν εξαρτώνται πλέον από τη ρύθμιση `prefers-reduced-motion`. Δεν άλλαξε τίποτε άλλο.

- **CSS:** αφαιρέθηκαν όλα τα `@media (prefers-reduced-motion: …)`.
  - 14 μπλοκ `no-preference` έγιναν κανονικοί κανόνες, χωρίς αλλαγή σε διάρκειες, easing ή ένταση. Αφορούν: hero entrances (όλες οι σελίδες), πεντάγραμμο Hero, timeline Αρχικής, reveals και chronicle στον «Οίκο», image hover, smooth scroll, page transitions και εμφάνιση καρτών.
  - Διαγράφηκαν 2 μπλοκ `reduce`: εναλλακτική φωτεινότητα εικόνας και προσαρμογές panels/buttons.
  - Αφαιρέθηκε το αχρησιμοποίητο token `--dur-feedback`.
  - Αρχεία: `style.css`, `about.css`, `contact.css`, `new-pianos.css`, `product.css`, `services.css`, `tokens.css`.
- **JavaScript:** αφαιρέθηκαν όλοι οι έλεγχοι `matchMedia('(prefers-reduced-motion: no-preference)')`.
  - `main.js`: reveals.
  - `about.js`: γραμμή διαδρομής.
  - `new-pianos.js`: reveals, featured, εμφάνιση καρτών μετά από φίλτρο.
  - `product.js`: reveals.
  - Το IntersectionObserver, οι listeners, το φιλτράρισμα και η γκαλερί δεν άλλαξαν. Μόνο σε browser χωρίς IntersectionObserver το περιεχόμενο εμφανίζεται αμέσως.
- **Page transitions:** `@view-transition { navigation: auto; }` χωρίς προϋπόθεση. Ίδιο cross-fade 260 ms. Σε browsers χωρίς υποστήριξη η πλοήγηση γίνεται κανονικά.

---

# NIKOTIAN — Motion System Fix v1.1 · Changelog (2026-11-10)

Βάση: Site-Wide Fine Tuning v1.0. Αλλαγές μόνο σε `css/style.css`, `css/tokens.css` και `js/main.js`.
Δεν άλλαξαν layout, τυπογραφία, χρώματα, φωτογραφίες, κείμενα, σύνδεσμοι, Product Details ή φόρμα.

## Αιτία
Στο `style.css` ένας καθολικός κανόνας για `prefers-reduced-motion: reduce` έκανε δύο πράγματα:
- μηδένιζε κάθε animation (`animation: none !important`);
- έκανε κάθε transition 1 ms (`transition-duration: 1ms !important`).

Έτσι, με reduced motion, χάνονταν και τα hover, focus και state feedback: underline, buttons, dropdown, mobile menu, gallery, φίλτρα. Όλα άλλαζαν απότομα.

## Διόρθωση: δύο επίπεδα κίνησης
- **Ο καθολικός κανόνας αφαιρέθηκε.**
- **Επίπεδο 1 · Micro-interactions — πάντα ενεργά, και στις δύο ρυθμίσεις:**
  - underlined CTAs (η γραμμή φεύγει δεξιά και επανέρχεται από αριστερά);
  - buttons (χρώμα, σκιά);
  - navigation: underline, βέλος, fade του dropdown και του mobile menu;
  - βελάκι των links, αλλαγές χρώματος, focus;
  - φίλτρα, cross-fade της γκαλερί και γραμμή των thumbnails στα Product Details;
  - header στο scroll.
- **Επίπεδο 2 · Διακοσμητική κίνηση — μόνο με `no-preference`:**
  - scroll reveals, εισαγωγές των hero, χρονολόγιο Αρχικής;
  - image zoom, page transitions, smooth scroll;
  - εμφάνιση καρτών μετά από φίλτρο, γραμμή διαδρομής στον «Οίκο».
- **Στοχευμένες προσαρμογές για reduce:**
  - Το dropdown, το mobile menu και το toast κάνουν fade στη θέση τους, χωρίς μετατόπιση.
  - Τα buttons κρατούν χρώμα και σκιά, χωρίς το ανέβασμα 1 px.
  - Το image hover γίνεται ήπια φωτεινότητα (+6%) σε 250 ms (νέο token `--dur-feedback`).
  - Το περιεχόμενο είναι ορατό αμέσως.
- **Hover σε touch laptops:** `hover: hover` → `any-hover: hover` στο CSS και στο dropdown (`js/main.js`). Ένα laptop με οθόνη αφής, που έχει και ποντίκι, παίρνει πλέον όλα τα hover effects.
- **JavaScript:** οι έλεγχοι `motionOK` στα `main.js`, `about.js`, `new-pianos.js` και `product.js` αφορούν μόνο κίνηση επιπέδου 2 (reveals, γραμμή διαδρομής, εμφάνιση καρτών). Με reduce, προσθέτουν αμέσως την ορατή κατάσταση. Δεν βρέθηκε άλλος κώδικας που να απενεργοποιεί κινήσεις.

---

# NIKOTIAN — Site-Wide Fine Tuning v1.0 · Changelog (2026-11-10)

Βάση: Contact Page v1.1. Χωρίς redesign. Δεν άλλαξαν logo, παλέτα, γραμματοσειρές, τυπογραφική κλίμακα, φωτογραφίες, product data ή templates.

## Όλες οι σελίδες
- **Header CTA «Επισκεφθείτε την έκθεση»** (desktop + mobile menu) → `contact.html`, στην αρχή της σελίδας. Ίδιο styling.
- **«Πιάνα» στο μενού:** δεν είναι πλέον σύνδεσμος. Είναι ένα ενιαίο κουμπί (κείμενο + βέλος) με `aria-expanded`.
  - Desktop: ανοίγει με hover και με click. Κλείνει με μικρή καθυστέρηση, ώστε να μην κλείνει όταν ο δείκτης πηγαίνει προς τις επιλογές.
  - Πληκτρολόγιο: Enter/Space ανοίγει, ↓/↑ μετακινούν στις επιλογές, Esc κλείνει.
  - Mobile: όλη η γραμμή «Πιάνα» ανοίγει/κλείνει το υπομενού. Το βέλος περιστρέφεται.
  - Οι τρεις σύνδεσμοι του υπομενού δεν άλλαξαν.
- **Κοινό underlined CTA** (`.link-arrow` / `.link-caps` / `.link-inline`):
  - Η γραμμή είναι πιο κοντά στο κείμενο (κενό .25em → .1em).
  - Λεπτή γραμμή 1 px στο χρώμα του κειμένου, σε light και dark sections.
  - Στο hover και στο keyboard focus, η γραμμή φεύγει προς τα δεξιά και ξανασχεδιάζεται από τα αριστερά (~400 ms).
  - Υλοποίηση με δύο pseudo-elements και transforms, χωρίς ορατό reset. Δεν εφαρμόζεται στους συνδέσμους μέσα σε κείμενο.
- **Image hover:** ενιαίος κανόνας για τις εικόνες που είχαν ήδη zoom (συλλογές Αρχικής, κάρτες προϊόντων).
  - Η κίνηση είναι ηπιότερη: 1.03 αντί για 1.035–1.04, σε 600 ms με ομαλό easing. Η παλιά κίνηση (1100 ms, έντονο ease-out) έμοιαζε απότομη.
  - Η εικόνα αποδίδεται σε δικό της layer, χωρίς layout shift.
  - Δεν προστέθηκε zoom σε άλλες εικόνες. Αφαιρέθηκε ένα ανενεργό transition στις εικόνες των Υπηρεσιών, που δεν είχαν hover.
- **Motion tokens** (`css/tokens.css`): κοινά durations και easings για underline, εικόνες, σελίδες και dropdown.
- **Page transitions:** cross-fade 260 ms με τα native View Transitions του browser, μόνο σε CSS (`@view-transition`).
  - Το Header μένει σταθερό ανάμεσα στις εσωτερικές σελίδες.
  - Χωρίς JS, SPA ή παρέμβαση στην πλοήγηση.
  - Σε browsers χωρίς υποστήριξη, η πλοήγηση γίνεται κανονικά.
- **Smooth scroll:** υπήρχε ήδη (`scroll-behavior` + `scroll-padding-top`). Ελέγχθηκε. Τα sections δεν κρύβονται πίσω από το Header.
- **Reveal safety net** (`js/main.js`): ένα block που προσπερνιέται με γρήγορο scroll ή άλμα σε anchor εμφανίζεται πλέον αμέσως.
  - Στο v1.1 μπορούσε να μείνει αόρατο (π.χ. Αρχική, «Ο Οίκος» μετά από End και επιστροφή).
- **prefers-reduced-motion:** χωρίς μετακινήσεις και page transition. Παραμένουν η αλλαγή χρώματος, η σταθερή γραμμή και μια ελαφριά φωτεινότητα στις εικόνες.

## Αρχική
- **Πεντάγραμμο:** τέσσερις προτάσεις ίδιου μήκους (54–60 χαρακτήρες, δύο γραμμές η καθεμία):
  - Ο Κάρλο Νικοτιάν ιδρύει τον Οίκο στην οδό Ακαδημίας 63.
  - Ξεκινά η συνεργασία με τον κατασκευαστή πιάνων Young Chang.
  - Ο Κάρολος και ο Ρομπέρ εντάσσονται σταδιακά στον Οίκο.
  - Η έκθεση της Nikotian βρίσκεται στη Σόλωνος 105, στην Αθήνα.
- **Τεχνογνωσία:** αφαιρέθηκε το «Ζητήστε χόρδισμα». Έμεινε το «Όλες οι υπηρεσίες →», με ίδιο styling και σύνδεσμο.
- **Η έκθεση:** το «Στείλτε μήνυμα» (mailto) έγινε «Επικοινωνήστε μαζί μας» → `contact.html`. Ίδιο outline button.

## Ο Οίκος
- Το «Επισκεφθείτε την έκθεση» → `contact.html` (χωρίς anchor). Τίποτε άλλο δεν άλλαξε.

## Υπηρεσίες
- **Τίτλος επικοινωνίας:** «Μιλήστε μας *για το πιάνο σας.*» Αντικαθιστά το «Το πιάνο σας αξίζει την κατάλληλη φροντίδα.». Η δίχρωμη σύνθεση παραμένει.
- **CTAs:**
  - Κύριο button: «Επικοινωνήστε μαζί μας» → `contact.html`.
  - Text link: «Καλέστε μας στο 210 380 8836 →» → `tel:+302103808836`.

## Καινούργια · Μεταχειρισμένα · Ηλεκτρικά
- **Breadcrumb «Πιάνα»:** απλό label. Χωρίς σύνδεσμο, χωρίς hover, μέσα στο ίδιο `nav > ol`.
- **«Επισκεφθείτε την έκθεση»** → `contact.html`. Ίδιο primary button.
- **«Καλέστε μας στο 210 380 8836 →»:** κοινό underlined text link αντί για outline button. Στο mobile στοιχίζεται στο κέντρο, κάτω από το button.
- **Φίλτρα:** καταργήθηκε το κόκκινο περίγραμμα που έμενε μετά την επιλογή.
  - Αιτία: ο Chrome κρατά το `:focus-visible` σε ένα `<select>` και μετά από επιλογή με mouse. Έτσι το κοινό κόκκινο focus ring έμενε γύρω από το control.
  - Λύση: το ring εμφανίζεται μόνο όταν η τελευταία ενέργεια έγινε με πληκτρολόγιο (`html[data-input]`).
  - Η επιλογή φαίνεται από την τιμή του select και από το γεμάτο segment. Ισχύει και για το φίλτρο των Κιθάρων.
- **Ηλεκτρικά:** νέος τίτλος «Γνωρίστε τα ηλεκτρικά πιάνα *από κοντά.*» με ίδια κλίμακα.

## Κιθάρες
- Νέος τίτλος «Δείτε τις κιθάρες *από κοντά.*».
- «Επισκεφθείτε την έκθεση» → `contact.html`.
- Το τηλέφωνο είναι πλέον underlined text link.

## Product Details (όλα τα πιάνα και οι κιθάρες, 65 σελίδες)
- **«Ρωτήστε για το μοντέλο»:** αντί για `mailto:` οδηγεί στο `contact.html?interest=<όνομα>&item=<slug>#contact-form`.
  - Το όνομα προέρχεται από τα product data, με σωστό URL encoding (ελληνικά, «&», «Č», τόνοι).
- **Breadcrumb «Πιάνα»** (όταν εμφανίζεται): απλό label, όπως στις συλλογές.

## Επικοινωνία
- Νέο `js/contact.js` (το μόνο που προστέθηκε). Δεν άλλαξε κανένα στοιχείο της σχεδίασης v1.1.
- **Προσυμπλήρωση:** το πεδίο «Μήνυμα» γεμίζει με «Ενδιαφέρομαι για το {μοντέλο}».
  - Γίνεται μέσω `URLSearchParams` και `.value`, όχι HTML.
  - Μόνο όταν το πεδίο είναι κενό· ό,τι έχει γράψει ο επισκέπτης δεν αντικαθίσταται.
  - Χωρίς παράμετρο, το πεδίο μένει κενό.
- **Εσωτερικό αναγνωριστικό:** το `item` (slug) μπαίνει σε κρυφό πεδίο `product`.
  - Έτσι διακρίνονται τα μεταχειρισμένα με ίδιο όνομα (π.χ. τρία «Young Chang 121»).
  - Ο αριθμός φωτογραφίας δεν εμφανίζεται πουθενά.
- **Scroll:** η φόρμα φέρνεται ξανά στη θέση της αφού φορτώσουν fonts και εικόνες, εκτός αν ο επισκέπτης έχει ήδη κάνει scroll. Η αρχή της φόρμας μένει κάτω από το Header.
- Κουμπί «Αποστολή μηνύματος» ίδιο. Χωρίς backend, χωρίς mock επιβεβαιώσεις.
