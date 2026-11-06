"""Prepare genuine anime poster art for the ORIGINAL Velora Cinema V3 UI (V5 anime fixes).

This does not change application screens or replace existing artwork. Anime image
sources: Jikan (MyAnimeList) and Kitsu. No generated posters or stock photos.
"""
from pathlib import Path
from catalog import CATALOG
from artwork import fetch_one, POSTERS


def main():
    anime = [item for item in CATALOG if item['kind'] == 'Anime']
    print('VELORA CINEMA V5 - GENUINE ANIME POSTERS')
    print('V3 UI retained. Checking 20 anime titles.\n', flush=True)
    done=[]
    missing=[]
    for i,item in enumerate(anime,1):
        path=POSTERS/(item['id']+'.jpg')
        if path.is_file() and path.stat().st_size > 5_000:
            status='already saved';done.append(item)
        else:
            try:
                poster,_=fetch_one(item)
            except Exception:
                poster=False
            if poster:
                done.append(item);status='downloaded'
            else:
                missing.append(item);status='not available (retry later)'
        print(f'[{i:02d}/{len(anime)}] {item["title"]}: {status}', flush=True)
    print(f'\nGenuine anime posters ready: {len(done)}/{len(anime)}')
    if missing:
        print('Retry this tool when online for any still missing:')
        for a in missing:print(' - '+a['title'])
    else:
        print('All 20 title-matched anime posters are cached. The app now works offline.')
    print('Start Velora Cinema with RUN_VELORA_V5.bat or python app.py')


if __name__=='__main__':
    main()
