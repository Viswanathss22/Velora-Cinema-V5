"""Download and cache real, title-matched film, TV and anime artwork.

Sources:
- TMDb image CDN for known film poster / backdrop paths
- Apple's iTunes Store Search API for film posters
- TVmaze public API for television series posters
- Jikan public MyAnimeList API for anime posters

The project intentionally does not invent artwork or show mismatched photos as posters.
Online artwork is owned by the respective rights holders. Personal student demo only.
"""
import concurrent.futures
import json
import re
import threading
import time
from urllib.error import HTTPError, URLError
from io import BytesIO
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from PIL import Image
from catalog import CATALOG
from anime_sources import DIRECT_ANIME_POSTERS

ROOT = Path(__file__).resolve().parent
POSTERS = ROOT / 'assets' / 'posters'
BACKDROPS = ROOT / 'assets' / 'backdrops'
POSTERS.mkdir(parents=True, exist_ok=True)
BACKDROPS.mkdir(parents=True, exist_ok=True)
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
           'Accept': 'application/json,image/jpeg,image/png,image/webp,*/*'}
_tv_lock = threading.Lock()
_anime_lock = threading.Lock()
# Exact MyAnimeList IDs make identification robust when English and Japanese
# titles differ or a search API has returned a special/movie edition instead.
MAL_ANIME_IDS = {
    'aot':16498,'deathnote':1535,'demonslayer':38000,'jjk':40748,
    'onepiece':21,'naruto':20,'shippuden':1735,'fmab':5114,
    'bebop':1,'chainsaw':44511,'vinland':37521,'spyfamily':50265,
    'frieren':52991,'hxh':11061,'onepunch':30276,'mha':31964,
    'steinsgate':9253,'bleach':269,'codegeass':1575,'haikyu':20583
}



def _get(url, timeout=9, limit=5_000_000):
    with urlopen(Request(url, headers=HEADERS), timeout=timeout) as response:
        return response.read(limit)


def _json(url):
    return json.loads(_get(url, timeout=8).decode('utf-8'))


def _save(data, destination, minimum=(130, 170)):
    img = Image.open(BytesIO(data)).convert('RGB')
    if img.width < minimum[0] or img.height < minimum[1]:
        raise ValueError('Invalid size of image')
    # Some APIs return square images. Prefer genuine vertical poster assets.
    if destination.parent == POSTERS and img.height < img.width * 1.05:
        raise ValueError('Not portrait artwork')
    # Atomic rename prevents the UI reading half-written files.
    temp = destination.with_suffix('.downloading')
    try:
        img.save(temp, 'JPEG', quality=86, optimize=True)
        temp.replace(destination)
    finally:
        if temp.exists():
            temp.unlink()


def _valid(path):
    if not (path.exists() and path.stat().st_size > 5_000):
        return False
    try:
        with Image.open(path) as image:
            image.verify()
        return True
    except (OSError, ValueError):
        return False


def _norm(value):
    return re.sub(r'[^a-z0-9]+', '', (value or '').lower())


def _apple_film_url(item):
    query = urlencode({'term': f"{item['title']} {item['year']}", 'entity':'movie', 'country':'us', 'limit':25})
    entries = _json('https://itunes.apple.com/search?' + query).get('results', [])
    for record in entries:
        if (_norm(record.get('trackName')) == _norm(item['title'])
            and record.get('releaseDate','').startswith(str(item['year']))):
            path = record.get('artworkUrl100','')
            if path:
                return path.replace('100x100bb','600x900bb').replace('100x100-75','600x900-75')
    return None


def _tvmaze_url(item):
    with _tv_lock:
        time.sleep(.55)  # Be respectful of TVmaze rate limits.
        result = _json('https://api.tvmaze.com/search/shows?' + urlencode({'q':item['search']}))
    for row in result:
        show = row.get('show',{})
        premiered = show.get('premiered') or ''
        if (_norm(show.get('name')) == _norm(item['title'])
            and premiered.startswith(str(item['year']))):
            images = show.get('image') or {}
            if images.get('original'):
                return images['original']
            return images.get('medium')
    return None


def _jikan_url(item):
    """Use the exact anime MAL ID, not a fuzzy title query."""
    anime_id = MAL_ANIME_IDS.get(item['id'])
    if anime_id is None:
        return None
    # Single anime endpoints avoid ambiguous names, remakes and season matches.
    # Jikan permits ~3 requests/sec, with occasional HTTP 429.
    with _anime_lock:
        time.sleep(0.58)
        data = _json('https://api.jikan.moe/v4/anime/' + str(anime_id)).get('data') or {}
    if data.get('mal_id') != anime_id:
        return None
    images = data.get('images') or {}
    jpg = images.get('jpg') or {}
    return jpg.get('large_image_url') or jpg.get('image_url')


def _kitsu_anime_url(item):
    """Fallback to authentic poster art from the Kitsu anime catalogue."""
    query = urlencode({'filter[text]': item['search'], 'page[limit]': 20})
    results = _json('https://kitsu.app/api/edge/anime?' + query).get('data') or []
    for result in results:
        attrs = result.get('attributes') or {}
        titles = [attrs.get('canonicalTitle')]
        titles += list((attrs.get('titles') or {}).values())
        titles += (attrs.get('abbreviatedTitles') or [])
        names = {_norm(name) for name in titles}
        if not names.intersection({_norm(item['title']), _norm(item['search'])}):
            continue
        start = attrs.get('startDate') or ''
        if not start.startswith(str(item['year'])):
            continue
        image = attrs.get('posterImage') or {}
        return image.get('original') or image.get('large') or image.get('medium')
    return None


def fetch_one(item):
    poster_path = POSTERS / (item['id'] + '.jpg')
    backdrop_path = BACKDROPS / (item['id'] + '.jpg')
    found_poster = _valid(poster_path)
    found_backdrop = _valid(backdrop_path)

    if not found_poster:
        # Primary: exact, individually selected promotional artwork for anime.
        # This avoids rate-limited search APIs and wrong sequel/season matches.
        candidates = list(DIRECT_ANIME_POSTERS.get(item['id'], ())) if item['kind'] == 'Anime' else []
        if item.get('poster'):
            candidates.append('https://image.tmdb.org/t/p/w500/' + item['poster'])

        def try_urls(urls):
            for url in dict.fromkeys(urls):
                if not url or not url.startswith('https://'):
                    continue
                try:
                    _save(_get(url, timeout=9), poster_path)
                    if _valid(poster_path):
                        return True
                except (OSError, ValueError, HTTPError, URLError):
                    continue
            return False

        found_poster = try_urls(candidates)
        if not found_poster:
            # Secondary: resolve using the existing exact catalogue APIs.
            try:
                if item['kind'] == 'Movies':
                    lookup = _apple_film_url(item)
                elif item['kind'] == 'TV Shows':
                    lookup = _tvmaze_url(item)
                else:
                    lookup = _jikan_url(item)
            except Exception:
                lookup = None
            found_poster = try_urls([lookup])
        if item['kind'] == 'Anime' and not found_poster:
            try:
                lookup = _kitsu_anime_url(item)
            except Exception:
                lookup = None
            found_poster = try_urls([lookup])

    # Only download real backdrops for titles with a known matching TMDb path.
    if item.get('backdrop') and not found_backdrop:
        try:
            _save(_get('https://image.tmdb.org/t/p/w1280/' + item['backdrop'], timeout=9),
                  backdrop_path, (320, 130))
            found_backdrop = _valid(backdrop_path)
        except Exception:
            pass
    return found_poster, found_backdrop


def fetch_all(progress=None, kind=None):
    items = [m for m in CATALOG if kind in (None, 'All') or m['kind'] == kind]
    # First resolve the missing anime first, not after 56 film/TV requests.
    if kind in (None, 'All'):
        items.sort(key=lambda m: (0 if m['kind'] == 'Anime' else 1, CATALOG.index(m)))
    results = []
    # Download in parallel so all 76 entries do not block on one slow service.
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(fetch_one, m): m for m in items}
        for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
            m = futures[future]
            try:
                p, b = future.result()
            except Exception:
                p, b = False, False
            results.append((m['title'], p, b))
            if progress:
                progress(m, p, b, i, len(items))
    return results


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Cache genuine poster artwork for the Velora student demo')
    parser.add_argument('--category', choices=['Movies','TV Shows','Anime'])
    args = parser.parse_args()
    print('Fetching genuine, title-matched artwork (internet required).')
    outcomes = fetch_all(lambda m,p,b,i,n: print(f'[{i:02d}/{n:02d}] {m["kind"]} / {m["title"]}: {"poster saved" if p else "not available"}',flush=True), kind=args.category)
    print(f'Downloaded/available {sum(int(p) for _,p,_ in outcomes)}/{len(outcomes)} posters.')
    print('Film and series imagery is copyright of its respective rights holders.')
