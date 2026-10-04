import json, os, re, io, urllib.request
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(f'{ROOT}/_raw/listings_raw.json'))
out = f'{ROOT}/assets/img/n'; os.makedirs(out, exist_ok=True)
jobs = []
for it in d:
    for p in it['photos'][:8]:
        fid = re.search(r'(\d+)\.jpg', p).group(1); jobs.append((p, f'{out}/{fid}.webp'))
def dl(j):
    p, dst = j
    if os.path.exists(dst): return dst, None
    raw = urllib.request.urlopen(urllib.request.Request('https://www.realitysmajlik.cz' + p, headers={'User-Agent': 'Mozilla/5.0'}), timeout=40).read()
    im = Image.open(io.BytesIO(raw)).convert('RGB'); size = im.size
    im.thumbnail((1400, 1400)); im.save(dst, 'webp', quality=78)
    return dst, size
with ThreadPoolExecutor(8) as ex:
    res = list(ex.map(dl, jobs))
sz = [r[1] for r in res if r[1]]
print(len(res), sz[:10])
