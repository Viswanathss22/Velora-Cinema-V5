"""Preserve authentic poster files downloaded by earlier Velora V3 copies.

Only copies catalogue-named files that Pillow verifies. No fabricated imagery.
"""
from pathlib import Path
from shutil import copy2
from PIL import Image
from catalog import BY_ID

HERE = Path(__file__).resolve().parent
DEST = HERE / 'assets' / 'posters'
DEST.mkdir(parents=True, exist_ok=True)


def ok(path):
    if not (path.exists() and path.stat().st_size > 5_000):
        return False
    try:
        with Image.open(path) as im:
            im.verify()
        return True
    except (OSError, ValueError):
        return False


def main():
    roots = [HERE.parent, HERE.parent.parent]
    sources = []
    for root in roots:
        for name in ('Velora_Cinema_V3', 'Velora_Cinema_Collections_V3',
                     'Velora_Cinema_Premium_V2', 'Velora_Cinema_Complete_Edition'):
            folder = root / name / 'assets' / 'posters'
            if folder.is_dir() and folder.resolve() != DEST.resolve():
                sources.append(folder)
    imported = 0
    for source in dict.fromkeys(sources):
        for mid in BY_ID:
            existing = source / (mid + '.jpg')
            target = DEST / (mid + '.jpg')
            if not ok(target) and ok(existing):
                copy2(existing, target)
                imported += 1
    print(f'Preserved {imported} existing Velora posters from older project folders.')
    print('Existing correctly named poster files are never overwritten.')


if __name__ == '__main__':
    main()
