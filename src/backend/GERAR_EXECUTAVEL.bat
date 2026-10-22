@echo off
setlocal
cd /d "%~dp0"
echo Gerador do VISAT para Windows
 echo Feche o VISAT antes de gerar novamente.
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -m venv .venv-build
) else (
    py -3.13 -m venv .venv-build
)
if errorlevel 1 goto erro
".venv-build\Scripts\python.exe" -m pip install -r requirements-exe.txt
if errorlevel 1 goto erro
".venv-build\Scripts\python.exe" build_windows.py
if errorlevel 1 goto erro
echo.
echo Concluido. O ZIP para enviar esta na pasta dist.
pause
exit /b 0
:erro
echo.
echo Falha. Envie uma foto desta janela para verificar o erro.
echo E necessario Python 3.13 instalado e internet para gerar.
pause
exit /b 1
