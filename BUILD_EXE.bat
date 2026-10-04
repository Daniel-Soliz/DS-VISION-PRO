@echo off
title DS VISION PRO - Build
py -m PyInstaller --noconfirm --onefile --windowed --collect-all customtkinter --name DS_VISION_PRO app.py
echo.
echo Executavel criado na pasta dist.
pause
