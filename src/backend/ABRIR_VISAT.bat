@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" VISAT_Leve.py
) else (
    py -3 VISAT_Leve.py
)
if errorlevel 1 pause
