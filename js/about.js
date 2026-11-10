// Nikotian — «Ο Οίκος» page
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
