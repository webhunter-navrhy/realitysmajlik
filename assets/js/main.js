(() => {
  const $ = (s, c = document) => c.querySelector(s), $$ = (s, c = document) => [...c.querySelectorAll(s)];

  // hlavička: průhledná nad hero, po scrollu plná, při scrollu dolů se schová
  const hdr = $('.hdr'), over = hdr && hdr.dataset.over === '1';
  let lastY = 0, ticking = false;
  const onScroll = () => {
    const y = scrollY;
    if (over) { hdr.classList.toggle('hdr--over', y < innerHeight * 0.6); hdr.classList.toggle('hdr--solid', y >= innerHeight * 0.6); }
    hdr.classList.toggle('hdr--hide', y > 500 && y > lastY + 4 && !document.body.classList.contains('nav-open'));
    if (y < lastY - 4 || y < 500) hdr.classList.remove('hdr--hide');
    lastY = y; ticking = false;
  };
  addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
  onScroll();

  // mobilní menu
  const burger = $('.burger');
  burger && burger.addEventListener('click', () => {
    const open = document.body.classList.toggle('nav-open');
    burger.setAttribute('aria-expanded', open); $('.mnav').setAttribute('aria-hidden', !open);
    document.documentElement.style.overflow = open ? 'hidden' : '';
  });
  $$('.mnav a').forEach(a => a.addEventListener('click', () => { document.body.classList.remove('nav-open'); document.documentElement.style.overflow = ''; }));

  // reveal + počítadla
  const io = new IntersectionObserver(es => es.forEach(e => {
    if (!e.isIntersecting) return;
    e.target.classList.add('in'); io.unobserve(e.target);
  }), { rootMargin: '0px 0px -8% 0px', threshold: .08 });
  $$('.rv,.rv-clip').forEach(el => io.observe(el));

  const cio = new IntersectionObserver(es => es.forEach(e => {
    if (!e.isIntersecting) return; cio.unobserve(e.target);
    const el = e.target, to = +el.dataset.countTo, from = el.hasAttribute('data-plain') ? to - 19 : 0, t0 = performance.now(), dur = 1600;
    const step = t => { const p = Math.min(1, (t - t0) / dur), k = 1 - Math.pow(1 - p, 4); el.textContent = Math.round(from + (to - from) * k); if (p < 1) requestAnimationFrame(step); };
    requestAnimationFrame(step);
  }), { threshold: .5 });
  $$('[data-count-to]').forEach(el => cio.observe(el));

  // vyhledávání v hero
  const finder = $('[data-finder]');
  if (finder) {
    const upd = () => {
      const f = new FormData(finder), deal = f.get('deal'), type = f.get('type'), br = f.get('branch');
      const n = (window.SMAJ || []).filter(x => x[0] === deal && (!type || x[1] === type) && (!br || x[2] === br)).length;
      $('[data-count]', finder).textContent = n;
    };
    $$('.seg button', finder).forEach(b => b.addEventListener('click', () => {
      $$('.seg button', finder).forEach(x => x.setAttribute('aria-pressed', x === b));
      finder.deal.value = b.dataset.deal; upd();
    }));
    finder.addEventListener('change', upd);
    finder.addEventListener('submit', e => {
      e.preventDefault();
      const p = new URLSearchParams(); new FormData(finder).forEach((v, k) => v && p.set(k, v));
      location.href = finder.getAttribute('action') + '?' + p;
    });
  }

  // záložky s nabídkou na úvodu
  $$('.tabs [data-tab]').forEach(b => b.addEventListener('click', () => {
    $$('.tabs [data-tab]').forEach(x => x.setAttribute('aria-selected', x === b));
    $$('[data-rail]').forEach(r => { r.hidden = r.dataset.rail !== b.dataset.tab; if (!r.hidden) r.scrollLeft = 0; });
  }));
  const rail = () => $$('[data-rail]').find(r => !r.hidden);
  const railBy = d => { const r = rail(); if (r) r.scrollBy({ left: d * (r.firstElementChild.offsetWidth + 22), behavior: 'smooth' }); };
  $('[data-rail-prev]') && $('[data-rail-prev]').addEventListener('click', () => railBy(-1));
  $('[data-rail-next]') && $('[data-rail-next]').addEventListener('click', () => railBy(1));

  // náhled fotky u řádků služeb
  const pv = $('.preview');
  const rows = $$('.route[data-img]');
  if (pv && rows.length && matchMedia('(hover:hover)').matches) {
    const base = (document.querySelector('link[rel=stylesheet][href*="style.css"]').getAttribute('href').split('assets/')[0]);
    rows.forEach((r, i) => { const im = new Image(); im.src = base + r.dataset.img; im.alt = ''; im.dataset.i = i; pv.appendChild(im); });
    let x = 0, y = 0, cx = 0, cy = 0, raf = 0, on = false;
    const loop = () => { cx += (x - cx) * .16; cy += (y - cy) * .16; pv.style.left = cx + 'px'; pv.style.top = cy + 'px'; if (on || Math.abs(x - cx) > .5) raf = requestAnimationFrame(loop); else raf = 0; };
    rows.forEach((r, i) => {
      r.addEventListener('mouseenter', e => { on = true; x = cx = e.clientX + 170; y = cy = e.clientY; pv.classList.add('on'); $$('img', pv).forEach(im => im.classList.toggle('on', +im.dataset.i === i)); if (!raf) raf = requestAnimationFrame(loop); });
      r.addEventListener('mousemove', e => { x = e.clientX + 170; y = e.clientY; if (!raf) raf = requestAnimationFrame(loop); });
      r.addEventListener('mouseleave', () => { on = false; pv.classList.remove('on'); });
    });
  }

  // filtr nabídky
  const grid = $('[data-grid]');
  if (grid) {
    const cards = $$('.card[data-deal]', grid), st = { deal: '', branch: '', type: '', q: '', sort: 'new' };
    const qs = new URLSearchParams(location.search);
    ['deal', 'branch', 'type'].forEach(k => { if (qs.get(k)) st[k] = qs.get(k); });
    const apply = () => {
      $$('.chip[data-f]').forEach(c => c.setAttribute('aria-pressed', st[c.dataset.f] === c.dataset.v));
      let n = 0;
      const q = st.q.trim().toLowerCase();
      cards.forEach(c => {
        const ok = (!st.deal || c.dataset.deal === st.deal) && (!st.branch || c.dataset.branch === st.branch) && (!st.type || c.dataset.type === st.type) && (!q || c.dataset.text.includes(q));
        c.hidden = !ok; c.style.display = ok ? '' : 'none'; if (ok) n++;
      });
      const key = c => +c.dataset.price || (st.sort === 'cheap' ? 1e12 : -1);
      const sorted = [...cards].sort((a, b) => st.sort === 'new' ? a.dataset.order - b.dataset.order : st.sort === 'cheap' ? key(a) - key(b) : key(b) - key(a));
      const empty = $('[data-empty]'); sorted.forEach(c => grid.insertBefore(c, empty));
      $('[data-shown]').textContent = n; empty.hidden = n > 0;
      const p = new URLSearchParams(); ['deal', 'branch', 'type'].forEach(k => st[k] && p.set(k, st[k]));
      history.replaceState(null, '', location.pathname + (p.toString() ? '?' + p : ''));
    };
    $$('.chip[data-f]').forEach(c => c.addEventListener('click', () => { st[c.dataset.f] = c.dataset.v; apply(); }));
    $('[data-q]').addEventListener('input', e => { st.q = e.target.value; apply(); });
    $('[data-sort]').addEventListener('change', e => { st.sort = e.target.value; apply(); });
    apply();
  }

  // galerie + lightbox
  const gal = $('.gal[data-photos]'), lb = $('.lb');
  if (gal && lb) {
    const ph = JSON.parse(gal.dataset.photos); let i = 0;
    const show = k => { i = (k + ph.length) % ph.length; $('img', lb).src = ph[i]; $('.cnt', lb).textContent = (i + 1) + ' / ' + ph.length; };
    const open = k => { show(k); lb.classList.add('on'); document.documentElement.style.overflow = 'hidden'; };
    const close = () => { lb.classList.remove('on'); document.documentElement.style.overflow = ''; };
    $$('[data-lb]', gal).forEach(a => a.addEventListener('click', e => { e.preventDefault(); open(+a.dataset.lb); }));
    $('.x', lb).onclick = close; $('.pv', lb).onclick = () => show(i - 1); $('.nx', lb).onclick = () => show(i + 1);
    lb.addEventListener('click', e => { if (e.target === lb) close(); });
    addEventListener('keydown', e => { if (!lb.classList.contains('on')) return; if (e.key === 'Escape') close(); if (e.key === 'ArrowLeft') show(i - 1); if (e.key === 'ArrowRight') show(i + 1); });
  }

  // formuláře v návrhu -> předvyplněný e-mail
  $$('form[data-mailto]').forEach(f => f.addEventListener('submit', e => {
    e.preventDefault();
    const lines = []; new FormData(f).forEach((v, k) => v && lines.push(k + ': ' + v));
    location.href = 'mailto:' + f.dataset.mailto + '?subject=' + encodeURIComponent(f.dataset.subject) + '&body=' + encodeURIComponent(lines.join('\n'));
  }));
})();
