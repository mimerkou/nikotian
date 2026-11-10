// Nikotian — Product Detail Template v1.0 · all pianos since Product Details v2.0 (piano.html?model=<slug>)
// · classical guitars since Guitar Product Details v1.0 (guitar.html?model=<slug>)
// One renderer for every instrument page. Each page declares its family on #pd (data-family="piano" | "guitar";
// default piano) and looks only in that family's collections, so piano.html never shows a guitar and vice versa. It reads the record from the collection data
// (data/new-pianos.js, data/used-pianos.js, data/electric-pianos.js), never from per-product HTML.
//
// Optional sections render only when the record has the data:
//   gallery thumbnails  → 2+ photographs (images[0] / its .large version, then gallery[] and images[] with
//                         role «gallery»); 7+ → one dense row
//   main text           → lead[] (page only), else summary[], else description[]
//   description section → body[] (longer text). Without it, the short text stays in the main presentation.
//   specs               → specs[] {label, value} (fallback: facts[])
//   technical brochure  → pdf {src, label, language, bytes}
// A record is published only when it has detailPage. ?preview=1 renders any record (internal review only).
// Field reference: data/PRODUCT-MODEL.md. WordPress: single-piano.php renders the same markup.

(() => {
  const root = document.getElementById('pd');
  if (!root) return;

  const PHONE = { href: 'tel:+302103808836', label: '210 380 8836' };

  // One entry per collection. «label» feeds the breadcrumb, «back» the return link, «condition» the type line.
  // «family» = the page that renders it · «portrait» = vertical instrument (portrait gallery, studio backdrop)
  const ALL_COLLECTIONS = [
    { key: 'new', global: 'NIKOTIAN_NEW_PIANOS', src: 'data/new-pianos.js', href: 'new-pianos.html',
      label: 'Καινούργια πιάνα', back: 'Πίσω στα Καινούργια Πιάνα', condition: 'Καινούργιο' },
    { key: 'used', global: 'NIKOTIAN_USED_PIANOS', src: 'data/used-pianos.js', href: 'used-pianos.html',
      label: 'Μεταχειρισμένα πιάνα', back: 'Πίσω στα Μεταχειρισμένα Πιάνα', condition: 'Μεταχειρισμένο' },
    { key: 'electric', global: 'NIKOTIAN_ELECTRIC_PIANOS', src: 'data/electric-pianos.js', href: 'electric-pianos.html',
      label: 'Ηλεκτρικά πιάνα', back: 'Πίσω στα Ηλεκτρικά Πιάνα', condition: null, typeFallback: 'Ηλεκτρικό πιάνο' },
    { key: 'guitar', family: 'guitar', global: 'NIKOTIAN_GUITARS', src: 'data/guitars.js', href: 'guitars.html',
      label: 'Κιθάρες', back: 'Πίσω στις Κιθάρες', condition: null, typeFallback: 'Κλασική κιθάρα', portrait: true },
  ];
  const FAMILY = root.dataset.family || 'piano';
  const COLLECTIONS = ALL_COLLECTIONS.filter((c) => (c.family || 'piano') === FAMILY);
  const PAGE = FAMILY === 'piano' ? 'piano.html' : `${FAMILY}.html`;

  const params = new URLSearchParams(location.search);
  const slug = params.get('model') || '';
  const preview = params.get('preview') === '1';

  const esc = (s) => String(s ?? '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const list = (v) => (Array.isArray(v) ? v.filter((x) => x != null && String(x).trim() !== '') : []);

  /* ---------- Data: the collection already on the page first, the others on demand ---------- */
  const loadScript = (src) => new Promise((resolve) => {
    const s = document.createElement('script');
    s.src = src; s.onload = resolve; s.onerror = resolve;
    document.head.appendChild(s);
  });
  async function find() {
    const hint = params.get('c');
    const order = [...COLLECTIONS].sort((a, b) => (b.key === hint) - (a.key === hint));
    for (const c of order) {
      if (!Array.isArray(window[c.global])) await loadScript(c.src);
      const data = window[c.global];
      const rec = Array.isArray(data) ? data.find((r) => r.slug === slug) : null;
      if (rec) return { rec, c, data };
    }
    return null;
  }

  /* ---------- Normalised view of a record (one shape for every collection) ---------- */
  function view(rec, c, data) {
    const name = rec.name || [rec.manufacturer, rec.model].filter(Boolean).join(' ');
    const first = rec.images && rec.images[0];
    const photo = (im, extra) => (im ? { ...im, ...(extra || {}) } : null);
    // fit: «contain» = instrument cut out on white (shown whole, white → Warm Beige) · «cover» = photograph
    // filling the frame · «photo» = showroom photograph shown whole, the frame takes its proportions
    const primary = first ? photo(first.large ? { ...first.large } : first, { fit: (first.large && first.large.fit) || first.pageFit || first.fit || 'contain' }) : null;
    // additional photographs: gallery[] (pianos) and images[] entries with role «gallery» (guitars)
    const extra = [...list(rec.gallery), ...list(rec.images).slice(1).filter((im) => im.role === 'gallery')];
    const gallery = [primary, ...extra.map((g) => photo(g, { fit: g.fit || 'cover' }))].filter(Boolean);
    const lead = list(rec.lead);
    const summary = list(rec.summary);
    const description = list(rec.description);
    const specsArr = Array.isArray(rec.specs) && rec.specs.length ? rec.specs : list(rec.facts);
    // a manufacturer crumb links only where the collection really filters by manufacturer
    const brands = new Set((data || []).map((r) => r.manufacturerSlug));
    return {
      name,
      manufacturer: rec.model ? rec.manufacturer : '',
      manufacturerSlug: rec.manufacturerSlug,
      brandLink: brands.size > 1 && (data || []).length >= 6,
      model: rec.model || name,
      typeLine: [rec.typeLabel || c.typeFallback, c.condition].filter(Boolean).join(' · '),
      lead: lead.length ? lead : summary.length ? summary : description,   // main presentation
      body: list(rec.body),                               // description section (optional)
      specs: specsArr.filter((s) => s && s.label && s.value),
      pdf: rec.pdf && rec.pdf.src ? rec.pdf : null,
      gallery,
      portrait: Boolean(c.portrait),
    };
  }

  /* ---------- «Ρωτήστε για το μοντέλο» → the Contact form, message prefilled (Fine Tuning v1.0) ----------
     contact.html?interest=<public name>&item=<slug>#contact-form
     · interest = the name shown on the page (manufacturer + model), never the internal photo number;
     · item     = the unique slug, kept internally (hidden field of the form) so that instruments with the
                  same name (e.g. three used «Young Chang 121») are never confused.
     URLSearchParams encodes Greek, accents, «&», spaces etc.; contact.html reads it back with URLSearchParams. */
  function contactHref(v) {
    const q = new URLSearchParams({ interest: v.name, item: slug });
    return `contact.html?${q.toString()}#contact-form`;
  }

  /* ---------- Markup ---------- */
  const img = (im, cls, attrs = '') => `<img class="${cls}" src="${esc(im.src)}" alt="${esc(im.alt || '')}" width="${im.width}" height="${im.height}" decoding="async"${attrs}>`;

  function galleryHTML(v) {
    if (!v.gallery.length) return '';
    const many = v.gallery.length > 1;
    // portrait (guitars): every photograph whole on its own studio colour (images[].backdrop), never enlarged
    const fitClass = (im) => (v.portrait ? 'portrait' : ['cover', 'photo'].includes(im.fit) ? im.fit : 'contain');
    const bd = (im) => (v.portrait && /^#[0-9a-f]{3,8}$/i.test(im.backdrop || '') ? ` style="--backdrop: ${im.backdrop}"` : '');
    // one showroom photograph: the frame follows its proportions (landscape up to 12:5; portrait → square frame)
    const one = v.gallery[0];
    const ratio = !many && one.fit === 'photo' && one.width && one.height
      ? ` style="aspect-ratio: ${Math.min(2.4, Math.max(1, one.width / one.height)).toFixed(4)}"` : '';
    const slides = v.gallery.map((im, i) => `
        <figure class="pd-gallery__slide pd-gallery__slide--${fitClass(im)}${i === 0 ? ' is-active' : ''}"${bd(im)} id="pd-slide-${i}"${many ? ` role="group" aria-roledescription="φωτογραφία" aria-label="${i + 1} από ${v.gallery.length}"` : ''}${i ? ' aria-hidden="true"' : ''}>
          ${img(im, 'pd-gallery__img', (i === 0 ? ' fetchpriority="high"' : ' loading="lazy"') + (im.position ? ` style="object-position: ${esc(im.position)}"` : ''))}
        </figure>`).join('');
    const thumbs = many ? `
      <ul class="pd-thumbs${v.gallery.length > 6 ? ' pd-thumbs--dense' : ''}" style="--n: ${v.gallery.length}" aria-label="Φωτογραφίες του ${esc(v.name)}">
        ${v.gallery.map((im, i) => `
        <li class="pd-thumbs__item">
          <button class="pd-thumbs__btn pd-thumbs__btn--${v.portrait ? 'portrait' : fitClass(im) === 'contain' ? 'contain' : 'cover'}"${bd(im)} type="button" data-slide="${i}" aria-controls="pd-slide-${i}"${i === 0 ? ' aria-current="true"' : ''} tabindex="${i === 0 ? 0 : -1}">
            <span class="visually-hidden">Φωτογραφία ${i + 1} από ${v.gallery.length}: ${esc(im.alt || v.name)}</span>
            <img src="${esc(im.src)}" alt="" width="${im.width}" height="${im.height}" loading="lazy" decoding="async">
          </button>
        </li>`).join('')}
      </ul>` : '';
    return `
      <div class="pd-gallery${many ? ' pd-gallery--many' : ''}${v.portrait ? ' pd-gallery--portrait' : ''}">
        <div class="pd-gallery__stage"${ratio}>${slides}
        </div>${thumbs}
      </div>`;
  }

  function mainHTML(v, c) {
    return `
      ${galleryHTML(v)}
      <div class="pd-info">
        ${v.manufacturer ? `<p class="t-meta pd-info__brand">${esc(v.manufacturer)}</p>` : ''}
        <h1 class="title title--md pd-info__title" id="pd-title">${v.manufacturer ? `<span class="visually-hidden">${esc(v.manufacturer)} </span>` : ''}${esc(v.model)}</h1>
        ${v.typeLine ? `<p class="t-caption pd-info__type">${esc(v.typeLine)}</p>` : ''}
        ${v.lead.length ? `<div class="pd-info__text">${v.lead.map((t) => `<p class="t-body">${esc(t)}</p>`).join('')}</div>` : ''}
        <div class="pd-info__actions">
          <a class="btn btn--primary pd-info__cta" href="${esc(contactHref(v))}">Ρωτήστε για το μοντέλο</a>
          <a class="link-arrow pd-info__phone" href="${PHONE.href}">Καλέστε μας στο ${PHONE.label}</a>
        </div>
      </div>`;
  }

  const kb = (bytes) => (bytes ? `${Math.max(1, Math.round(bytes / 1024)).toLocaleString('el-GR')} KB` : '');

  function detailsHTML(v) {
    const hasBody = v.body.length > 0;
    const hasAside = v.specs.length > 0 || Boolean(v.pdf);
    if (!hasBody && !hasAside) return '';
    const desc = hasBody ? `
        <div class="pd-desc" data-reveal>
          <h2 class="t-meta t-label-rule pd-label" id="pd-desc-title">Περιγραφή</h2>
          <div class="pd-desc__text">${v.body.map((t) => `<p class="t-body">${esc(t)}</p>`).join('')}</div>
        </div>` : '';
    const specs = v.specs.length ? `
          <section class="pd-specs" aria-labelledby="pd-specs-title">
            <h2 class="t-meta t-label-rule pd-label" id="pd-specs-title">Τεχνικά χαρακτηριστικά</h2>
            <dl class="pd-specs__list">${v.specs.map((s) => `
              <div class="pd-specs__row"><dt class="t-meta">${esc(s.label)}</dt><dd class="t-meta-value">${esc(s.value)}</dd></div>`).join('')}
            </dl>
          </section>` : '';
    const meta = v.pdf ? [v.pdf.label || 'PDF', `PDF${v.pdf.bytes ? `, ${kb(v.pdf.bytes)}` : ''}`, v.pdf.language].filter(Boolean).join(' · ') : '';
    const doc = v.pdf ? `
          <section class="pd-doc" aria-labelledby="pd-doc-title">
            <h2 class="t-meta t-label-rule pd-label" id="pd-doc-title">Τεχνικό φυλλάδιο</h2>
            <p class="t-caption pd-doc__meta">${esc(meta)}</p>
            <a class="link-arrow pd-doc__link" href="${esc(v.pdf.src)}" target="_blank" rel="noopener" type="application/pdf">Προβολή PDF<span class="visually-hidden">: ${esc(v.name)} (ανοίγει σε νέα καρτέλα)</span> <span class="link-arrow__icon" aria-hidden="true">↗</span></a>
          </section>` : '';
    return `
      <div class="wrap pd-details__grid${hasBody ? '' : ' pd-details__grid--aside-only'}${hasAside ? '' : ' pd-details__grid--text-only'}">${desc}
        ${hasAside ? `<div class="pd-aside" data-reveal style="--d: 120ms">${specs}${doc}
        </div>` : ''}
      </div>`;
  }

  /* ---------- Gallery behaviour: thumbnails (click, ←/→/Home/End), swipe on the stage ---------- */
  function gallery() {
    const stage = root.querySelector('.pd-gallery__stage');
    const btns = [...root.querySelectorAll('.pd-thumbs__btn')];
    if (!stage || btns.length < 2) return;
    const slides = [...stage.querySelectorAll('.pd-gallery__slide')];
    let current = 0;
    const show = (i, focus) => {
      i = (i + slides.length) % slides.length;
      if (i === current) { if (focus) btns[i].focus(); return; }
      slides[current].classList.remove('is-active'); slides[current].setAttribute('aria-hidden', 'true');
      slides[i].classList.add('is-active'); slides[i].removeAttribute('aria-hidden');
      btns.forEach((b, j) => {
        if (j === i) b.setAttribute('aria-current', 'true'); else b.removeAttribute('aria-current');
        b.tabIndex = j === i ? 0 : -1;
      });
      current = i;
      if (focus) btns[i].focus();
    };
    btns.forEach((b, i) => b.addEventListener('click', () => show(i)));
    root.querySelector('.pd-thumbs').addEventListener('keydown', (e) => {
      const map = { ArrowRight: current + 1, ArrowLeft: current - 1, Home: 0, End: slides.length - 1 };
      if (!(e.key in map)) return;
      e.preventDefault();
      show(map[e.key], true);
    });
    let x0 = null; let y0 = null;
    stage.addEventListener('pointerdown', (e) => { if (e.pointerType !== 'mouse') { x0 = e.clientX; y0 = e.clientY; } });
    stage.addEventListener('pointerup', (e) => {
      if (x0 === null) return;
      const dx = e.clientX - x0; const dy = e.clientY - y0;
      x0 = null;
      if (Math.abs(dx) > 40 && Math.abs(dx) > Math.abs(dy) * 1.5) show(current + (dx < 0 ? 1 : -1));
    });
    stage.addEventListener('pointercancel', () => { x0 = null; });
  }

  function reveal() {
    const parts = root.querySelectorAll('[data-reveal]');
    if (!('IntersectionObserver' in window)) { parts.forEach((el) => el.classList.add('is-in')); return; }
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-in');
        io.unobserve(entry.target);
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -6% 0px' });
    parts.forEach((el) => io.observe(el));
  }

  function setMeta(title, description) {
    document.title = title;
    const m = document.querySelector('meta[name="description"]');
    if (m && description) m.setAttribute('content', description.length > 158 ? `${description.slice(0, 155).replace(/\s+\S*$/, '')}…` : description);
  }

  function markCollection(c) {
    document.querySelectorAll('[data-collection-link]').forEach((a) => {
      if (a.dataset.collectionLink === c.key) a.setAttribute('aria-current', 'true');
    });
    const self = document.querySelector('[data-lang-self]');
    if (self) self.setAttribute('href', `${PAGE}${location.search}`);
  }

  /* ---------- Not found / not published ---------- */
  function notFound() {
    setMeta('Το μοντέλο δεν βρέθηκε | Μουσικός Οίκος Nikotian');
    root.classList.add('pd--empty');
    const family = FAMILY === 'guitar' ? '<li><a href="guitars.html">Κιθάρες</a></li>' : '<li><span class="crumbs__label">Πιάνα</span></li>';
    document.getElementById('pd-crumbs').innerHTML = `<ol><li><a href="index.html">Αρχική</a></li>${family}</ol>`;
    document.getElementById('pd-main').innerHTML = `
      <div class="pd-missing">
        <h1 class="title title--md" id="pd-title">Το μοντέλο δεν βρέθηκε.</h1>
        <p class="t-body pd-missing__text">Η σελίδα που αναζητάτε δεν είναι διαθέσιμη. Δείτε τις συλλογές μας ή καλέστε μας στο <a class="link-inline" href="${PHONE.href}">${PHONE.label}</a>.</p>
        <ul class="pd-missing__links">${COLLECTIONS.map((c) => `<li><a class="link-arrow" href="${c.href}">${esc(c.label)} <span class="link-arrow__icon" aria-hidden="true">→</span></a></li>`).join('')}</ul>
      </div>`;
    root.removeAttribute('aria-busy');
  }

  /* ---------- Render ---------- */
  (async () => {
    const found = slug ? await find() : null;
    if (!found || (!found.rec.detailPage && !preview)) { notFound(); return; }
    const { rec, c, data } = found;
    const v = view(rec, c, data);

    setMeta(`${v.name} — ${c.label} | Μουσικός Οίκος Nikotian`, v.lead.join(' '));
    markCollection(c);

    // 01 · breadcrumb: collection / manufacturer / model — a crumb links only to a page that exists
    const brandHref = `${c.href}?brand=${encodeURIComponent(v.manufacturerSlug)}#syllogi`;
    document.getElementById('pd-crumbs').innerHTML = `
      <ol>
        <li><a href="${c.href}">${esc(c.label)}</a></li>
        ${v.manufacturer ? `<li>${v.brandLink ? `<a href="${esc(brandHref)}">${esc(v.manufacturer)}</a>` : esc(v.manufacturer)}</li>` : ''}
        <li><span aria-current="page">${esc(v.model)}</span></li>
      </ol>`;

    const main = document.getElementById('pd-main');
    main.classList.toggle('pd-main--no-media', !v.gallery.length);
    main.innerHTML = mainHTML(v, c);

    // 02 · description, specs, brochure (only what the record has)
    const details = document.getElementById('pd-details');
    const html = detailsHTML(v);
    if (html) { details.innerHTML = html; details.hidden = false; }

    // 03 · back to the collection
    const back = document.getElementById('pd-back');
    back.innerHTML = `<div class="wrap"><a class="link-arrow pd-back__link" href="${c.href}"><span class="link-arrow__icon" aria-hidden="true">←</span> ${esc(c.back)}</a></div>`;
    back.hidden = false;

    root.removeAttribute('aria-busy');
    gallery();
    reveal();
  })();
})();
