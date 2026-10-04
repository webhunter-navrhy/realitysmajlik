"""_raw/listings_raw.json -> _data/listings.json (+ náhledy assets/img/t/, hero ořezy)."""
import json, os, re, unicodedata
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
raw = json.load(open(f'{ROOT}/_raw/listings_raw.json'))
os.makedirs(f'{ROOT}/assets/img/t', exist_ok=True)

def typ(t):
    t = t.split(' - ')[-1]
    return {'Byty': 'byty', 'Rodinné domy': 'domy', 'Nájemní domy': 'domy', 'Pozemky': 'pozemky',
            'Chaty a chalupy': 'rekreace', 'Garáže a jiné malé objekty': 'garaze'}.get(t, 'komerce')

def num(s):
    m = re.match(r'\s*([\d.]+)\s*Kč', s or '')
    return int(m.group(1).replace('.', '')) if m else None

def fmt_price(s):
    m = re.match(r'\s*([\d.]+)\s*Kč\s*\(za (.*?)\)?$', s or '')
    if not m: return s or 'Informace v RK', ''
    n = int(m.group(1).replace('.', '')); unit = m.group(2).strip().rstrip(')')
    v = f'{n:,}'.replace(',', ' ') + ' Kč'
    u = {'nemovitost': '', 'měsíc': 'měsíčně', 'm²': 'za m²', 'm² / měsíc': 'za m² měsíčně'}.get(unit, unit)
    return v, u

AMEN = ['Škola', 'Školka', 'Obchody', 'Supermarket', 'Lékař', 'Pošta', 'MHD', 'Autobus', 'Železnice', 'Dálnice', 'Parkoviště', 'Služby']
KEYS = ['Číslo', 'Plocha', 'Užitná plocha', 'Plocha pozemku', 'Plocha zastavěná', 'Číslo podlaží v domě', 'Celkový počet podlaží',
        'Stav objektu', 'Technologie výstavby', 'Vlastnictví', 'Rok výstavby', 'Rok rekonstrukce', 'Včetně vybavení',
        'Balkón', 'Lodžie', 'Terasa', 'Sklep', 'Výtah', 'Garáž', 'Počet bytů v domě', 'Umístění objektu',
        'Třída energetické náročnosti budovy']
out = []
seen = set()
for i, x in enumerate(raw):
    p = x['params']
    loc = p.get('Lokalita', x['town'])
    region = loc.split(', ')[-1]
    branch = 'cheb' if region == 'Karlovarský' else 'plzen' if region == 'Plzeňský' else 'praha'
    title = x['h1'] or x['title']
    rent = 'měsíc' in x['price_raw'] or bool(re.match(r'pronájem', title, re.I)) or bool(re.search(r'k pronájmu|na pronájem', title, re.I))
    slug = x['url'].rstrip('/').rsplit('/', 1)[-1][:90].strip('-')
    while slug in seen: slug += '-2'
    seen.add(slug)
    photos = []
    for ph in x['photos'][:8]:
        fid = re.search(r'(\d+)\.jpg', ph).group(1)
        src = f'{ROOT}/assets/img/n/{fid}.webp'
        if not os.path.exists(src): continue
        dst = f'{ROOT}/assets/img/t/{fid}.webp'
        if not os.path.exists(dst):
            im = Image.open(src); im.thumbnail((720, 720)); im.save(dst, 'webp', quality=74)
        w, h = Image.open(src).size
        photos.append(dict(id=fid, w=w, h=h))
    price, unit = fmt_price(x['price_raw'])
    area = p.get('Užitná plocha') or p.get('Plocha') or p.get('Plocha pozemku') or ''
    area = area.replace(' m 2', ' m²').replace('m 2', 'm²')
    params = [[k, p[k].replace(' m 2', ' m²') + (' m²' if k.startswith('Plocha') and re.fullmatch(r'[\d .,]+', p[k]) else '')] for k in KEYS if p.get(k)]
    status = [s for s in x['status'] if s != 'aktuální']
    out.append(dict(
        id=x['number'], slug=slug, title=title, lead=x.get('lead', ''), desc=x.get('desc', ''),
        town=x['town'], locality=loc.replace(', Karlovarský', '').replace(', Plzeňský', ''), region=region, branch=branch,
        type=typ(p.get('Typ reality', '')), category=x['category'], deal='pronajem' if rent else 'prodej',
        price=price, price_unit=unit, price_num=num(x['price_raw']), price_note=x.get('price_note', ''),
        area=area, status=status, params=params, amenities=[a for a in AMEN if p.get(a) == 'Ano'],
        energy=p.get('Třída energetické náročnosti budovy', ''), broker=x.get('broker', {}), photos=photos,
        source=x['url'], order=i))
json.dump(out, open(f'{ROOT}/_data/listings.json', 'w'), ensure_ascii=False, indent=1)
from collections import Counter
print(len(out), Counter(o['deal'] for o in out), Counter(o['type'] for o in out), Counter(o['branch'] for o in out))
print(sum(1 for o in out if not o['photos']))
