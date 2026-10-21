"""Inicializador de projeto Django existente; usa o Python instalado no PC."""
import json
import os
from pathlib import Path
import queue
import socket
import sqlite3
import subprocess
import sys
import threading
import time
import urllib.request
import webbrowser
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

CREATE_NO_WINDOW = getattr(subprocess, 'CREATE_NO_WINDOW', 0)


def python_for(project):
    for name in ('.venv', 'venv', 'env'):
        candidate = project / name / 'Scripts' / 'python.exe'
        if candidate.is_file():
            return [str(candidate)]
    if not getattr(sys, 'frozen', False):
        return [sys.executable]
    return ['py', '-3']


def run(command, project):
    result = subprocess.run(command, cwd=project, capture_output=True, text=True,
                            encoding='utf-8', errors='replace', creationflags=CREATE_NO_WINDOW)
    if result.returncode:
        raise RuntimeError((result.stderr or result.stdout)[-4000:])
    return result.stdout


def main():
    root = tk.Tk()
    root.title('VISAT — Inicializador leve')
    root.geometry('560x270')
    data = Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'VISAT_Leve'
    data.mkdir(parents=True, exist_ok=True)
    config = data / 'projeto.json'
    home = Path(sys.executable if getattr(sys, 'frozen', False) else __file__).resolve().parent
    project = home if (home / 'manage.py').is_file() else None
    if not project and config.exists():
        try:
            project = Path(json.loads(config.read_text(encoding='utf-8'))['project'])
        except (ValueError, KeyError):
            pass
    if not project or not (project / 'manage.py').is_file():
        selected = filedialog.askopenfilename(title='Selecione o manage.py do VISAT', filetypes=[('Projeto Django', 'manage.py')])
        if not selected:
            root.destroy()
            return
        project = Path(selected).resolve().parent
    if not (project / 'demandas').is_dir() or not (project / 'config' / 'settings.py').is_file():
        messagebox.showerror('VISAT', 'Selecione a pasta do projeto VISAT que contém manage.py e demandas.')
        root.destroy()
        return
    config.write_text(json.dumps({'project': str(project)}), encoding='utf-8')
    panel = ttk.Frame(root, padding=22)
    panel.pack(fill='both', expand=True)
    ttk.Label(panel, text='VISAT — Versão leve', font=('Segoe UI', 17, 'bold')).pack(anchor='w')
    status = tk.StringVar(value='Verificando Python, Django e banco...')
    ttk.Label(panel, textvariable=status, wraplength=510).pack(anchor='w', pady=15)
    ttk.Label(panel, text=str(project), wraplength=510).pack(anchor='w')
    events = queue.Queue()
    state = {'process': None, 'busy': True, 'url': None, 'log': None}
    button = ttk.Button(panel, text='Abrir no navegador', state='disabled', command=lambda: webbrowser.open(state['url']))
    button.pack(anchor='w', pady=15)

    def stop():
        if state['busy']:
            messagebox.showinfo('VISAT', 'Aguarde a inicialização terminar.')
            return
        proc = state['process']
        if proc and proc.poll() is None:
            if not messagebox.askokcancel('Encerrar', 'Salve os formulários no navegador antes de encerrar. Continuar?'):
                return
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
        if state['log']:
            state['log'].close()
        root.destroy()

    ttk.Button(panel, text='Encerrar', command=stop).pack(anchor='e')
    root.protocol('WM_DELETE_WINDOW', stop)

    def worker():
        try:
            py = python_for(project)
            run(py + ['-c', 'import django; print(django.get_version())'], project)
            run(py + ['manage.py', 'check'], project)
            # Não modifica esquema automaticamente. A atualização continua explícita.
            run(py + ['manage.py', 'migrate', '--check'], project)
            with socket.socket() as sock:
                sock.bind(('127.0.0.1', 0))
                port = sock.getsockname()[1]
            url = f'http://127.0.0.1:{port}/'
            state['log'] = open(data / 'servidor.log', 'w', encoding='utf-8')
            state['process'] = subprocess.Popen(py + ['manage.py', 'runserver', f'127.0.0.1:{port}', '--noreload'],
                cwd=project, stdout=state['log'], stderr=subprocess.STDOUT, creationflags=CREATE_NO_WINDOW)
            for _ in range(120):
                if state['process'].poll() is not None:
                    raise RuntimeError('Servidor encerrou. Consulte ' + str(data / 'servidor.log'))
                try:
                    with urllib.request.urlopen(url, timeout=1) as response:
                        if response.status == 200:
                            events.put(('ready', url))
                            return
                except Exception:
                    time.sleep(0.25)
            raise RuntimeError('O servidor não respondeu. Consulte ' + str(data / 'servidor.log'))
        except Exception as exc:
            proc = state['process']
            if proc and proc.poll() is None:
                proc.terminate()
                proc.wait(timeout=5)
            events.put(('error', str(exc) or 'Verifique as migrações: execute manage.py migrate no ambiente do projeto.'))

    def poll():
        try:
            kind, value = events.get_nowait()
            state['busy'] = False
            if kind == 'ready':
                state['url'] = value
                status.set('Sistema ligado: ' + value + '\nMantenha esta janela aberta.')
                button.configure(state='normal')
                webbrowser.open(value)
            else:
                status.set('Falha na inicialização.')
                messagebox.showerror('VISAT', value + '\n\nUse o ambiente .venv do projeto. Se houver migrações pendentes, faça backup do banco e execute manage.py migrate.')
        except queue.Empty:
            pass
        proc = state['process']
        if state['url'] and proc and proc.poll() is not None:
            status.set('Servidor encerrado. Consulte o log e reabra o inicializador.')
            button.configure(state='disabled')
            state['url'] = None
        root.after(200, poll)

    threading.Thread(target=worker, daemon=True).start()
    root.after(200, poll)
    root.mainloop()


if __name__ == '__main__':
    main()
