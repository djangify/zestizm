from pathlib import Path
import os
import environ

# Initialize environment variables
env = environ.Env()
BASE_DIR = Path(__file__).resolve().parent.parent.parent
# Read the .env file
env.read_env(os.path.join(BASE_DIR, ".env"))

# SECRET_KEY
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.redirects",
    "django.contrib.sitemaps",
    "core",
    "blog",
    "accounts",
    "shop",
    "infopages",
    "tinymce",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "zestizm.middleware.BlockWPExploitAttemptsMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "zestizm.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.homepage_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "zestizm.wsgi.application"

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DATABASE_NAME"),
        "USER": env("DATABASE_USER"),
        "PASSWORD": env("DATABASE_PASSWORD"),
        "HOST": env("DATABASE_HOST", default="localhost"),
        "PORT": env("DATABASE_PORT", default="5432"),
    }
}

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Only include if you want to use WhiteNoise for static files
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

WHITENOISE_MAX_AGE = 31536000  # 1 year

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

SITE_ID = 1


# Login URLs
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/accounts/dashboard/"
LOGOUT_REDIRECT_URL = "/"

# Session and CORS settings
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7  # 1 week
SESSION_SAVE_EVERY_REQUEST = True
CORS_SUPPORT_CREDENTIALS = True

DEFAULT_FROM_EMAIL = "noreply@djangify.com"
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "accounts.authentication.EmailAuthBackend",
]

# Stripe settings
STRIPE_PUBLISHABLE_KEY = env("STRIPE_PUBLISHABLE_KEY", default="pk_test_placeholder")
STRIPE_SECRET_KEY = env("STRIPE_SECRET_KEY", default="sk_test_placeholder")
STRIPE_WEBHOOK_SECRET = env("STRIPE_WEBHOOK_SECRET", default="whsec_placeholder")
CART_SESSION_ID = "cart"


# Email verification settings
EMAIL_HOST = env("EMAIL_HOST", default="")
EMAIL_PORT = env("EMAIL_PORT", default=587)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = env("EMAIL_USE_TLS", default=True)
EMAIL_USE_SSL = env.bool("EMAIL_USE_SSL", default=False)
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@djangify.com")
SUPPORT_EMAIL = env("SUPPORT_EMAIL", default="noreply@djangify.com")


TINYMCE_DEFAULT_CONFIG = {
    "height": 650,
    "width": "auto",
    "cleanup_on_startup": True,
    "custom_undo_redo_levels": 20,
    "selector": "textarea",
    "theme": "silver",
    "plugins": """
        textcolor save link image media preview codesample contextmenu
        table code lists fullscreen insertdatetime nonbreaking
        contextmenu directionality searchreplace wordcount visualblocks
        visualchars code fullscreen autolink lists charmap print hr
        anchor pagebreak
        """,
    "toolbar1": """
        fullscreen preview bold italic underline | fontselect,
        fontsizeselect | forecolor backcolor | alignleft alignright |
        aligncenter alignjustify | indent outdent | bullist numlist table |
        | link image media | codesample |
        """,
    "toolbar2": """
        visualblocks visualchars |
        charmap hr pagebreak nonbreaking anchor | code |
        """,
    "contextmenu": "formats | link image",
    "menubar": True,
    "statusbar": True,
}
