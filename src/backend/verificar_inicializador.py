import tempfile
from pathlib import Path
import threading
import urllib.request
import sqlite3
from desktop_core import DatabaseLock, prepare, needs_admin, create_admin, make_server, backup_database

with tempfile.TemporaryDirectory() as tmp:
    db = Path(tmp) / 'db.sqlite3'
    lock = DatabaseLock(db)
    lock.acquire()
    try:
        DatabaseLock(db).acquire()
        raise AssertionError('second lock accepted')
    except RuntimeError:
        pass
    prepare(db)
    assert needs_admin()
    create_admin('teste_local', 'Teste-local-4938!')
    assert not needs_admin()
    from django.contrib.auth import authenticate
    assert authenticate(username='teste_local', password='Teste-local-4938!')
    original = sqlite3.connect(db).execute('SELECT username,password FROM auth_user').fetchall()
    backup = backup_database(db)
    assert sqlite3.connect(backup).execute('SELECT username,password FROM auth_user').fetchall() == original
    prepare(db)
    assert sqlite3.connect(db).execute('SELECT username,password FROM auth_user').fetchall() == original
    server = make_server()
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    url = f'http://127.0.0.1:{server.effective_port}'
    for path, needle in [('/login/', b'VISAT'), ('/static/demandas/css/app.css', b'.'), ('/static/admin/css/base.css', b'.')]:
        response = urllib.request.urlopen(url + path, timeout=10)
        assert response.status == 200 and needle in response.read(), path
    server.close()
    lock.release()
    lock.acquire()
    lock.release()
    print('PASS: migrations, new admin/login, existing credentials, backup, exclusive lock, HTTP, app/admin CSS, shutdown.')
