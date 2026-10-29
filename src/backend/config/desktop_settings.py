import os
from .settings import *

DEBUG = False
SECRET_KEY = os.environ['VISAT_SECRET']
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': os.environ['VISAT_DATABASE']}}
STATIC_URL = '/static/'
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
