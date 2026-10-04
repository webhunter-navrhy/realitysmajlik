"""Sestaví návrh webu Reality Smajlík z _data/*.json do kořene repozitáře.
Spuštění: python3 _build/build.py
"""
import hashlib, html, json, os, re, shutil
from urllib.parse import quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = lambda n: json.load(open(f'{ROOT}/_data/{n}.json', encoding='utf-8'))
SITE, BR, TEAM, SV, REV, LOC = D('site'), D('branches'), D('team'), D('services'), D('reviews'), D('localities')
L = D('listings')
E = lambda s: html.escape(str(s or ''), quote=True)

def ver(p):
    return hashlib.md5(open(f'{ROOT}/{p}', 'rb').read()).hexdigest()[:8]
CSS_V, JS_V = ver('assets/css/style.css'), ver('assets/js/main.js')

TYPES = {'byty': 'Byty', 'domy': 'Domy', 'rekreace': 'Chaty a chalupy', 'pozemky': 'Pozemky', 'komerce': 'Komerční', 'garaze': 'Garáže'}
BRN = {'cheb': 'Chebsko', 'plzen': 'Plzeňsko', 'praha': 'Praha'}
STATUS = {'novinka': 'Novinka', 'doporučujeme': 'Doporučujeme', 'sleva': 'Sleva', 'rezervováno': 'Rezervováno'}
SLUG = lambda s: re.sub(r'[^a-z]', '', s.lower().translate(str.maketrans('áčďéěíňóřšťúůýž', 'acdeeinorstuuyz')))

I = {
 'arrow': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
 'left': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M19 12H5M11 6l-6 6 6 6"/></svg>',
 'pin': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M12 21s-7-6.2-7-11.5A7 7 0 0 1 19 9.5C19 14.8 12 21 12 21Z"/><circle cx="12" cy="9.5" r="2.5"/></svg>',
 'area': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/></svg>',
 'check': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>',
 'house': '<svg viewBox="0 0 40 40" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M5 35V19L20 6l6 5V7h4v8l5 4M5 35h30"/></svg>',
 'tag': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 12V4h8l10 10-8 8L3 12Z"/><circle cx="7.5" cy="8" r="1.4"/></svg>',
}
HOUSE_BIG = '<svg class="house-bg" viewBox="0 0 400 300" aria-hidden="true"><path d="M30 292V140L180 18l62 50V34h34v62l70 58M30 292h360"/><path d="M60 292V156L180 58l130 106v128"/></svg>'
SMILE = '<svg class="smile" viewBox="0 0 100 30" preserveAspectRatio="none" aria-hidden="true"><path pathLength="1" d="M4 8 Q50 40 96 8"/><circle cx="4" cy="3" r="2.6"/><circle cx="96" cy="3" r="2.6"/></svg>'

def initials(n):
    n = re.sub(r'^(Bc\.|Ing\.|Mgr\.)\s*', '', n); n = re.sub(r'\(.*?\)\s*', '', n)
    return ''.join(w[0] for w in n.split()[:2])

def img(r, p, kind='t'):
    return f'{r}assets/img/{kind}/{p["id"]}.webp'

def count(**kw):
    return sum(1 for x in L if all(x[k] == v for k, v in kw.items()))

# ------------------------------------------------------------------ layout
def head(title, r, desc=''):
    return f'''<!DOCTYPE html>
<html lang="cs"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>{E(title)}</title>
<meta name="description" content="{E(desc or 'Reality Smajlík – realitní kancelář s pobočkami v Praze, Plzni a Chebu. Prodej a pronájem bytů, domů, pozemků a komerčních prostor.')}">
<meta name="theme-color" content="#0F2818">
<link rel="icon" href="{r}assets/img/favicon.ico">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght,SOFT@0,9..144,300..600,0..100;1,9..144,300..600,0..100&family=Manrope:wght@300..700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{r}assets/css/style.css?v={CSS_V}">
</head>'''

NAV = [('nabidka.html', 'Nabídka'), ('prodat.html', 'Prodávající'), ('lokality.html', 'Lokality Cheb'), ('o-nas.html', 'O nás'), ('kontakt.html', 'Kontakt')]

def header(r, active, over):
    links = ''.join(f'<a href="{r}{h}"{" aria-current=page" if h == active else ""}>{t}</a>' for h, t in NAV)
    return f'''<a class="skip" href="#main">Přeskočit na obsah</a>
<header class="hdr{' hdr--over' if over else ' hdr--solid'}" data-over="{1 if over else 0}"><div class="wrap">
<a class="hdr__logo" href="{r}index.html" aria-label="Reality Smajlík – úvod"><img class="l-dark" src="{r}brand/logo.svg" alt="Reality Smajlík"><img class="l-light" src="{r}brand/logo-dark.svg" alt="" aria-hidden="true"></a>
<nav class="hdr__nav" aria-label="Hlavní menu">{links}<a class="btn btn--orange" href="{r}prodat.html#formular">Chci prodat</a></nav>
<button class="burger" aria-label="Menu" aria-expanded="false"><span></span><span></span></button>
</div></header>
<div class="mnav" aria-hidden="true">{''.join(f'<a class="big" href="{r}{h}">{t}</a>' for h, t in NAV)}<a class="big" href="{r}prodat.html#formular" style="color:var(--orange)">Chci prodat</a>
<small>{E(SITE['company'])} · {SITE['phones'][1]} · {SITE['email']}<br>Praha · Plzeň · Cheb</small></div>'''

def footer(r):
    br = ''.join(f'<li><b style="color:#fff">{b["city"]}</b><br>{b["address"]}, {b["zip"]}</li>' for b in BR)
    return f'''<footer class="ftr"><div class="wrap">
<div class="ftr__top">
<div><img class="ftr__logo" src="{r}brand/logo-light.svg" alt="Reality Smajlík"><p class="ftr__claim">{SITE['claim']}</p><p style="margin-top:1rem">Realitní kancelář, která pomáhá s bydlením od roku {SITE['since']}.</p></div>
<div><h4>Pobočky</h4><ul>{br}</ul></div>
<div><h4>Nabídka</h4><ul><li><a href="{r}nabidka.html?deal=prodej">Prodej</a></li><li><a href="{r}nabidka.html?deal=pronajem">Pronájem</a></li><li><a href="{r}nabidka.html?type=byty">Byty</a></li><li><a href="{r}nabidka.html?type=domy">Domy</a></li><li><a href="{r}nabidka.html?type=pozemky">Pozemky</a></li><li><a href="{r}prodat.html">Chci prodat</a></li><li><a href="{r}prodat.html#penb">Energetické průkazy</a></li><li><a href="{r}o-nas.html#kariera">Kariéra</a></li></ul></div>
<div><h4>Kontakt</h4><ul><li><a href="tel:{SITE['phones'][1].replace(' ', '')}">{SITE['phones'][1]}</a></li><li><a href="tel:{SITE['phones'][0].replace(' ', '')}">{SITE['phones'][0]}</a></li><li><a href="mailto:{SITE['email']}">{SITE['email']}</a></li><li style="margin-top:.6rem">{E(SITE['company'])}<br>IČ: {SITE['ico']}<br>{SITE['address']}</li></ul></div>
</div>
<div class="ftr__bottom"><span>© 2026 {E(SITE['company'])} – všechna práva vyhrazena</span><span><a href="{r}o-nas.html#odstoupeni">Odstoupení od smlouvy</a> · <a href="{r}kontakt.html">Ochrana osobních údajů</a></span></div>
</div></footer>
<div class="preview" aria-hidden="true"></div>
<script src="{r}assets/js/main.js?v={JS_V}" defer></script>
</body></html>'''

def page(fn, title, body, r='', active='', over=False, desc=''):
    out = head(title, r, desc) + f'\n<body class="{"has-over" if over else ""}"><div class="grain"></div>' + header(r, active, over) + f'<main id="main">{body}</main>' + footer(r)
    p = f'{ROOT}/{fn}'; os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w', encoding='utf-8').write(out)

# ------------------------------------------------------------------ komponenty
def card(x, r='', cls='', attrs=False):
    ph = x['photos'][0] if x['photos'] else None
    im = f'<img src="{img(r, ph)}" alt="{E(x["title"])}" loading="lazy" width="720" height="480">' if ph else f'<div class="noimg">{I["house"]}</div>'
    bd = ''.join(f'<span class="badge badge--{SLUG(s)}">{STATUS.get(s, s)}</span>' for s in x['status'])
    bd += f'<span class="badge badge--deal">{"Pronájem" if x["deal"] == "pronajem" else "Prodej"}</span>'
    unit = f'<small>{E(x["price_unit"])}</small>' if x['price_unit'] else ''
    area = f'<span>{I["area"]}{E(x["area"])}</span>' if x['area'] else ''
    data = ''
    if attrs:
        data = (f' data-deal="{x["deal"]}" data-type="{x["type"]}" data-branch="{x["branch"]}" data-price="{x["price_num"] or 0}"'
                f' data-order="{x["order"]}" data-text="{E((x["title"] + " " + x["locality"] + " " + x["category"]).lower())}"')
    res = ' card--res' if 'rezervováno' in x['status'] else ''
    return (f'<a class="card{res} {cls}" href="{r}nemovitost/{x["slug"]}.html"{data}><div class="card__img">{im}<div class="badges">{bd}</div></div>'
            f'<div class="card__body"><div class="card__price">{E(x["price"])}{unit}</div><h3 class="card__title">{E(x["title"])}</h3>'
            f'<div class="card__meta"><span>{I["pin"]}{E(x["town"])}</span>{area}</div></div></a>')

def person(k, big=False):
    t = TEAM[k]
    return (f'<li class="person"><span class="ava">{initials(t["name"])}</span><div><b>{E(t["name"])}</b>{E(t["role"])}<br>'
            f'<a href="tel:{t["phone"].replace(" ", "")}">{t["phone"]}</a> · <a href="mailto:{t["email"]}">{t["email"]}</a></div></li>')

def branch_card(b, r=''):
    n = count(branch=b['id'])
    cnt = f'<a class="link" href="{r}nabidka.html?branch={b["id"]}">{n} nemovitostí v nabídce {I["arrow"]}</a>' if n else '<span class="count">Napište nám, co v Praze hledáte</span>'
    q = quote(f'{b["address"]}, {b["zip"]}')
    top = (f'<div class="branch__img"><img src="{r}assets/img/s/{b["img"]}.webp" alt="" loading="lazy"><span class="branch__city">{b["city"]}</span></div>' if b['img'] else
           f'<div class="branch__img branch__img--brand">' + HOUSE_BIG.replace('house-bg', 'house-mini') + f'<span class="branch__city">{b["city"]}</span></div>')
    return (f'<article class="branch rv">{top}'
            f'<div class="branch__body"><p class="branch__addr">{b["address"]}<small>{b["zip"]}{" · " + b["note"] if b.get("note") else ""}</small></p>'
            f'<ul class="people">{"".join(person(k) for k in b["team"])}</ul>'
            f'<div class="branch__foot">{cnt}<a class="link" href="https://mapy.cz/zakladni?q={q}" target="_blank" rel="noopener">Mapa</a></div></div></article>')

def checks(items):
    return '<ul class="checks">' + ''.join(f'<li>{I["check"]}<span>{E(i)}</span></li>' for i in items) + '</ul>'

def mailform(to, subject, fields_html, btn='Odeslat poptávku'):
    return f'<form class="form" data-mailto="{to}" data-subject="{E(subject)}">{fields_html}<div class="full"><button class="btn btn--green" type="submit">{btn} {I["arrow"]}</button></div><p class="full note">Formulář v návrhu otevře e-mail s vyplněnými údaji. Na ostrém webu se poptávka odešle rovnou do kanceláře.</p></form>'

# ------------------------------------------------------------------ úvod
def build_index():
    hero_l = next(x for x in L if any(p['id'] == '47191' for p in x['photos']))
    sel = {'doporucujeme': [x for x in L if 'doporučujeme' in x['status']],
           'novinky': [x for x in L if 'novinka' in x['status']],
           'zlevnene': [x for x in L if 'sleva' in x['status']]}
    names = {'doporucujeme': 'Doporučujeme', 'novinky': 'Novinky', 'zlevnene': 'Zlevněné'}
    tabs = ''.join(f'<button role="tab" aria-selected="{"true" if i == 0 else "false"}" data-tab="{k}">{names[k]}<sup>{len(v)}</sup></button>' for i, (k, v) in enumerate(sel.items()))
    rails = ''.join(f'<div class="rail" data-rail="{k}"{"" if i == 0 else " hidden"}>{"".join(card(x) for x in v)}</div>' for i, (k, v) in enumerate(sel.items()))
    opts_type = ''.join(f'<option value="{k}">{v}</option>' for k, v in TYPES.items())
    opts_br = ''.join(f'<option value="{k}">{v}</option>' for k, v in BRN.items() if count(branch=k))
    marq = ['Cheb', '<i>Plzeň</i>', 'Praha', 'Prodej', '<i>Pronájem</i>', 'Privatizace bytů', '<i>Energetické průkazy</i>', 'Znalecký odhad zdarma', '<i>Advokát zdarma</i>', f'Od roku {SITE["since"]}']
    mi = ''.join(f'<span class="marquee__item">{m}{I["house"]}</span>' for m in marq)
    routes = ''.join(f'<a class="route rv" href="{r["href"]}" data-img="assets/img/s/{r["img"]}.webp"><span class="route__n">{i:02d}</span><div><span class="route__k">{r["k"]}</span><h3>{r["t"]}</h3></div><p>{r["d"]}</p><span class="route__arrow">{I["arrow"]}</span></a>' for i, r in enumerate(SV['routes'], 1))
    big = next(q for q in REV if q.get('big'))
    small = [q for q in REV if not q.get('big')][:3]
    n_all, n_sale, n_rent = len(L), count(deal='prodej'), count(deal='pronajem')
    body = f'''
<section class="hero">
 <div class="hero__img"><img src="assets/img/s/hero.webp" alt="Rodinný dům se zahradou ve Františkových Lázních z nabídky Reality Smajlík" fetchpriority="high"></div>
 <div class="hero__inner">
  <div>
   <span class="eyebrow hero__eyebrow">Realitní kancelář · Praha · Plzeň · Cheb</span>
   <h1><span class="w"><span class="thin" style="animation-delay:.25s">…u&nbsp;nás</span></span> <span class="w"><span style="animation-delay:.37s"><em>koupíte</em></span></span><br><span class="w" style="overflow:visible"><span class="smile-word" style="animation-delay:.5s">domov{SMILE}</span></span></h1>
   <p class="hero__sub">Prodáváme, pronajímáme a pomáháme s bydlením od roku {SITE['since']}. Osobně, poctivě a s makléřem po Vašem boku od nacenění až po přepis energií.</p>
   <div class="hero__actions"><a class="btn btn--orange" href="nabidka.html">Prohlédnout nabídku {I['arrow']}</a><a class="btn btn--light" href="prodat.html">Chci prodat nemovitost</a></div>
  </div>
  <a class="hero__card" href="nemovitost/{hero_l['slug']}.html"><img src="{img('', hero_l['photos'][1] if len(hero_l['photos']) > 1 else hero_l['photos'][0])}" alt=""><span><small>Na fotografii</small><b>{E(hero_l['price'])}</b>{E(hero_l['title'][:62])}…</span></a>
 </div>
 <span class="scroll-ind" aria-hidden="true"></span>
</section>

<div class="finder"><div class="wrap"><form class="finder__box" action="nabidka.html" data-finder>
 <div class="seg" role="group" aria-label="Druh nabídky"><button type="button" aria-pressed="true" data-deal="prodej">Koupit</button><button type="button" aria-pressed="false" data-deal="pronajem">Pronajmout</button></div>
 <input type="hidden" name="deal" value="prodej">
 <div class="field"><label for="f-type">Co hledáte</label><select id="f-type" name="type"><option value="">Všechny typy</option>{opts_type}</select></div>
 <div class="field"><label for="f-br">Oblast</label><select id="f-br" name="branch"><option value="">Všechny pobočky</option>{opts_br}</select></div>
 <button class="btn btn--green" type="submit"><span>Zobrazit <span data-count>{n_sale}</span> nemovitostí</span> {I['arrow']}</button>
</form></div></div>
<script>window.SMAJ={json.dumps([[x['deal'], x['type'], x['branch']] for x in L])}</script>

<section class="marquee" aria-hidden="true"><div class="marquee__track">{mi}{mi}</div></section>

<section class="sec"><div class="wrap">
 <div class="sec-head"><div><span class="eyebrow">Aktuální nabídka</span><h2 class="rv">Vybrali jsme <em>pro Vás</em></h2></div>
 <div class="sec-tools"><div class="tabs" role="tablist">{tabs}</div><div class="rail-nav"><button data-rail-prev aria-label="Předchozí">{I['left']}</button><button data-rail-next aria-label="Další">{I['arrow']}</button></div></div></div>
 {rails}
 <p style="margin-top:2rem"><a class="link" href="nabidka.html">Celá nabídka – {n_all} nemovitostí {I['arrow']}</a></p>
</div></section>

<section class="sec" style="padding-top:0"><div class="wrap">
 <div class="sec-head"><div><span class="eyebrow">S čím přicházíte</span><h2 class="rv">Jedna kancelář, <em>celé</em> bydlení</h2></div><p class="lede">Ať prodáváte, kupujete, nebo jen potřebujete energetický průkaz – postaráme se o to celé, osobně a bez starostí.</p></div>
 <div class="routes">{routes}</div>
</div></section>

<section class="sec dark">{HOUSE_BIG}<div class="wrap">
 <div class="stats-top"><div><span class="eyebrow">Reality Smajlík</span><h2 class="rv" style="margin-top:1rem">Pomáháme s bydlením <em>od roku {SITE['since']}</em></h2></div>
 <p class="lede rv d1">Tým zkušených makléřů s profesionálním a individuálním přístupem. Pomáháme prodávajícím i kupujícím šetřit peníze a čas – a jejich spokojenost je naší nejlepší referencí.</p></div>
 <div class="stats">
  <div class="stat rv"><div class="stat__n" data-count-to="{SITE['since']}" data-plain>{SITE['since']}</div><p>rok, od kterého řešíme bydlení s našimi klienty</p></div>
  <div class="stat rv d1"><div class="stat__n" data-count-to="3">3</div><p>pobočky – Praha, Plzeň a Cheb</p></div>
  <div class="stat rv d2"><div class="stat__n" data-count-to="{n_sale}">{n_sale}</div><p>nemovitostí právě na prodej</p></div>
  <div class="stat rv d3"><div class="stat__n" data-count-to="{n_rent}">{n_rent}</div><p>nemovitostí k pronájmu</p></div>
 </div>
 <div class="perks">{''.join(f'<span class="perk">{I["check"]}{E(p)}</span>' for p in SITE['perks'])}</div>
</div></section>

<section class="sec"><div class="wrap sticky-split">
 <figure class="sticky-media rv-clip"><img src="assets/img/s/vila.webp" alt="Vila ve Františkových Lázních z nabídky Reality Smajlík" loading="lazy"><figcaption><b>Od nacenění po předání klíčů</b>Makléř je u všech jednání potřebných k prodeji či pronájmu Vaší nemovitosti.</figcaption></figure>
 <div>
  <span class="eyebrow">Služby v našem podání</span>
  <h2 class="rv" style="margin-top:1rem">Prodat <em>rychle</em> a bez starostí</h2>
  <ol class="steps">{''.join(f'<li class="rv">{E(s[0].upper() + s[1:])}</li>' for s in SV['included'])}</ol>
  <div class="excl rv"><h3>Při výhradním zastoupení navíc</h3><ul>{''.join(f'<li>{I["check"]}<span>{E(s)}</span></li>' for s in SV['exclusive'])}</ul><p class="portals">Inzerujeme na serverech {", ".join(SITE['portals'])} a mnoha dalších.</p></div>
  <p style="margin-top:2rem"><a class="btn btn--green" href="prodat.html#formular">Domluvit nezávaznou schůzku {I['arrow']}</a></p>
 </div>
</div></section>

<section class="sec" style="background:var(--bg-alt)"><div class="wrap">
 <span class="eyebrow">Reference</span>
 <blockquote style="margin-top:3.5rem"><p class="quote-big rv">{E(big['q'])}</p><p class="quote-src">— z reference spokojeného klienta</p></blockquote>
 <div class="quotes">{''.join(f'<figure class="q rv d{i}"><p>„{E(q["q"])}“</p><cite>{E(q["a"])}</cite></figure>' for i, q in enumerate(small))}</div>
 <p style="margin-top:2.4rem"><a class="link" href="o-nas.html#reference">Všechny reference {I['arrow']}</a></p>
</div></section>

<section class="sec"><div class="wrap">
 <div class="sec-head"><div><span class="eyebrow">Pobočky</span><h2 class="rv">Jsme <em>blízko</em> – v&nbsp;Praze, Plzni i&nbsp;Chebu</h2></div><p class="lede">Zastavte se osobně, nebo napište přímo makléřce, která má Vaši oblast na starost.</p></div>
 <div class="branches">{''.join(branch_card(b) for b in BR)}</div>
</div></section>

<section class="sec" style="padding-top:0"><div class="wrap loc-split">
 <div><span class="eyebrow">Průvodce</span><h2 class="rv" style="margin-top:1rem">{LOC['title']}</h2><p class="lede" style="margin-top:1.2rem">Přehled nejžádanějších lokalit – kde je klid, kde škola za rohem a kde se byty nejlépe pronajímají.</p><p style="margin-top:1.8rem"><a class="btn btn--ghost" href="lokality.html">Číst průvodce {I['arrow']}</a></p></div>
 <div class="loc-list rv">{''.join(f'<a href="lokality.html#{SLUG(n)}">{n}</a>' for n, *_ in LOC['items'])}</div>
</div></section>

<section class="wrap"><div class="cta rv">
 <svg class="smile-deco" viewBox="0 0 200 200" aria-hidden="true"><circle cx="100" cy="100" r="92" fill="none" stroke="currentColor" stroke-width="10"/><path d="M52 112 Q100 168 148 112" fill="none" stroke="currentColor" stroke-width="10" stroke-linecap="round"/><circle cx="72" cy="78" r="10" fill="currentColor"/><circle cx="128" cy="78" r="10" fill="currentColor"/></svg>
 <div><span class="eyebrow" style="color:var(--ink)">Prodáváte?</span><h2 style="margin-top:1rem">Začněme <em>reálným</em> naceněním.</h2><p style="margin-top:1.2rem;max-width:46ch;font-size:1.08rem">Domluvte si nezávaznou osobní schůzku s naším makléřem. Znalecký odhad i advokáta máte u nás zdarma.</p></div>
 <div><ul>{''.join(f'<li>{I["check"]}{E(p)}</li>' for p in SITE['perks'][:3])}</ul><p style="margin-top:1.6rem"><a class="btn btn--green" href="prodat.html#formular">Chci prodat {I['arrow']}</a></p></div>
</div></section>'''
    page('index.html', 'Reality Smajlík – …u nás koupíte domov | Praha, Plzeň, Cheb', body, over=True)

# ------------------------------------------------------------------ nabídka
def build_list():
    def chip(group, val, label, n, on=False):
        dis = ' disabled' if n == 0 and val else ''
        return f'<button class="chip" data-f="{group}" data-v="{val}" aria-pressed="{"true" if on else "false"}"{dis}>{label}<sup>{n}</sup></button>'
    deal = chip('deal', '', 'Vše', len(L), True) + chip('deal', 'prodej', 'Prodej', count(deal='prodej')) + chip('deal', 'pronajem', 'Pronájem', count(deal='pronajem'))
    br = chip('branch', '', 'Všechny oblasti', len(L), True) + ''.join(chip('branch', k, v, count(branch=k)) for k, v in BRN.items())
    ty = chip('type', '', 'Vše', len(L), True) + ''.join(chip('type', k, v, count(type=k)) for k, v in TYPES.items())
    cards = ''.join(card(x, attrs=True) for x in L)
    body = f'''
<section class="phero" style="padding-bottom:2.5rem"><div class="wrap">
 <nav class="crumbs"><a href="index.html">Úvod</a><span>/</span><span>Nabídka nemovitostí</span></nav>
 <h1>Nabídka <em>nemovitostí</em></h1>
 <p class="lede">Byty, rodinné domy, chalupy, pozemky i komerční prostory. Vyberte oblast podle pobočky, typ nemovitosti a jestli chcete kupovat, nebo pronajímat.</p>
</div></section>
<div class="filters"><div class="wrap">
 <div class="chips" role="group" aria-label="Druh">{deal}</div><span class="fsep"></span>
 <div class="chips" role="group" aria-label="Oblast">{br}</div>
</div><div class="wrap" style="margin-top:.7rem">
 <div class="chips" role="group" aria-label="Typ">{ty}</div>
 <div class="fctl"><input type="search" placeholder="Hledat obec, ulici, dispozici…" data-q aria-label="Hledat"><select data-sort aria-label="Řazení"><option value="new">Nejnovější</option><option value="cheap">Od nejlevnější</option><option value="exp">Od nejdražší</option></select></div>
</div></div>
<section class="wrap" style="padding-bottom:2rem">
 <div class="results-head"><h2><span data-shown>{len(L)}</span> nemovitostí</h2><p class="note">Stav nabídky převzatý z realitysmajlik.cz k 4. 10. 2026.</p></div>
 <div class="grid" data-grid>{cards}<div class="empty" hidden data-empty><h3>Tady zatím nic není</h3><p>Pro tuto kombinaci teď nemáme nabídku. Napište nám, co hledáte – <a class="link" href="mailto:{SITE['email']}">{SITE['email']}</a></p></div></div>
</section>'''
    page('nabidka.html', 'Nabídka nemovitostí | Reality Smajlík', body, active='nabidka.html')

# ------------------------------------------------------------------ detail
ECOL = {'A': '#00843D', 'B': '#4CA03A', 'C': '#B5C934', 'D': '#F4D21F', 'E': '#F3A31B', 'F': '#E5641F', 'G': '#D52B1E'}
def build_details():
    for x in L:
        r = '../'
        ph = x['photos']
        cls = {1: ' gal--1', 2: ' gal--2', 3: ' gal--3'}.get(len(ph), '')
        gal = ''
        for i, p in enumerate(ph[:5]):
            more = f'<span class="more">+ {len(ph) - 5} fotografií</span>' if i == 4 and len(ph) > 5 else ''
            gal += f'<a href="{img(r, p, "n")}" data-lb="{i}"><img src="{img(r, p, "n" if i == 0 else "t")}" alt="{E(x["title"])} – foto {i + 1}" {"" if i == 0 else "loading=lazy"}>{more}</a>'
        lbdata = json.dumps([img(r, p, 'n') for p in ph])
        gal_html = f'<div class="gal{cls}" data-photos=\'{E(lbdata)}\'>{gal}</div>' if ph else ''
        paras = ''.join(f'<p>{E(p)}</p>' for p in x['desc'].split('\n') if p.strip())
        params = ''.join(f'<div><dt>{E(k)}</dt><dd>{E(v)}</dd></div>' for k, v in x['params'] if k != 'Třída energetické náročnosti budovy')
        amen = ''.join(f'<span>{E(a)}</span>' for a in x['amenities'])
        en = ''
        if x['energy']:
            c = x['energy'][0]
            en = f'<h2 class="d-h">Energetická náročnost</h2><span class="energy"><b style="background:{ECOL.get(c, "#888")}">{c}</b>{E(x["energy"])}</span>'
        b = x['broker'] or {}
        bk = next((k for k, t in TEAM.items() if t['email'] == b.get('email')), 'veberova')
        t = TEAM[bk]
        sim = [y for y in L if y is not x and y['type'] == x['type'] and y['deal'] == x['deal']]
        sim = (sim + [y for y in L if y is not x and y['branch'] == x['branch'] and y not in sim])[:3]
        st = ''.join(f'<span class="badge badge--{SLUG(s)}" style="position:static">{STATUS.get(s, s)}</span>' for s in x['status'])
        body = f'''
<section class="d-head wrap">
 <nav class="crumbs"><a href="../index.html">Úvod</a><span>/</span><a href="../nabidka.html">Nabídka</a><span>/</span><a href="../nabidka.html?deal={x['deal']}&amp;type={x['type']}">{TYPES[x['type']]}</a></nav>
 <h1>{E(x['title'])}</h1>
 <div class="d-sub"><span>{I['pin']}{E(x['locality'])}</span>{f"<span>{I['area']}{E(x['area'])}</span>" if x['area'] else ''}<span>{I['tag']}č. {E(x['id'])}</span>{st}</div>
</section>
<section class="wrap">{gal_html}
 <div class="d-body">
  <article>
   <div class="d-price"><b>{E(x['price'])}</b><small>{E(x['price_unit'])} {E(x['price_note'])}</small><span class="badge badge--deal" style="position:static">{"Pronájem" if x['deal'] == 'pronajem' else 'Prodej'}</span></div>
   <a class="btn btn--orange d-quick" href="#poptat">Domluvit prohlídku {I['arrow']}</a>
   {f'<p class="d-lead">{E(x["lead"])}</p>' if x['lead'] else ''}
   <div class="d-desc">{paras}</div>
   <h2 class="d-h">Parametry</h2><dl class="params">{params}</dl>
   {f'<h2 class="d-h">V okolí</h2><div class="amen">{amen}</div>' if amen else ''}
   {en}
   <h2 class="d-h">Kde to je</h2><p><a class="btn btn--ghost" href="https://mapy.cz/zakladni?q={quote(x['locality'])}" target="_blank" rel="noopener">Zobrazit {E(x['town'])} na mapě {I['arrow']}</a></p>
  </article>
  <aside class="aside" id="poptat">
   <ul style="list-style:none"><li class="person"><span class="ava">{initials(t['name'])}</span><div><small>Vaše makléřka</small><b>{E(t['name'])}</b>{E(t['role'])}</div></li></ul>
   <div class="contact-row"><a href="tel:{t['phone'].replace(' ', '')}">{t['phone']}</a><a href="mailto:{t['email']}">{t['email']}</a></div>
   <form data-mailto="{t['email']}" data-subject="Dotaz k nemovitosti č. {E(x['id'])}">
    <input name="Jméno" placeholder="Jméno a příjmení" required><input name="E-mail" type="email" placeholder="E-mail" required><input name="Telefon" placeholder="Telefon">
    <textarea name="Zpráva">Dobrý den, mám zájem o nemovitost č. {E(x['id'])} ({E(x['title'][:70])}). Prosím o více informací a termín prohlídky.</textarea>
    <button class="btn btn--orange" type="submit">Domluvit prohlídku {I['arrow']}</button>
    <small>V návrhu otevře e-mail s vyplněnými údaji.</small>
   </form>
  </aside>
 </div>
</section>
<section class="sec wrap" style="padding-bottom:0"><div class="sec-head"><h2>Mohlo by Vás <em>zajímat</em></h2><a class="link" href="../nabidka.html">Celá nabídka {I['arrow']}</a></div><div class="grid">{''.join(card(y, r) for y in sim)}</div></section>
<div class="lb" aria-hidden="true"><button class="x" aria-label="Zavřít">×</button><button class="pv" aria-label="Předchozí">‹</button><img alt=""><button class="nx" aria-label="Další">›</button><span class="cnt"></span></div>'''
        page(f'nemovitost/{x["slug"]}.html', f'{x["title"]} | Reality Smajlík', body, r=r, active='nabidka.html', desc=x['lead'][:160])

# ------------------------------------------------------------------ prodávající
def build_sell():
    types = ['Byty', 'Domy', 'Garáže, jiné malé objekty', 'Hotely, penzióny, restaurace', 'Komerční objekty', 'Komerční prostory', 'Novostavby, developerské objekty', 'Pozemky', 'Rekreační objekty', 'Zemědělské objekty']
    f = (f'<label>Typ nemovitosti<select name="Typ nemovitosti">{"".join(f"<option>{t}</option>" for t in types)}</select></label>'
         '<label>Typ akce<select name="Typ akce"><option>Prodej</option><option>Prodej či pronájem</option><option>Pronájem</option></select></label>'
         '<label>Lokalita<input name="Lokalita"></label><label>Požadovaná cena v Kč<input name="Požadovaná cena"></label>'
         '<label class="full">Popis<textarea name="Popis"></textarea></label>'
         '<label>Jméno a příjmení *<input name="Jméno" required></label><label>Telefon *<input name="Telefon" required></label><label class="full">E-mail *<input name="E-mail" type="email" required></label>')
    penb = SV['penb']
    body = f'''
<section class="phero phero--img"><img src="assets/img/s/vila2.webp" alt=""><div class="wrap">
 <span class="eyebrow">Pro prodávající a pronajímatele</span>
 <h1>Prodáme Vaši nemovitost <em>bez starostí</em></h1>
 <p class="lede">Reálné nacenění, kvalitní prohlídky, smlouvy, úschova peněz i přepis energií. Kontaktujte nás a domluvte si nezávaznou osobní schůzku s naším makléřem.</p>
 <nav class="anchor-nav"><a href="#formular">Realitní formulář</a><a href="#penb">Energetický průkaz</a><a href="#privatizace">Privatizace bytů</a><a href="#poptavame">Aktuálně poptáváme</a><a href="#partneri">Partneři</a></nav>
</div></section>

<section class="sec"><div class="wrap two">
 <div><span class="eyebrow">Služby v našem podání</span><h2 class="rv" style="margin:1rem 0 2rem">Co pro Vás <em>uděláme</em></h2>{checks([s[0].upper() + s[1:] for s in SV['included']])}</div>
 <div class="panel panel--green rv"><h3 style="margin-bottom:1.2rem">Při výhradním zastoupení navíc</h3>{checks(SV['exclusive'])}<p class="portals" style="margin-top:1.4rem;color:rgba(243,238,227,.65)">Inzerujeme na serverech {", ".join(SITE['portals'])} a mnoha dalších.</p></div>
</div></section>

<section class="sec dark" style="padding-block:clamp(4rem,8vw,6rem)">{HOUSE_BIG}<div class="wrap"><span class="eyebrow">Proč svěřit nemovitost nám</span><div class="perks" style="margin-top:2rem">{''.join(f'<span class="perk">{I["check"]}{E(p)}</span>' for p in SITE['perks'])}</div></div></section>

<section class="sec" id="formular"><div class="wrap two">
 <div><span class="eyebrow">Chci prodat</span><h2 class="rv" style="margin:1rem 0 1.4rem">Realitní <em>formulář</em></h2><p class="lede">Napište nám pár slov o nemovitosti. Ozveme se a domluvíme nezávaznou osobní schůzku s makléřem z nejbližší pobočky.</p></div>
 <div class="panel rv">{mailform(SITE['email'], 'Chci prodat – realitní formulář', f)}</div>
</div></section>

<section class="sec" id="penb" style="background:var(--bg-alt)"><div class="wrap two">
 <div><span class="eyebrow">Energetický průkaz</span><h2 class="rv" style="margin:1rem 0 1.4rem">Chcete průkaz energetické <em>náročnosti</em> budovy?</h2><p class="lede">{penb['intro']} Průkaz Vám zajistíme – kontaktujte nás a domluvte si nezávaznou schůzku.</p><p style="margin-top:1.8rem"><a class="btn btn--green" href="mailto:{SITE['email']}?subject=Energetick%C3%BD%20pr%C5%AFkaz">Poptat PENB {I['arrow']}</a></p></div>
 <div class="rv"><h3 style="margin-bottom:1rem">Povinnosti vlastníka budovy</h3>{checks(penb['owner_building'])}<h3 style="margin:2rem 0 1rem">Povinnosti vlastníka jednotky</h3>{checks(penb['owner_unit'])}<p class="note" style="margin-top:1.4rem">{penb['note']}</p></div>
</div></section>

<section class="sec" id="privatizace"><div class="wrap two">
 <figure class="sticky-media rv-clip" style="aspect-ratio:4/3;position:relative;top:0"><img src="assets/img/s/cheb.webp" alt="" loading="lazy"></figure>
 <div><span class="eyebrow">Privatizace bytů</span><h2 class="rv" style="margin:1rem 0 1.6rem">Kompletní <em>servis</em> při privatizaci</h2><div class="prose">{''.join(f'<p>{E(p)}</p>' for p in SV['privatization'])}</div></div>
</div></section>

<section class="sec" id="poptavame" style="padding-top:0"><div class="wrap">
 <div class="sec-head"><div><span class="eyebrow">Aktuálně poptáváme</span><h2 class="rv">Hledáme pro naše <em>klienty</em></h2></div><p class="lede">Máte něco podobného? Napište nám – kupce už máme.</p></div>
 <ul class="wanted">{''.join(f'<li class="rv">{E(w[0].upper() + w[1:])}</li>' for w in SV['wanted'])}</ul>
</div></section>

<section class="sec" id="partneri" style="padding-top:0"><div class="wrap">
 <div class="sec-head"><div><span class="eyebrow">Partneři</span><h2 class="rv">Slevy u našich <em>partnerů</em></h2></div><p class="lede">Našim klientům se snažíme být partnerem i v otázkách rekonstrukcí. Pro získání slevy nás kontaktujte na praha@realitysmajlik.cz.</p></div>
 <div class="partners">{''.join(f'<div class="panel rv d{i}"><h3>{E(p["t"])}</h3><p>{E(p["d"])}</p><span class="link">{E(p["web"])}</span></div>' for i, p in enumerate(SV['partners']))}</div>
</div></section>'''
    page('prodat.html', 'Chci prodat | Reality Smajlík', body, active='prodat.html', over=True)

# ------------------------------------------------------------------ o nás
def build_about():
    rv = ''.join(f'<figure class="q"><p>„{E(q["q"])}“</p><cite>{E(q["a"]) or "spokojený klient"}</cite></figure>' for q in REV)
    c = SV['career']
    body = f'''
<section class="phero phero--img"><img src="assets/img/s/chalupa.webp" alt=""><div class="wrap">
 <span class="eyebrow">O nás</span>
 <h1>Bydlení řešíme <em>od roku {SITE['since']}</em></h1>
 <p class="lede">Reality Smajlík s.r.o. – realitní kancelář s pobočkami v Praze, Plzni a Chebu.</p>
</div></section>
<section class="sec"><div class="wrap two">
 <div class="prose rv">{''.join(f'<p>{E(p)}</p>' for p in SITE['about'])}<p>K dispozici jsme v tuto chvíli na třech místech republiky, a to v Praze, Plzni a Chebu.</p></div>
 <div class="panel rv d1"><span class="eyebrow">Tým</span><ul class="people" style="border:0;margin-top:1.4rem">{''.join(person(k) for k in TEAM)}</ul><p style="margin-top:1.6rem"><a class="link" href="kontakt.html">Pobočky a kontakty {I['arrow']}</a></p></div>
</div></section>
<section class="sec" id="reference" style="background:var(--bg-alt)"><div class="wrap">
 <div class="sec-head"><div><span class="eyebrow">Reference</span><h2 class="rv">Co o nás říkají <em>klienti</em></h2></div></div>
 <div class="masonry">{rv}</div>
</div></section>
<section class="sec" id="kariera"><div class="wrap">
 <div class="sec-head"><div><span class="eyebrow">Kariéra</span><h2 class="rv">Přidejte se k <em>nám</em></h2></div><p class="lede">Na naše pobočky v Praze, Plzni a Chebu hledáme schopné a aktivní lidi na pozici realitního makléře. Chtěli byste mít pobočku Reality Smajlík ve Vašem městě?</p></div>
 <div class="two"><div class="panel panel--green rv"><h3 style="margin-bottom:1.2rem">Co Vám nabízíme</h3>{checks(c['offer'])}</div><div class="panel rv d1"><h3 style="margin-bottom:1.2rem">Co potřebujete</h3>{checks(c['need'])}<p style="margin-top:1.8rem">Za zkoušku nic nedáte – životopis pošlete na <a class="link" href="mailto:{SITE['email']}">{SITE['email']}</a>.</p></div></div>
</div></section>
<section class="wrap" id="odstoupeni"><h3 style="margin-bottom:1rem">Odstoupení od zprostředkovatelské smlouvy</h3><p class="note">{E(SITE['withdrawal'])}</p></section>'''
    page('o-nas.html', 'O nás | Reality Smajlík', body, active='o-nas.html', over=True)

# ------------------------------------------------------------------ kontakt
def build_contact():
    f = ('<label>Jméno a příjmení *<input name="Jméno" required></label><label>E-mail *<input name="E-mail" type="email" required></label>'
         '<label class="full">Pobočka<select name="Pobočka"><option>Cheb</option><option>Plzeň</option><option>Praha</option></select></label>'
         '<label class="full">Zpráva<textarea name="Zpráva"></textarea></label>')
    body = f'''
<section class="phero"><div class="wrap">
 <nav class="crumbs"><a href="index.html">Úvod</a><span>/</span><span>Kontakt</span></nav>
 <h1>Pojďme to <em>probrat</em></h1>
 <p class="lede">Zavolejte, napište, nebo se zastavte na pobočce. Domluvíme si nezávaznou osobní schůzku.</p>
</div></section>
<section class="wrap"><div class="branches">{''.join(branch_card(b) for b in BR)}</div></section>
<section class="sec"><div class="wrap two">
 <div class="rv"><span class="eyebrow">Společnost</span><h2 style="margin:1rem 0 1.6rem">{E(SITE['company'])}</h2>
  <p>IČ: {SITE['ico']}<br>{SITE['address']}</p>
  <p style="margin-top:1rem"><a class="link" href="tel:{SITE['phones'][1].replace(' ', '')}">{SITE['phones'][1]}</a><br><a class="link" href="tel:{SITE['phones'][0].replace(' ', '')}">{SITE['phones'][0]}</a><br><a class="link" href="mailto:{SITE['email']}">{SITE['email']}</a></p>
  <p class="note" style="margin-top:1.4rem">{E(SITE['registry'])}.<br>Číslo účtu pro rezervační zálohy: {SITE['account']}</p></div>
 <div class="panel rv d1"><h3 style="margin-bottom:1.4rem">Napište nám</h3>{mailform(SITE['email'], 'Dotaz z webu', f, 'Odeslat zprávu')}</div>
</div></section>'''
    page('kontakt.html', 'Kontakt | Reality Smajlík', body, active='kontakt.html')

# ------------------------------------------------------------------ lokality
def build_loc():
    rows = ''.join(f'<div class="loc-row rv" id="{SLUG(n)}"><span class="n">{i:02d}</span><h3>{n}<small>{s}</small></h3><p>{E(t)}</p></div>' for i, (n, s, t) in enumerate(LOC['items'], 1))
    cheb = [x for x in L if x['type'] == 'byty' and x['deal'] == 'prodej' and x['town'] == 'Cheb'][:6]
    body = f'''
<section class="phero phero--img"><img src="assets/img/s/cheb.webp" alt=""><div class="wrap">
 <span class="eyebrow">Průvodce</span>
 <h1>Kde koupit byt <em>v&nbsp;Chebu?</em></h1>
 <p class="lede">Přehled nejžádanějších lokalit.</p>
</div></section>
<section class="sec"><div class="wrap">
 <p class="d-lead rv" style="max-width:52ch">{E(LOC['intro'])}</p>
 <p class="lede rv" style="margin-bottom:3rem">Pokud hledáte byt na prodej v Chebu, vyplatí se zaměřit nejen na cenu nemovitosti, ale také na občanskou vybavenost, dopravní dostupnost, možnosti parkování, školy, školky a celkovou kvalitu života v dané lokalitě.</p>
 <div class="loc-art">{rows}</div>
</div></section>
<section class="wrap"><div class="sec-head"><div><span class="eyebrow">Z nabídky</span><h2>Byty na prodej <em>v Chebu</em></h2></div><a class="link" href="nabidka.html?deal=prodej&amp;type=byty&amp;branch=cheb">Všechny byty {I['arrow']}</a></div><div class="grid">{''.join(card(x) for x in cheb)}</div></section>'''
    page('lokality.html', 'Kde koupit byt v Chebu? | Reality Smajlík', body, active='lokality.html', over=True)

def build_404():
    body = f'<section class="phero" style="min-height:70vh"><div class="wrap"><span class="eyebrow">404</span><h1>Tahle stránka <em>se odstěhovala</em></h1><p class="lede">Zkuste nabídku nemovitostí nebo úvodní stránku.</p><p style="margin-top:2rem;display:flex;gap:.8rem;flex-wrap:wrap"><a class="btn btn--green" href="/realitysmajlik/nabidka.html">Nabídka {I["arrow"]}</a><a class="btn btn--ghost" href="/realitysmajlik/">Úvod</a></p></div></section>'
    page('404.html', 'Stránka nenalezena | Reality Smajlík', body, r='/realitysmajlik/')

if __name__ == '__main__':
    shutil.rmtree(f'{ROOT}/nemovitost', ignore_errors=True)
    build_index(); build_list(); build_details(); build_sell(); build_about(); build_contact(); build_loc(); build_404()
    open(f'{ROOT}/robots.txt', 'w').write('User-agent: *\nDisallow: /\n')
    open(f'{ROOT}/.nojekyll', 'w').write('')
    print('hotovo', len(L), 'detailů')
