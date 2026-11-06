@echo off
cd /d "%~dp0"
title Velora Cinema V5 - Prepare Anime and Launch
python -m pip install -r requirements.txt
if errorlevel 1 (
  echo Could not install Pillow. Check Python and your internet connection.
  pause
  exit /b 1
)
python import_existing_art.py
python anime_images.py
python app.py
if errorlevel 1 pause
