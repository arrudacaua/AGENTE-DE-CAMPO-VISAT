@echo off
setlocal
cd /d "%~dp0"
py -3 -m venv .build-leve
if errorlevel 1 goto erro
".build-leve\Scripts\python.exe" -m pip install PyInstaller==6.22.0
if errorlevel 1 goto erro
".build-leve\Scripts\python.exe" -m PyInstaller --noconfirm --clean --onefile --windowed --name Iniciar_VISAT_Leve VISAT_Leve.py
if errorlevel 1 goto erro
echo Pronto! Executavel em dist\Iniciar_VISAT_Leve.exe
explorer dist
pause
exit /b 0
:erro
echo Falha ao gerar. Envie uma foto desta janela.
pause
exit /b 1
