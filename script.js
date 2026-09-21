(() => {
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  const art = document.querySelector('.hero-art img');
  let pending = false;
  function update() {
    pending = false;
    const offset = reduced.matches ? 0 : Math.min(window.scrollY * 0.045, 42);
    art.style.transform = `translateY(${offset}px) rotate(-12deg)`;
  }
  window.addEventListener('scroll', () => {
    if (!pending && window.scrollY < 1400) { pending = true; requestAnimationFrame(update); }
  }, { passive: true });
  reduced.addEventListener('change', update);
})();

(() => {
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  let targets = [...document.querySelectorAll('[data-reveal], .section, footer, .method-list')];
  const showAll = () => { targets.forEach((el) => el.classList.add('in')); targets = []; };

  if (reduced.matches) { showAll(); return; }

  let ticking = false;
  function check() {
    ticking = false;
    const h = window.innerHeight;
    targets = targets.filter((el) => {
      const r = el.getBoundingClientRect();
      const visible = r.top < h * 0.92 && r.bottom > 0;
      if (visible) el.classList.add('in');
      return !visible;
    });
    if (!targets.length) {
      window.removeEventListener('scroll', request);
      window.removeEventListener('resize', request);
    }
  }
  function request() { if (!ticking) { ticking = true; requestAnimationFrame(check); } }

  window.addEventListener('scroll', request, { passive: true });
  window.addEventListener('resize', request, { passive: true });
  window.addEventListener('load', check);
  window.addEventListener('pageshow', check);
  reduced.addEventListener('change', (e) => { if (e.matches) showAll(); });
  check();
})();
