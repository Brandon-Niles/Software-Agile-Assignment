from .settings import *
import os

# Local development settings override
DEBUG = True

# Allow local hosts and Docker host
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost 127.0.0.1').split()

# Relax security for local development
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'
SECURE_SSL_REDIRECT = False

# Use file-based static files (WhiteNoise still works locally)
STATICFILES_DIRS = [BASE_DIR / 'static']

# Helpful default for running locally
print('Using settings_local (DEBUG=True)')
