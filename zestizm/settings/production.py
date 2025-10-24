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
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="djangify@djangify.com")  # noqa: F405
SERVER_EMAIL = env("SERVER_EMAIL", default="djangify@djangify.com")  # noqa: F405

# Admin configuration
ADMINS = [
    (
        env("ADMIN_NAME", default="Admin"),  # noqa: F405
        env("ADMIN_EMAIL", default="djangify@djangify.com"),  # noqa: F405
    ),
]

# Static files optimization for production
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

SITE_URL = env("SITE_URL", default="https://www.zestizm.com")  # noqa: F405

# Logging configuration
# LOG_DIR = os.path.join(BASE_DIR, "logs")
# os.makedirs(LOG_DIR, exist_ok=True)

# LOGGING = {
#     "version": 1,
#     "disable_existing_loggers": False,
#     "formatters": {
#         "verbose": {
#             "format": "[{asctime}] {levelname} {name} ({lineno}) — {message}",
#             "style": "{",
#         },
#         "simple": {
#             "format": "{levelname} {message}",
#             "style": "{",
#         },
#     },
#     "handlers": {
#         # Write all warnings and errors to file
#         "file": {
#             "level": "WARNING",
#             "class": "logging.FileHandler",
#             "filename": os.path.join(LOG_DIR, "django.log"),
#             "formatter": "verbose",
#         },
#         # Email admins on errors
#         "mail_admins": {
#             "level": "ERROR",
#             "class": "django.utils.log.AdminEmailHandler",
#             "include_html": True,
#         },
#         # Optional: log to console during development
#         "console": {
#             "level": "INFO",
#             "class": "logging.StreamHandler",
#             "formatter": "simple",
#         },
#     },
#     "loggers": {
#         # Django core
#         "django": {
#             "handlers": ["file", "mail_admins"],
#             "level": "WARNING",
#             "propagate": True,
#         },
#         # Log database queries or silent fails if needed
#         "django.db.backends": {
#             "handlers": ["file"],
#             "level": "ERROR",  # Change to DEBUG if you want all queries logged
#             "propagate": False,
#         },
#         # Your own apps
#         "core": {"handlers": ["file"], "level": "INFO", "propagate": True},
#         "shop": {"handlers": ["file"], "level": "INFO", "propagate": True},
#         "accounts": {"handlers": ["file"], "level": "INFO", "propagate": True},
#         "blog": {"handlers": ["file"], "level": "INFO", "propagate": True},
#     },
# }
