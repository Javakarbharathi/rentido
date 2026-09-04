"""
Development settings for Rentido project.
"""
from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']

# CORS for local frontend testing
CORS_ALLOW_ALL_ORIGINS = True

# Database: SQLite for effortless local development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
