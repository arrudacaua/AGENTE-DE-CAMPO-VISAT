"""Executado pelo GERAR_EXECUTAVEL.bat em ambiente isolado."""
from pathlib import Path
import os
import subprocess
import sys
import zipfile

base = Path(__file__).resolve().parent
os.chdir(base)
if sys.platform != 'win32':
    raise SystemExit('Gere o executável em um computador Windows.')
import tkinter
import django
import django.contrib.admin
print('Gerando executável. Isso pode levar alguns minutos...', flush=True)
args = [sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean', '--onedir', '--windowed',
        '--name', 'Iniciar_VISAT', '--collect-all', 'django', '--collect-all', 'waitress',
        '--collect-all', 'whitenoise', '--collect-submodules', 'demandas',
        '--collect-submodules', 'config', '--add-data', 'templates;templates',
        '--add-data', 'static;static', 'iniciar_visat.py']
subprocess.run(args, check=True)
folder = base / 'dist' / 'Iniciar_VISAT'
(folder / 'LEIA_PRIMEIRO.txt').write_text(
    'Execute Iniciar_VISAT.exe e mantenha a janela aberta.\n'
    'Na primeira abertura, escolha seu banco existente ou crie uma instalação nova.\n'
    'Não precisa instalar Python no computador de destino.\n'
    'Copie esta pasta INTEIRA, incluindo _internal.\n'
    'Dados novos: %LOCALAPPDATA%\\VISAT. Cada PC tem seu próprio banco.\n'
    'Para encerrar, salve no navegador e use Encerrar na janela.\n', encoding='utf-8')
archive = base / 'dist' / 'VISAT_Para_Distribuir.zip'
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as out:
    for path in folder.rglob('*'):
        if path.is_file():
            out.write(path, path.relative_to(folder.parent))
print('\nPronto! Envie dist\\VISAT_Para_Distribuir.zip para a galera.', flush=True)
os.startfile(str(base / 'dist'))
