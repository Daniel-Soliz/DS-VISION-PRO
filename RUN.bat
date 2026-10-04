@echo off
title DS VISION PRO
py app.py
if errorlevel 1 (
  echo.
  echo O aplicativo encontrou um erro.
  pause
)
