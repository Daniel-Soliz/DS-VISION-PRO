@echo off
title DS VISION PRO - Build local
echo ==========================================
echo       DS VISION PRO - BUILD LOCAL
echo ==========================================
echo.
echo Gerando versao Windows em pasta (onedir)...
py -m PyInstaller --noconfirm --onedir --windowed --collect-all customtkinter --name DS_VISION_PRO app.py
echo.
echo Build concluido.
echo Abra: dist\DS_VISION_PRO\DS_VISION_PRO.exe
echo.
pause
