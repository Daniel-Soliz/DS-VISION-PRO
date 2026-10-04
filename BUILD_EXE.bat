@echo off
title DS VISION PRO - Build local
echo ==========================================
echo       DS VISION PRO - BUILD LOCAL
echo ==========================================
echo.
echo Gerando aplicativo Windows...
python -m PyInstaller --noconfirm --onedir --windowed --collect-all customtkinter --name DS_VISION_PRO app.py
echo.
echo Build concluido.
echo Aplicativo: dist\DS_VISION_PRO\DS_VISION_PRO.exe
echo.
pause
