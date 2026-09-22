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

  // Monospace labels type in; proportional display type resolves per character.
  const TYPE_SEL = '.eyebrow, .index, .micro-head, .m-num, .hero-foot span';
  const CHAR_SEL = '#hero-title, #contact-title, .m-body h3';
  // Prose resolves a word at a time, not a letter at a time: a sentence split
  // into ~140 inline-block spans can be read out character by character.
  const WORD_SEL = '.about-statement';
  const FADE_SEL = '[data-reveal], .section, footer, .method-list';

  const seen = new Set();
  let targets = [...document.querySelectorAll(FADE_SEL + ', ' + TYPE_SEL + ', ' + CHAR_SEL + ', ' + WORD_SEL)]
    .filter((el) => !(seen.has(el) || !seen.add(el)));

  // Type a label out one character at a time behind a block caret. The width is
  // pinned first so a growing label never nudges its neighbours.
  function typeIn(el) {
    const full = el.textContent;
    if (!full.trim()) { el.classList.add('in'); return; }
    el.style.minWidth = Math.ceil(el.getBoundingClientRect().width) + 'px';
    el.setAttribute('aria-label', full);
    el.textContent = '';
    el.classList.add('in', 'typing');
    const per = Math.min(20, 380 / full.length);
    const finish = () => {
      el.textContent = full;
      el.classList.remove('typing');
      el.removeAttribute('aria-label');
      el.style.minWidth = '';
    };
    // Driven by elapsed time rather than a chain of timers, so a dropped frame
    // catches up instead of falling behind, and a hard stop guarantees the full
    // text lands even if the tab is backgrounded mid-type.
    const start = performance.now();
    (function frame(now) {
      const n = Math.max(1, Math.min(full.length, Math.round((now - start) / per)));
      el.textContent = full.slice(0, n);
      if (n < full.length) { requestAnimationFrame(frame); return; }
      finish();
    })(start);
    setTimeout(() => { if (el.classList.contains('typing')) finish(); },
               full.length * per + 2000);
  }

  // Wrap every glyph in its own span, keeping <br>, nested spans and spaces
  // intact so nothing reflows, then let staggered CSS delays resolve them.
  function charsIn(el, byWord) {
    const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    const nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);

    const pieces = (v) => byWord ? v.split(/(\s+)/).filter(Boolean) : [...v];
    let count = 0;
    nodes.forEach((n) => { for (const p of pieces(n.nodeValue)) if (p.trim()) count++; });
    const step = count ? Math.min(byWord ? 34 : 15, 520 / count) : 0;

    let i = 0;
    nodes.forEach((node) => {
      const frag = document.createDocumentFragment();
      for (const piece of pieces(node.nodeValue)) {
        if (!piece.trim()) { frag.appendChild(document.createTextNode(piece)); continue; }
        const span = document.createElement('span');
        span.className = 'ch';
        span.textContent = piece;
        span.style.setProperty('--d', Math.round(i++ * step) + 'ms');
        frag.appendChild(span);
      }
      node.parentNode.replaceChild(frag, node);
    });

    el.classList.add('in');
    requestAnimationFrame(() => {
      el.querySelectorAll('.ch').forEach((c) => c.classList.add('on'));
    });
  }

  function play(el) {
    if (el.matches(TYPE_SEL)) typeIn(el);
    else if (el.matches(CHAR_SEL)) charsIn(el, false);
    else if (el.matches(WORD_SEL)) charsIn(el, true);
    else el.classList.add('in');
  }

  const showAll = () => { targets.forEach((el) => el.classList.add('in')); targets = []; };
  if (reduced.matches) { showAll(); return; }

  let ticking = false;
  function check() {
    ticking = false;
    const h = window.innerHeight;
    targets = targets.filter((el) => {
      const r = el.getBoundingClientRect();
      const visible = r.top < h - 60 && r.bottom > 0;
      if (visible) play(el);
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
