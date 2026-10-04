"""Stáhne nabídku z realitysmajlik.cz (RealBrána) do _data/listings.json + fotky do assets/img/n/."""
import re, html, json, os, sys, time, urllib.request, io, hashlib
from concurrent.futures import ThreadPoolExecutor
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, '_raw'); BASE = 'https://www.realitysmajlik.cz'
UA = {'User-Agent': 'Mozilla/5.0'}

def get(url):
    for i in range(3):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40).read()
        except Exception as e:
            time.sleep(2)
    raise RuntimeError(url)

def clean(s):
    s = re.sub(r'<[^>]+>', ' ', s); s = html.unescape(s).replace('\xa0', ' ')
    return re.sub(r'\s+', ' ', s).strip()

items = []
for f in range(0, 80, 10):
    s = open(f'{RAW}/list_{f}.html', encoding='utf-8').read()
    for b in re.findall(r'<div class="box (?:lichy|sudy)[^"]*">(.*?)<div class="cleaner"></div>\s*</div>', s, re.S):
        m = re.search(r'<h2><a href="([^"]+)">(.*?)</a></h2>', b, re.S)
        if not m: continue
        st = [clean(x) for x in re.findall(r'<strong class="cedulka[^"]*">(.*?)</strong>', b)]
        loc = re.search(r'class="location">Lokalita:(.*?)</li>', b, re.S)
        cat = re.search(r'class="category">Zařazení:(.*?)</li>', b, re.S)
        num = re.search(r'Číslo:(.*?)</li>', b, re.S)
        pr = re.search(r'class="price">(.*?)</span>\s*<form', b, re.S) or re.search(r'class="price">(.*?)</span>', b, re.S)
        items.append(dict(url=m.group(1), title=clean(m.group(2)), status=st,
            town=clean(loc.group(1)) if loc else '', category=clean(cat.group(1)) if cat else '',
            number=clean(num.group(1)) if num else '', price_raw=clean(pr.group(1)).replace('Cena:', '').strip() if pr else ''))
print('seznam', len(items), file=sys.stderr)

def detail(it):
    s = get(it['url']).decode('utf-8', 'ignore')
    d = {}
    m = re.search(r'<h1[^>]*>(.*?)</h1>', s, re.S); d['h1'] = clean(m.group(1)) if m else it['title']
    def para(x):
        t = re.sub(r'(?i)<br\s*/?>', '\n', x); t = re.sub(r'</p>', '\n', t)
        t = html.unescape(re.sub(r'<[^>]+>', '', t)).replace('\xa0', ' ')
        return '\n'.join(re.sub(r'[ \t]+', ' ', y).strip() for y in t.split('\n') if y.strip())
    m = re.search(r'<div class="pre-annotation">(.*?)</div>', s, re.S); d['lead'] = para(m.group(1)) if m else ''
    m = re.search(r'<div class="text description">(.*?)</div>', s, re.S); d['desc'] = para(m.group(1)) if m else ''
    m = re.search(r'<span class="note">(.*?)</span>', s, re.S); d['price_note'] = clean(m.group(1)) if m else ''
    params = {}
    for k, v in re.findall(r'<(?:dt|th)[^>]*>(.*?)</(?:dt|th)>\s*<(?:dd|td)[^>]*>(.*?)</(?:dd|td)>', s, re.S):
        k = clean(k).rstrip(':'); v = clean(v)
        if k and v and len(k) < 60: params[k] = v
    d['params'] = params
    m = re.search(r'Kontakt na makléře(.*?)Kontaktovat makléře', s, re.S)
    if m:
        t = clean(m.group(1)); em = re.search(r'[\w.]+@realitysmajlik\.cz', t)
        name = re.sub(r'\s*\+?[\d ]{9,}.*', '', t).strip()
        d['broker'] = dict(name=name, email=em.group(0) if em else '')
    d['photos'] = list(dict.fromkeys(re.findall(r'href="(/editor/image/reality_photos/tn_zoom_filename_\d+\.jpg)"', s)))
    g = re.search(r'gps" size="30" value="([\d.]+)', s); g2 = re.search(r'gps_lng[^>]*value="([\d.]+)|lng" size="30" value="([\d.]+)', s)
    d['_gps_raw'] = re.findall(r'name="[^"]*gps[^"]*"[^>]*value="([\d.]+)"', s)
    return d

with ThreadPoolExecutor(6) as ex:
    for it, d in zip(items, ex.map(detail, items)):
        it.update(d)
json.dump(items, open(f'{RAW}/listings_raw.json', 'w'), ensure_ascii=False, indent=1)
print('hotovo', len(items), file=sys.stderr)
