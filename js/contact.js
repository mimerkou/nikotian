// Nikotian — Contact page (Fine Tuning v1.0)
// «Ρωτήστε για το μοντέλο» on every product page links here as
//   contact.html?interest=<public model name>&item=<slug>#contact-form
// This script only prefills the «Μήνυμα» field and brings the form into view. It sends nothing.
// · the value goes in with .value (never as HTML);
// · text the visitor has already typed (or the browser restored) is never replaced;
// · without ?interest the field stays empty;
// · item (unique slug) is kept in a hidden field, so instruments with the same name are told apart later.

(() => {
  const form = document.getElementById('contact-form');
  const message = document.getElementById('cf-message');
  if (!form || !message) return;

  const params = new URLSearchParams(location.search);
  const interest = (params.get('interest') || '').replace(/\s+/g, ' ').trim().slice(0, 200);
  const item = (params.get('item') || '').trim().slice(0, 120);

  if (interest && message.value.trim() === '') {
    message.value = `Ενδιαφέρομαι για το ${interest}`;
  }
  if (item && !form.querySelector('input[name="product"]')) {
    const hidden = document.createElement('input');
    hidden.type = 'hidden';
    hidden.name = 'product';
    hidden.value = item;
    form.appendChild(hidden);
  }

  /* ---------- Bring the form into view once the page has settled ----------
     The browser already jumps to #contact-form while parsing. Web fonts and images can still move it a little,
     so the position is corrected once after load — unless the visitor has started scrolling by then.
     html { scroll-padding-top } keeps the start of the form clear of the fixed header. */
  if (location.hash !== '#contact-form') return;
  let userMoved = false;
  const moved = () => { userMoved = true; };
  ['wheel', 'touchstart', 'keydown', 'pointerdown'].forEach((t) => window.addEventListener(t, moved, { once: true, passive: true }));

  const align = () => {
    if (userMoved) return;
    const top = form.getBoundingClientRect().top;
    const pad = parseFloat(getComputedStyle(document.documentElement).scrollPaddingTop) || 0;
    if (Math.abs(top - pad) > 2) form.scrollIntoView({ block: 'start', behavior: 'instant' });
  };
  const fontsReady = document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve();
  const loaded = document.readyState === 'complete' ? Promise.resolve() : new Promise((r) => window.addEventListener('load', r, { once: true }));
  Promise.all([fontsReady, loaded]).then(() => requestAnimationFrame(align));
})();
