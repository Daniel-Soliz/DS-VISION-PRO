@echo off
title DS VISION PRO
python app.py
if errorlevel 1 (
  echo.
  echo O aplicativo encontrou um erro.
  pause
)
