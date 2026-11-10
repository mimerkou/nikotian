// Nikotian — piano collections: product grid + filters (manufacturer × type)
// Shared by «Καινούργια», «Μεταχειρισμένα» and «Ηλεκτρικά πιάνα» (one rendering + filtering system).
// Data: the global named in #np-grid[data-source]; default window.NIKOTIAN_NEW_PIANOS
// (data/new-pianos.js). Used pianos: window.NIKOTIAN_USED_PIANOS (data/used-pianos.js).
// Electric pianos: window.NIKOTIAN_ELECTRIC_PIANOS (data/electric-pianos.js).
//
// Opt-in options (v1.0 Ηλεκτρικά; pages without them behave exactly as before):
//   #np-grid[data-layout="auto"] + #np-featured  → a collection with ONE record is shown as the featured
//       presentation (same record, same data); from two records on, the shared 3/2/1 grid is rendered.
//   #np-filters[data-min-items="N"]              → the filter bar appears only from N records on.
//   No type radios in #np-filters                → manufacturer filter only (types are not used).
//   #np-grid[data-noun="κιθάρα|κιθάρες"]          → the word used in the result count (v1.0 Κιθάρες;
//       default «πιάνο|πιάνα»).
//   images[0].backdrop (record)                   → the card frame takes the studio colour of the photograph,
//       which is shown whole and unblended (v1.0 Κιθάρες).
// Optional record fields (used pianos only): name, images[0].fit / .position, sameNameIndex.
// Product pages do not exist yet. A record with detailPage set gets a real link; every other record
// keeps its future URL in data-href and the shared «pending page» notice (main.js) instead of a 404.

(() => {
  const grid = document.getElementById('np-grid');
  const DATA = window[(grid && grid.dataset.source) || 'NIKOTIAN_NEW_PIANOS'];
  const form = document.getElementById('np-filters');
  if (!Array.isArray(DATA) || !grid || !form) return;

  const countEl = document.getElementById('np-count');
  const resetBtn = form.querySelector('.filters__reset');
  const empty = document.getElementById('np-empty');
  const brandSelect = form.querySelector('#np-brand');

  const pianos = [...DATA].sort((a, b) => a.order - b.order);

  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const linkAttrs = (p) => (p.detailPage
    ? `href="${esc(p.detailPage)}"`
    : `href="#" data-href="${esc(p.url)}" data-pending="${esc(p.name || `${p.manufacturer} ${p.model}`)}"`);

  /* ---------- Featured presentation: one record, shown large (data-layout="auto") ----------
     Same record as the card: primary photograph, manufacturer + model, the short presentation (summary),
     the facts marked show:true, up to three detail photographs, and the link to the model.
     Optional fields that are empty render nothing. */
  const featuredEl = document.getElementById('np-featured');
  if (grid.dataset.layout === 'auto' && featuredEl && pianos.length === 1) {
    const p = pianos[0];
    const name = p.name || `${p.manufacturer} ${p.model}`;
    const main = p.images[0];
    const details = p.images.filter((im) => im.role === 'detail').slice(0, 3);
    const text = (p.summary && p.summary.length ? p.summary : p.description || []);
    const facts = (p.specs || []).filter((f) => f.show).slice(0, 3);
    // the model name never breaks on its hyphen («SLP-|175»)
    const keep = (html) => (p.model ? html.split(esc(p.model)).join(`<span style="white-space: nowrap">${esc(p.model)}</span>`) : html);
    const img = (im, cls, extra = '') => `<img class="${cls}" src="${esc(im.src)}" alt="${esc(im.alt || '')}" width="${im.width}" height="${im.height}" decoding="async"${extra}>`;
    featuredEl.innerHTML = `
      <article class="np-feature" id="${esc(p.slug)}" aria-labelledby="t-${esc(p.slug)}" data-brand="${esc(p.manufacturerSlug)}">
        <figure class="np-feature__media frame" data-reveal>${img(main, 'np-feature__img', ' fetchpriority="high"')}</figure>
        <div class="np-feature__body" data-reveal style="--d: 120ms">
          <p class="t-meta np-feature__brand">${esc(p.manufacturer)}</p>
          <h3 class="title title--md np-feature__title" id="t-${esc(p.slug)}">${esc(p.model || name)}</h3>
          ${text.length ? `<div class="np-feature__text">${text.map((t) => `<p class="t-body">${keep(esc(t))}</p>`).join('')}</div>` : ''}
          <a class="link-arrow np-feature__more" ${linkAttrs(p)}>Ανακαλύψτε το μοντέλο<span class="visually-hidden">: ${esc(name)}</span> <span class="link-arrow__icon" aria-hidden="true">→</span></a>
        </div>
        ${details.length ? `<ul class="np-feature__details" aria-label="Λεπτομέρειες του ${esc(name)}" data-reveal style="--d: 220ms">${details.map((d) => `<li class="frame np-feature__detail">${img(d, 'np-feature__img', ' loading="lazy"')}</li>`).join('')}</ul>` : ''}
        ${facts.length ? `<dl class="np-feature__facts" data-reveal style="--d: 280ms">${facts.map((f) => `<div class="np-feature__fact"><dt class="t-meta">${esc(f.label)}</dt><dd class="t-meta-value">${esc(f.value)}</dd></div>`).join('')}</dl>` : ''}
      </article>`;
    featuredEl.hidden = false;
    grid.hidden = true;
    // rendered after main.js collected its reveal targets: observe these here (same motion)
    const parts = featuredEl.querySelectorAll('[data-reveal]');
    if ('IntersectionObserver' in window) {
      const io = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          entry.target.classList.add('is-in');
          io.unobserve(entry.target);
        });
      }, { threshold: 0.18, rootMargin: '0px 0px -6% 0px' });
      parts.forEach((el) => io.observe(el));
    } else {
      parts.forEach((el) => el.classList.add('is-in'));
    }
    return;   // one record: no grid, no filter bar
  }

  /* ---------- Options: manufacturers come from the data; types are fixed ---------- */
  const brands = [];
  pianos.forEach((p) => {
    if (!brands.some((b) => b.value === p.manufacturerSlug)) brands.push({ value: p.manufacturerSlug, label: p.manufacturer });
  });
  brands.sort((a, b) => a.label.localeCompare(b.label, 'el'));
  const BRAND_VALUES = ['all', ...brands.map((b) => b.value)];
  const TYPE_VALUES = ['all', 'upright', 'grand'];

  // Manufacturer options come from the catalogue data (the «all» option is in the markup).
  brandSelect.insertAdjacentHTML('beforeend', brands.map((b) => `<option value="${esc(b.value)}">${esc(b.label)}</option>`).join(''));

  /* ---------- Cards ---------- */
  const card = (p) => {
    const img = p.images[0];
    const name = p.name || `${p.manufacturer} ${p.model}`;
    // no model in the source (manufacturer only): the name is the title, the label line stays empty
    const title = p.model || name;
    const brand = p.model ? p.manufacturer : '';
    const media = img.fit === 'contain' ? ' np-card__media--contain' : '';
    const pos = img.position ? ` style="object-position: ${esc(img.position)}"` : '';
    const backdrop = img.backdrop ? ` np-card__media--backdrop" style="--backdrop: ${esc(img.backdrop)}` : '';
    // instruments with the same name: tell them apart for screen readers
    const same = p.sameNameIndex ? `, όργανο ${p.sameNameIndex[0]} από ${p.sameNameIndex[1]} με την ίδια ονομασία` : '';
    const live = Boolean(p.detailPage);
    const href = live ? p.detailPage : '#';
    const pending = live ? '' : ` data-href="${esc(p.url)}" data-pending="${esc(name)}"`;
    return `
      <li class="np-card" id="${esc(p.slug)}" data-brand="${esc(p.manufacturerSlug)}" data-type="${p.type || 'unknown'}">
        <article class="np-card__inner" aria-labelledby="t-${esc(p.slug)}">
          <a class="np-card__media${media}${backdrop}" href="${esc(href)}"${pending} tabindex="-1" aria-hidden="true">
            <img src="${esc(img.src)}" alt="" width="${img.width}" height="${img.height}" loading="lazy" decoding="async"${pos}>
          </a>
          <div class="np-card__body">
            <p class="t-meta np-card__brand"${brand ? '' : ' aria-hidden="true"'}>${brand ? esc(brand) : '&nbsp;'}</p>
            <h3 class="t-subtitle np-card__title" id="t-${esc(p.slug)}">${esc(title)}</h3>
            ${p.typeLabel ? `<p class="t-caption np-card__type">${esc(p.typeLabel)}</p>` : ''}
            <span class="np-card__spacer" aria-hidden="true"></span>
            <a class="link-arrow np-card__more" href="${esc(href)}"${pending}>Ανακαλύψτε το μοντέλο<span class="visually-hidden">: ${esc(name)}${same}</span> <span class="link-arrow__icon" aria-hidden="true">→</span></a>
          </div>
        </article>
      </li>`;
  };
  grid.innerHTML = pianos.map(card).join('');
  const cards = [...grid.children];

  /* ---------- State (kept in the URL: ?brand=petrof&type=upright) ---------- */
  const hasType = Boolean(form.querySelector('input[name="type"]'));
  const typeInput = (v) => form.querySelector(`input[name="type"][value="${v}"]`);
  const params = new URLSearchParams(location.search);
  const initBrand = params.get('brand');
  const initType = params.get('type');
  if (initBrand && BRAND_VALUES.includes(initBrand)) brandSelect.value = initBrand;
  if (hasType && initType && TYPE_VALUES.includes(initType)) typeInput(initType).checked = true;

  const state = () => ({
    brand: brandSelect.value,
    type: hasType ? form.querySelector('input[name="type"]:checked').value : 'all',
  });
  // A model with an undocumented type is shown under «Όλα» only.
  const match = (p, s) => (s.brand === 'all' || p.manufacturerSlug === s.brand) && (s.type === 'all' || p.type === s.type);
  const [nounOne, nounMany] = (grid.dataset.noun || 'πιάνο|πιάνα').split('|');
  const plural = (n) => (n === 1 ? nounOne : nounMany);

  const apply = (animate) => {
    const s = state();
    let shown = 0;
    cards.forEach((el, i) => {
      const ok = match(pianos[i], s);
      const was = !el.hidden;
      el.hidden = !ok;
      if (ok) {
        shown += 1;
        if (animate && !was) {
          el.classList.remove('is-entering'); void el.offsetWidth; el.classList.add('is-entering');
        }
      }
    });

    const filtered = s.brand !== 'all' || s.type !== 'all';
    countEl.textContent = filtered ? `${shown} από ${pianos.length} ${plural(pianos.length)}` : `${pianos.length} ${plural(pianos.length)}`;
    resetBtn.hidden = !filtered;
    empty.hidden = shown !== 0;
    grid.hidden = shown === 0;

    const q = new URLSearchParams();
    if (s.brand !== 'all') q.set('brand', s.brand);
    if (s.type !== 'all') q.set('type', s.type);
    const url = `${location.pathname}${q.toString() ? `?${q}` : ''}${location.hash}`;
    try { history.replaceState(null, '', url); } catch (e) { /* file:// in some browsers */ }
  };

  form.addEventListener('change', () => apply(true));
  form.addEventListener('submit', (e) => e.preventDefault());
  const resetAll = (focusTarget) => {
    brandSelect.value = 'all';
    if (hasType) typeInput('all').checked = true;
    apply(true);
    focusTarget?.focus();
  };
  // after a reset the reset button disappears: focus moves to the first control
  form.addEventListener('reset', (e) => { e.preventDefault(); resetAll(brandSelect); });
  empty.querySelector('.np-empty__reset').addEventListener('click', () => resetAll(brandSelect));

  // Filters only where they mean something (data-min-items; default: always, as before).
  const minItems = Number(form.dataset.minItems || 0);
  const filtersOn = pianos.length >= minItems && (brands.length > 1 || hasType);
  if (filtersOn) {
    form.hidden = false;
    apply(false);
  } else {
    countEl.textContent = '';
    try { if (location.search) history.replaceState(null, '', `${location.pathname}${location.hash}`); } catch (e) { /* file:// */ }
  }

  /* ---------- Reveal the cards as they enter the viewport (same motion as the shared reveal) ---------- */
  if ('IntersectionObserver' in window) {
    cards.forEach((el) => { el.setAttribute('data-reveal', ''); });
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        const el = entry.target;
        // small stagger inside a row
        const cols = getComputedStyle(grid).gridTemplateColumns.split(' ').length;
        const col = cards.filter((c) => !c.hidden).indexOf(el) % cols;
        el.style.setProperty('--d', `${Math.max(0, col) * 90}ms`);
        el.classList.add('is-in');
        io.unobserve(el);
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -4% 0px' });
    cards.forEach((el) => io.observe(el));
    // cards revealed later by a filter change must never stay invisible
    form.addEventListener('change', () => cards.forEach((el) => { if (!el.hidden) el.classList.add('is-in'); }));
  }
})();
