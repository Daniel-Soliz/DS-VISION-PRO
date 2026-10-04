@echo off
title DS VISION PRO - Criar atalho
if not exist "dist\DS_VISION_PRO\DS_VISION_PRO.exe" (
  echo O aplicativo ainda nao foi gerado.
  echo Execute BUILD_EXE.bat primeiro.
  pause
  exit /b 1
)

powershell -NoProfile -Command "$desktop=[Environment]::GetFolderPath('Desktop'); $target=(Resolve-Path '.\dist\DS_VISION_PRO\DS_VISION_PRO.exe').Path; $shell=New-Object -ComObject WScript.Shell; $shortcut=$shell.CreateShortcut((Join-Path $desktop 'DS VISION PRO.lnk')); $shortcut.TargetPath=$target; $shortcut.WorkingDirectory=(Split-Path $target); $shortcut.Save()"

echo.
echo Atalho DS VISION PRO criado na Area de Trabalho.
pause
