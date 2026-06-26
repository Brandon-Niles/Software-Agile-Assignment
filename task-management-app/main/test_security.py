from django.test import TestCase
from django.conf import settings

class SecurityConfigTests(TestCase):
    def test_csrf_middleware_enabled(self):
        self.assertIn('django.middleware.csrf.CsrfViewMiddleware', settings.MIDDLEWARE)

    def test_security_middleware_present(self):
        self.assertIn('django.middleware.security.SecurityMiddleware', settings.MIDDLEWARE)
        self.assertIn('django.middleware.clickjacking.XFrameOptionsMiddleware', settings.MIDDLEWARE)
