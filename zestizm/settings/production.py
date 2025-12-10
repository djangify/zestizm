from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# ALLOWED_HOSTS
ALLOWED_HOSTS = [
    "zestizm.com",
    "www.zestizm.com",
    ".djangify.com",
    "65.108.89.200",
    "localhost",
    "127.0.0.1",
]

# Database in base.py is already set up to use environment variables

# CSRF Configuration
CSRF_TRUSTED_ORIGINS = [
    "https://zestizm.com",
    "https://www.zestizm.com",
    "https://65.108.89.200",
    "http://localhost",
    "http://127.0.0.1",
]

# CSRF Cookie Configuration
CSRF_COOKIE_SECURE = True

# Session Configuration
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = True  # Changed to True for production HTTPS
SESSION_COOKIE_HTTPONLY = True

# Security settings
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True  # Enable SSL redirect for production
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

# Additional security headers
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Email settings for production
EMAIL_HOST = env("EMAIL_HOST", default="localhost")  # noqa: F405
EMAIL_PORT = env("EMAIL_PORT", default=25)  # noqa: F405
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")  # noqa: F405
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")  # noqa: F405
EMAIL_USE_TLS = env("EMAIL_USE_TLS", default=False)  # noqa: F405
EMAIL_USE_SSL = env("EMAIL_USE_SSL", default=False)  # noqa: F405
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="zestizmlives@gmail.com")  # noqa: F405
SERVER_EMAIL = env("SERVER_EMAIL", default="zestizmlives@gmail.com")  # noqa: F405

# Admin configuration
ADMINS = [
    (
        env("ADMIN_NAME", default="Admin"),  # noqa: F405
        env("ADMIN_EMAIL", default="zestizmlives@gmail.com"),  # noqa: F405
    ),
]

# Static files optimization for production
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

SITE_URL = env("SITE_URL", default="https://www.zestizm.com")  # noqa: F405

# Logging info for logging_config.py file
from logging_config import LOGGING  # noqa: F401, E402
