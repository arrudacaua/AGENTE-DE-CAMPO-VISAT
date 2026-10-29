"""Runtime local: dados fora do pacote, backup e servidor somente loopback."""
import os
import secrets
import sqlite3
import sys
from datetime import datetime
from pathlib import Path


def resources():
    return Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent))


def default_data():
    return Path(os.environ.get('LOCALAPPDATA', Path.home() / '.local' / 'share')) / 'VISAT'


class DatabaseLock:
    def __init__(self, database):
        self.path = Path(str(database) + '.visat.lock')
        self.handle = None

    def acquire(self):
        self.handle = self.path.open('a+b')
        self.handle.seek(0)
        self.handle.write(b'0')
        self.handle.flush()
        self.handle.seek(0)
        try:
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(self.handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            self.handle.close()
            self.handle = None
            raise RuntimeError('Este banco já está aberto em outro inicializador VISAT.')

    def release(self):
        if self.handle:
            self.handle.close()
            self.handle = None


def backup_database(database):
    database = Path(database)
    if not database.exists():
        return None
    folder = database.parent / 'backups_visat'
    folder.mkdir(exist_ok=True)
    target = folder / ('db_' + datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '.sqlite3')
    with sqlite3.connect(database) as source, sqlite3.connect(target) as dest:
        source.backup(dest)
    return target


def prepare(database):
    database = Path(database).resolve()
    database.parent.mkdir(parents=True, exist_ok=True)
    secret_path = database.parent / '.visat_secret'
    if not secret_path.exists():
        secret_path.write_text(secrets.token_urlsafe(48), encoding='utf-8')
    os.environ['VISAT_DATABASE'] = str(database)
    os.environ['VISAT_SECRET'] = secret_path.read_text(encoding='utf-8').strip()
    os.environ['DJANGO_SETTINGS_MODULE'] = 'config.desktop_settings'
    import django
    django.setup()
    from django.core.management import call_command
    from django.db import connection
    from django.db.migrations.executor import MigrationExecutor
    executor = MigrationExecutor(connection)
    plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
    connection.close()
    if plan:
        backup_database(database)
        call_command('migrate', interactive=False, verbosity=0)
    call_command('check', verbosity=0)


def needs_admin():
    from django.contrib.auth import get_user_model
    return not get_user_model().objects.exists()


def create_admin(username, password):
    from django.contrib.auth import get_user_model
    from django.contrib.auth.password_validation import validate_password
    if not needs_admin():
        raise ValueError('O banco já possui usuários. Use a conta existente.')
    username = username.strip()
    if not username:
        raise ValueError('Informe o nome de usuário.')
    validate_password(password)
    get_user_model().objects.create_superuser(username=username, password=password)


def make_server():
    from django.core.wsgi import get_wsgi_application
    from whitenoise import WhiteNoise
    from waitress import create_server
    import django.contrib.admin
    app = WhiteNoise(get_wsgi_application(), root=str(resources() / 'static'), prefix='/static/')
    admin_static = Path(django.contrib.admin.__file__).parent / 'static'
    app.add_files(str(admin_static), prefix='/static/')
    # Porta atribuída pelo SO: não conflita com runserver ou outro aplicativo.
    return create_server(app, host='127.0.0.1', port=0, threads=4)
