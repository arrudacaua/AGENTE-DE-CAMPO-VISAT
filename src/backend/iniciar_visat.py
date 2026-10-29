"""Janela do inicializador; pode rodar como script ou executável PyInstaller."""
import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import queue
import sys
import threading
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from desktop_core import DatabaseLock, create_admin, default_data, make_server, needs_admin, prepare


def main():
    data = default_data()
    data.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(data / 'inicializador.log', maxBytes=1000000, backupCount=2, encoding='utf-8')
    logging.basicConfig(level=logging.INFO, handlers=[handler])
    # PyInstaller --windowed não oferece stdout/stderr.
    if sys.stdout is None:
        sys.stdout = open(data / 'runtime.log', 'a', encoding='utf-8')
    if sys.stderr is None:
        sys.stderr = sys.stdout
    root = tk.Tk()
    root.title('VISAT — Inicializador')
    root.geometry('570x310')
    root.resizable(False, False)
    panel = ttk.Frame(root, padding=24)
    panel.pack(fill='both', expand=True)
    ttk.Label(panel, text='Agente de Campo — VISAT', font=('Segoe UI', 17, 'bold')).pack(anchor='w')
    status = tk.StringVar(value='Preparando o sistema...')
    ttk.Label(panel, textvariable=status, wraplength=510).pack(anchor='w', pady=18)
    address = tk.StringVar()
    ttk.Label(panel, textvariable=address).pack(anchor='w')
    events = queue.Queue()
    state = {'server': None, 'lock': None, 'url': None, 'busy': True}
    config = data / 'inicializador.json'
    try:
        saved = json.loads(config.read_text(encoding='utf-8')) if config.exists() else {}
        database = Path(saved['database']) if saved.get('database') else None
        if database and not database.is_file():
            raise ValueError('O banco selecionado anteriormente não foi encontrado:\n' + str(database))
        if database is None:
            use_existing = messagebox.askyesnocancel('Banco de dados',
                'Você já tem um banco db.sqlite3 do VISAT?\n\nSim: selecionar seu banco atual. Pare o runserver antes.\nNão: criar uma instalação nova neste computador.\nCancelar: sair.', parent=root)
            if use_existing is None:
                root.destroy()
                return
            if use_existing:
                selected = filedialog.askopenfilename(title='Selecione seu db.sqlite3 do VISAT', filetypes=[('SQLite', '*.sqlite3'), ('Todos', '*.*')], parent=root)
                if not selected:
                    root.destroy()
                    return
                database = Path(selected).resolve()
                import sqlite3
                with sqlite3.connect(database.as_uri() + '?mode=ro', uri=True) as conn:
                    names = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                if not {'django_migrations', 'demandas_demanda', 'auth_user'} <= names:
                    raise ValueError('O arquivo selecionado não é um banco do VISAT.')
            else:
                database = data / 'db.sqlite3'
        lock = DatabaseLock(database)
        lock.acquire()
        state['lock'] = lock
    except Exception as exc:
        logging.exception('Falha ao selecionar banco')
        messagebox.showerror('VISAT', str(exc), parent=root)
        root.destroy()
        return

    ttk.Label(panel, text='Banco: ' + str(database), wraplength=510).pack(anchor='w', pady=12)
    open_button = ttk.Button(panel, text='Abrir no navegador', state='disabled', command=lambda: webbrowser.open(state['url']))
    open_button.pack(anchor='w')

    def stop():
        if state['busy']:
            messagebox.showinfo('VISAT', 'Aguarde a preparação terminar antes de encerrar.', parent=root)
            return
        if state['server'] and not messagebox.askokcancel('Encerrar VISAT', 'Salve o que estiver preenchendo no navegador antes de encerrar. Encerrar agora?', parent=root):
            return
        if state['server']:
            state['server'].close()
        if state['lock']:
            state['lock'].release()
        root.destroy()

    ttk.Button(panel, text='Encerrar', command=stop).pack(anchor='e', pady=8)
    root.protocol('WM_DELETE_WINDOW', stop)

    def prepare_worker():
        try:
            prepare(database)
            events.put(('prepared', needs_admin()))
        except Exception as exc:
            logging.exception('Falha na preparação')
            events.put(('error', str(exc)))

    def server_worker():
        try:
            server = make_server()
            state['server'] = server
            events.put(('running', f'http://127.0.0.1:{server.effective_port}/'))
            server.run()
        except Exception as exc:
            logging.exception('Falha no servidor')
            events.put(('error', str(exc)))

    def poll():
        try:
            kind, value = events.get_nowait()
        except queue.Empty:
            root.after(100, poll)
            return
        if kind == 'prepared':
            if value:
                while True:
                    username = simpledialog.askstring('Primeiro acesso', 'Crie o nome do administrador:', parent=root)
                    if username is None:
                        state['busy'] = False
                        stop()
                        return
                    password = simpledialog.askstring('Primeiro acesso', 'Senha (mínimo 8 caracteres):', show='*', parent=root)
                    confirm = simpledialog.askstring('Primeiro acesso', 'Repita a senha:', show='*', parent=root) if password is not None else None
                    if password is None or confirm is None:
                        state['busy'] = False
                        stop()
                        return
                    try:
                        if password != confirm:
                            raise ValueError('As senhas não conferem.')
                        create_admin(username, password)
                        break
                    except Exception as exc:
                        messagebox.showerror('Cadastro', str(exc), parent=root)
            config.write_text(json.dumps({'database': str(database)}, ensure_ascii=False), encoding='utf-8')
            threading.Thread(target=server_worker, daemon=True).start()
        elif kind == 'running':
            state.update(url=value, busy=False)
            address.set(value)
            status.set('Sistema ligado. Mantenha esta janela aberta enquanto usa o VISAT.')
            open_button.configure(state='normal')
            webbrowser.open(value)
        elif kind == 'error':
            state['busy'] = False
            status.set('Não foi possível iniciar. Veja o log em ' + str(data / 'inicializador.log'))
            messagebox.showerror('VISAT', value, parent=root)
        root.after(100, poll)

    threading.Thread(target=prepare_worker, daemon=True).start()
    root.after(100, poll)
    root.mainloop()


if __name__ == '__main__':
    main()
