// Nikotian — «Ο Οίκος» page (v4: + letter reader)
// The route axis fills as the reader moves through the five stations.
// Without JS the line is simply drawn in full.

(() => {
  const list = document.querySelector('[data-route]');
  if (!list) return;

  let ticking = false;
  const update = () => {
    const rect = list.getBoundingClientRect();
    const vh = window.innerHeight;
    // 0 when the top of the list reaches 75% of the viewport, 1 when its end reaches 55%
    const start = vh * 0.75;
    const end = vh * 0.55;
    const total = rect.height + (start - end);
    const p = Math.min(1, Math.max(0, (start - rect.top) / total));
    list.style.setProperty('--progress', p.toFixed(4));
    ticking = false;
  };
  update();
  const onScroll = () => { if (!ticking) { requestAnimationFrame(update); ticking = true; } };
  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onScroll);
})();

// Letters of 1931 (v4): each archive button opens its <dialog> — the letter large, with a free translation.
// Esc closes (native), as do the close button and a click on the backdrop. Focus returns to the button.
// v4.1: no wait when the reader opens. The dialog image starts as the page thumbnail (already in cache);
// the large scan is preloaded + decoded off-screen as the letters approach the viewport (or on hover/focus),
// then swapped in while the dialog is still closed — or, if the visitor is faster, seamlessly while open.
(() => {
  const upgrade = (img) => {
    if (!img || !img.dataset.full || img.dataset.upgrading) return;
    img.dataset.upgrading = '1';
    const full = new Image();
    full.decoding = 'async';
    full.src = img.dataset.full;
    const swap = () => { img.src = full.src; delete img.dataset.full; };
    (full.decode ? full.decode() : Promise.reject()).then(swap, () => { full.onload = swap; if (full.complete) swap(); });
  };
  const readerImg = (btn) => document.getElementById(btn.dataset.letter)?.querySelector('img[data-full]');
  const buttons = [...document.querySelectorAll('.archive__open[data-letter]')];
  const archive = document.querySelector('.archive');
  if (archive && 'IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => {
      if (entries.some((e) => e.isIntersecting)) { buttons.forEach((b) => upgrade(readerImg(b))); io.disconnect(); }
    }, { rootMargin: '600px 0px' });
    io.observe(archive);
  }
  buttons.forEach((btn) => {
    ['pointerenter', 'focus', 'touchstart'].forEach((ev) => btn.addEventListener(ev, () => upgrade(readerImg(btn)), { once: true, passive: true }));
  });
})();

(() => {
  document.querySelectorAll('.archive__open[data-letter]').forEach((btn) => {
    const dlg = document.getElementById(btn.dataset.letter);
    if (!dlg || typeof dlg.showModal !== 'function') return;
    const close = () => dlg.close();
    btn.addEventListener('click', () => {
      dlg.showModal();
      document.documentElement.classList.add('has-dialog');
    });
    dlg.addEventListener('close', () => {
      document.documentElement.classList.remove('has-dialog');
      btn.focus();
    });
    dlg.querySelector('[data-close]')?.addEventListener('click', close);
    dlg.addEventListener('click', (e) => { if (e.target === dlg) close(); });
  });
})();
