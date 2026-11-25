import sqlite3
import tempfile
import threading
import urllib.request
from contextlib import closing
from pathlib import Path

from desktop_core import (
    DatabaseLock,
    prepare,
    needs_admin,
    create_admin,
    make_server,
    backup_database,
)


with tempfile.TemporaryDirectory() as tmp:
    db = Path(tmp) / 'db.sqlite3'
    lock = DatabaseLock(db)

    lock.acquire()

    try:
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

        assert authenticate(
            username='teste_local',
            password='Teste-local-4938!'
        )

        with closing(sqlite3.connect(db)) as connection:
            original = connection.execute(
                'SELECT username,password FROM auth_user'
            ).fetchall()

        backup = backup_database(db)

        with closing(sqlite3.connect(backup)) as connection:
            backup_users = connection.execute(
                'SELECT username,password FROM auth_user'
            ).fetchall()

        assert backup_users == original

        prepare(db)

        with closing(sqlite3.connect(db)) as connection:
            restored_users = connection.execute(
                'SELECT username,password FROM auth_user'
            ).fetchall()

        assert restored_users == original

        server = make_server()
        thread = threading.Thread(target=server.run, daemon=True)

        try:
            thread.start()

            url = f'http://127.0.0.1:{server.effective_port}'

            for path, needle in [
                ('/login/', b'VISAT'),
                ('/static/demandas/css/app.css', b'.'),
                ('/static/admin/css/base.css', b'.'),
            ]:
                with closing(
                    urllib.request.urlopen(url + path, timeout=10)
                ) as response:
                    content = response.read()
                    assert response.status == 200 and needle in content, path

        finally:
            server.task_dispatcher.shutdown(timeout=10)
            server.close()
            thread.join(timeout=10)

            if thread.is_alive():
                raise RuntimeError(
                    'O servidor HTTP não encerrou dentro do tempo esperado.'
                )

        lock.release()
        lock.acquire()

        print(
            'PASS: migrations, new admin/login, existing credentials, '
            'backup, exclusive lock, HTTP, app/admin CSS, shutdown.'
        )

    finally:
        lock.release()
