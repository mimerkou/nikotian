// Nikotian — Homepage final prototype
// Progressive enhancement: without JS every section is visible and every link works.

(() => {
  const root = document.documentElement;
  const header = document.querySelector('[data-header]');
  const menuToggle = document.querySelector('.menu-toggle');
  const nav = document.getElementById('site-nav');
  const subToggles = document.querySelectorAll('.nav__parent');
  const mobileQuery = window.matchMedia('(max-width: 67.5rem)');

  /* ---------- Input modality ----------
     Chrome treats a <select> (and a radio reached through its label) as «focus-visible» even after a mouse
     or touch selection, so the red focus ring stayed on the filters after every choice. html[data-input]
     records the last input type; the filters show their focus ring only for the keyboard (new-pianos.css). */
  const setInput = (type) => { if (root.dataset.input !== type) root.dataset.input = type; };
  window.addEventListener('pointerdown', () => setInput('pointer'), { capture: true, passive: true });
  window.addEventListener('keydown', (e) => { if (!e.metaKey && !e.ctrlKey && !e.altKey) setInput('keyboard'); }, { capture: true });

  /* ---------- Header: transparent over the hero, solid ivory after scroll ---------- */
  let ticking = false;
  const updateHeader = () => {
    header.classList.toggle('is-solid', window.scrollY > 24);
    ticking = false;
  };
  updateHeader();
  window.addEventListener('scroll', () => {
    if (!ticking) { requestAnimationFrame(updateHeader); ticking = true; }
  }, { passive: true });

  /* ---------- Mobile menu ---------- */
  const setMenu = (open) => {
    menuToggle.setAttribute('aria-expanded', String(open));
    menuToggle.querySelector('.menu-toggle__label').textContent = open ? 'Κλείσιμο' : 'Μενού';
    root.classList.toggle('menu-open', open);
    if (open) nav.querySelector('a, button')?.focus({ preventScroll: true });
  };
  menuToggle.addEventListener('click', () => setMenu(menuToggle.getAttribute('aria-expanded') !== 'true'));
  nav.addEventListener('click', (e) => {
    if (e.target.closest('a') && root.classList.contains('menu-open')) setMenu(false);
  });
  mobileQuery.addEventListener('change', (e) => { if (!e.matches) setMenu(false); closeSubs(); });

  // Focus order while the menu is open: toggle → menu items → back to the toggle
  document.addEventListener('keydown', (e) => {
    if (e.key !== 'Tab' || !root.classList.contains('menu-open')) return;
    const items = [...nav.querySelectorAll('a[href], button')].filter((el) => el.getClientRects().length > 0);
    const first = items[0];
    const last = items[items.length - 1];
    const active = document.activeElement;
    let next = null;
    if (!e.shiftKey && active === menuToggle) next = first;
    else if (!e.shiftKey && active === last) next = menuToggle;
    else if (e.shiftKey && active === first) next = menuToggle;
    else if (e.shiftKey && active === menuToggle) next = last;
    else if (!nav.contains(active)) next = first;
    if (next) { e.preventDefault(); next.focus(); }
  });

  /* ---------- «Πιάνα»: a category, not a page ----------
     One <button class="nav__parent"> (label + chevron) controls the submenu everywhere:
     desktop → opens on hover (with a short grace period on leave) and on click / Enter / Space / ↓;
     mobile menu → the whole row toggles the accordion. aria-expanded always matches what is shown. */
  // any-hover: a laptop with a touch screen still has a mouse/trackpad that should open the menu on hover
  const hoverDesktop = window.matchMedia('(any-hover: hover) and (min-width: 67.5625rem)');
  const setSub = (btn, open) => {
    btn.setAttribute('aria-expanded', String(open));
    btn.closest('.nav__item').classList.toggle('is-open', open);
  };
  function closeSubs(except) {
    subToggles.forEach((btn) => { if (btn !== except) setSub(btn, false); });
  }
  const subLinks = (btn) => [...document.getElementById(btn.getAttribute('aria-controls')).querySelectorAll('a')];

  subToggles.forEach((btn) => {
    const item = btn.closest('.nav__item');
    let closeTimer;
    btn.addEventListener('click', (e) => {
      clearTimeout(closeTimer);
      // desktop mouse: hover has already opened it, so a click on «Πιάνα» keeps it open (never closes it under the pointer)
      const mouseOnDesktop = e.detail > 0 && hoverDesktop.matches && item.matches(':hover');
      const open = mouseOnDesktop || btn.getAttribute('aria-expanded') !== 'true';
      closeSubs(btn);
      setSub(btn, open);
    });
    // Desktop hover (mouse/pen only; touch uses the click above)
    item.addEventListener('pointerenter', (e) => {
      if (e.pointerType === 'touch' || !hoverDesktop.matches) return;
      clearTimeout(closeTimer);
      closeSubs(btn);
      setSub(btn, true);
    });
    item.addEventListener('pointerleave', (e) => {
      if (e.pointerType === 'touch' || !hoverDesktop.matches) return;
      if (item.contains(document.activeElement) && document.activeElement !== btn) return;   // keyboard is inside
      clearTimeout(closeTimer);
      closeTimer = setTimeout(() => setSub(btn, false), 160);
    });
    // Keyboard: ↓ opens and moves to the first option; ↑ / ↓ move between options; Home / End
    btn.addEventListener('keydown', (e) => {
      if (e.key !== 'ArrowDown' && e.key !== 'ArrowUp') return;
      e.preventDefault();
      closeSubs(btn);
      setSub(btn, true);
      const links = subLinks(btn);
      (e.key === 'ArrowDown' ? links[0] : links[links.length - 1])?.focus();
    });
    document.getElementById(btn.getAttribute('aria-controls')).addEventListener('keydown', (e) => {
      const links = subLinks(btn);
      const i = links.indexOf(document.activeElement);
      let next = null;
      if (e.key === 'ArrowDown') next = links[(i + 1) % links.length];
      else if (e.key === 'ArrowUp') next = i <= 0 ? btn : links[i - 1];
      else if (e.key === 'Home') next = links[0];
      else if (e.key === 'End') next = links[links.length - 1];
      if (next) { e.preventDefault(); next.focus(); }
    });
  });
  document.addEventListener('click', (e) => {
    if (!mobileQuery.matches && !e.target.closest('.nav__item--has-sub')) closeSubs();
  });
  document.querySelectorAll('.nav__item--has-sub').forEach((item) => {
    item.addEventListener('focusout', (e) => {
      if (!mobileQuery.matches && e.relatedTarget && !item.contains(e.relatedTarget)) closeSubs();
    });
  });
  document.addEventListener('keydown', (e) => {
    if (e.key !== 'Escape') return;
    const openSub = document.querySelector('.nav__parent[aria-expanded="true"]');
    if (openSub) { closeSubs(); openSub.focus(); return; }
    if (root.classList.contains('menu-open')) { setMenu(false); menuToggle.focus(); }
  });
  // pages restored from the back/forward cache come back with every submenu closed
  window.addEventListener('pageshow', (e) => { if (e.persisted) closeSubs(); });

  /* ---------- Pages that do not exist yet ----------
     Links carry the future URL in data-href and keep an in-page anchor as href.
     A short notice says the page is on its way; the anchor still scrolls to the relevant section. */
  const toast = document.querySelector('[data-toast]');
  let toastTimer;
  document.addEventListener('click', (e) => {
    const link = e.target.closest('a[data-pending]');
    if (!link || !toast) return;
    if (link.getAttribute('href') === '#') e.preventDefault();
    toast.textContent = `Η σελίδα «${link.dataset.pending}» θα είναι διαθέσιμη στο τελικό website.`;
    toast.classList.add('is-visible');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove('is-visible'), 3200);
  });

  /* ---------- Smooth scroll to sections (Navigation Motion Hotfix v1.3) ----------
     Same-page anchors only (#oikos, #pianos, #top … and page.html#id on that same page): the page glides
     from where the visitor is to the section, with requestAnimationFrame and an ease-in-out curve — no jump first.
     · duration follows the distance: ~400 ms for short hops, up to 850 ms for long ones;
     · lands under the fixed header (html scroll-padding-top + the target's own scroll-margin-top);
     · the URL gets the #hash (pushState), so Back / Forward step through the sections as usual;
     · a wheel, touch or key press during the glide hands control back to the visitor at once;
     · not handled here: other pages, ?query links, external links, href="#" placeholders, the skip link
       (it must move keyboard focus at once), and clicks with a modifier key (new tab / window). */
  const scrollEase = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);   // easeInOutCubic
  let glide = 0;
  const stopGlide = () => { if (glide) { cancelAnimationFrame(glide); glide = 0; } };
  ['wheel', 'touchstart', 'keydown'].forEach((t) => window.addEventListener(t, stopGlide, { passive: true }));

  const sectionTop = (target) => {
    const pad = parseFloat(getComputedStyle(root).scrollPaddingTop) || 0;
    const margin = parseFloat(getComputedStyle(target).scrollMarginTop) || 0;
    const y = target.getBoundingClientRect().top + window.scrollY - pad - margin;
    const max = document.documentElement.scrollHeight - window.innerHeight;
    return Math.max(0, Math.min(Math.round(y), max));
  };
  const glideTo = (target) => {
    stopGlide();
    const from = window.scrollY;
    const to = sectionTop(target);
    const distance = Math.abs(to - from);
    if (distance < 2) return;
    const duration = Math.min(850, Math.max(380, 250 + Math.sqrt(distance) * 14));
    // Time is counted frame by frame, each frame worth at most 34 ms: if the browser is briefly busy
    // (an image decoding, a hero animation), the glide waits for it instead of jumping ahead.
    let elapsed = 0;
    let last = null;
    const step = (now) => {
      elapsed += last === null ? 0 : Math.min(now - last, 34);
      last = now;
      const t = Math.min(1, elapsed / duration);
      window.scrollTo(0, from + (to - from) * scrollEase(t));
      if (t < 1) { glide = requestAnimationFrame(step); return; }
      glide = 0;
      // late layout (fonts, images) can move the section a little while gliding: settle on its final place
      const end = sectionTop(target);
      if (Math.abs(end - window.scrollY) > 1) window.scrollTo(0, end);
    };
    glide = requestAnimationFrame(step);
  };

  document.addEventListener('click', (e) => {
    if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    const link = e.target.closest('a[href*="#"]');
    if (!link || link.classList.contains('skip-link') || link.target === '_blank') return;
    const raw = link.getAttribute('href');
    if (raw === '#' || link.hasAttribute('data-pending')) return;
    const url = new URL(link.href, location.href);
    if (url.origin !== location.origin || url.pathname !== location.pathname || url.search !== location.search) return;
    let id;
    try { id = decodeURIComponent(url.hash.slice(1)); } catch (err) { return; }
    const target = id && document.getElementById(id);
    if (!target) return;
    e.preventDefault();
    if (location.hash !== url.hash) {
      try { history.pushState(null, '', url.hash); } catch (err) { /* file:// in some browsers: no URL update */ }
    }
    glideTo(target);
  });

  /* ---------- Reveals ---------- */
  const targets = document.querySelectorAll('[data-reveal], [data-timeline]');
  if (!('IntersectionObserver' in window)) {
    targets.forEach((el) => el.classList.add('is-in'));
  } else {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-in');
        io.unobserve(entry.target);
      });
    }, { threshold: 0.18, rootMargin: '0px 0px -6% 0px' });
    targets.forEach((el) => io.observe(el));

    /* Safety net (Fine Tuning v1.0): a block that is jumped over — a fast fling, End, an #anchor or a
       link straight to the contact form — never crosses the viewport, so the observer never sees it.
       Anything already above the viewport is shown at once; nothing stays invisible because a motion
       did not run. Covers blocks added later by the page scripts (cards, product sections) as well. */
    let netTimer;
    const revealPassed = () => {
      document.querySelectorAll('.js [data-reveal]:not(.is-in), .js [data-timeline]:not(.is-in)').forEach((el) => {
        if (el.getBoundingClientRect().bottom <= 0) el.classList.add('is-in');
      });
    };
    window.addEventListener('scroll', () => { clearTimeout(netTimer); netTimer = setTimeout(revealPassed, 120); }, { passive: true });
    window.addEventListener('load', revealPassed);
    window.addEventListener('hashchange', revealPassed);
  }
})();
