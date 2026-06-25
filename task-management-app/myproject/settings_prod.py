from .settings import *
import os

# Production/staging settings override
DEBUG = False

# Read ALLOWED_HOSTS from env in production
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '127.0.0.1').split()

# Ensure secure cookies in prod
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'

# Security recommended in production
SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', '1') in ('1', 'true', 'yes')
