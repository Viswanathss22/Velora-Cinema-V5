# VELORA CINEMA V5 — ANIME ARTWORK UPDATE

**Original Velora Cinema V3 layout is retained.** The only visual change is a small fix that keeps long title names on a single line so the genre text does not overlap.

This is a **Python Tkinter front end only** college project. There are **76 real titles** including **36 movies**, **20 TV shows**, and **20 anime**. No database or video streaming is included.

## Windows: quickest way to get the anime art

1. Extract this new ZIP to your desktop. Keep it separate from the old Velora V3.
2. Make sure you have an internet connection.
3. Double click **DOWNLOAD_ANIME_AND_RUN.bat**.
4. The script installs Pillow (if needed), searches nearby previous Velora folders for saved posters, retrieves genuine artwork for the 20 anime, and then launches the familiar V3 interface.

For a different time, open `RUN_VELORA_V5.bat` or type `python app.py` in VS Code. The app also downloads any remaining uncached posters in the background.

In VS Code the equivalent is:

```powershell
python -m pip install -r requirements.txt
python import_existing_art.py
python anime_images.py
python app.py
```

## Important notes about real anime images

The V5 downloader prioritises a list of **20 individually matched, direct anime promotion poster URLs** (see `anime_sources.py`). Jikan and Kitsu are fallbacks. It uses all 20 original IDs and saves actual images in `assets/posters/<id>.jpg`. The source URLs were checked against series titles but download success depends on internet access and external image servers. The ZIP does **not** contain the 20 copyrighted poster images; it contains the verified retrieval code and source URLs. If you cannot reach a poster host, a placeholder remains instead of misrepresenting another image as real anime art.

If your older V3 already downloaded authentic posters, `import_existing_art.py` copies any found files from neighbouring Velora folders without deleting your originals. You can also manually copy contents of your old `assets/posters/` into the new project's `assets/posters/` before running the downloader.

You can run `GET_ANIME_POSTERS.bat` again later if a host is unavailable. Previously cached genuine images are kept.

## Features retained from V3

Home, Movies, TV Shows, Anime, Saved, About, scrolling, search, filters, film details, guest entry, and poster caching.

Poster artwork is owned by the respective production studios/distributors. It is used here as a non-commercial educational UI demonstration. No movies, series or episodes are streamed or distributed.
