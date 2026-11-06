@echo off
cd /d "%~dp0"
title Velora Cinema V5
python -m pip install -r requirements.txt
if errorlevel 1 (
  echo Python/Pillow installation problem. Run pip manually if needed.
  pause
  exit /b 1
)
python import_existing_art.py
python app.py
if errorlevel 1 pause
