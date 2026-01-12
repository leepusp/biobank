from pathlib import Path

# =========================
# BASE
# =========================
BASE_DIR = Path(__file__).resolve().parent.parent


# =========================
# SEGURANÇA / DEBUG
# =========================
SECRET_KEY = "dev-secret-key"  # ⚠️ trocar em produção
DEBUG = True
ALLOWED_HOSTS = []


# =========================
# APLICAÇÕES
# =========================
INSTALLED_APPS = [
    # Django core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Utilitários
    "django_extensions",

    # APIs / filtros
    "rest_framework",
    "django_filters",

    # App principal
    "core",
]


# =========================
# MIDDLEWARE
# =========================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# =========================
# URLS / WSGI
# =========================
ROOT_URLCONF = "biobank.urls"
WSGI_APPLICATION = "biobank.wsgi.application"


# =========================
# TEMPLATES
# =========================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",

        # ROOT dos templates (internal + public)
        "DIRS": [
            BASE_DIR / "core" / "interfaces" / "web",
        ],

        "APP_DIRS": True,

        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# =========================
# STATIC FILES
# =========================
STATIC_URL = "/static/"

# Raiz única de assets (internal + public)
STATICFILES_DIRS = [
    BASE_DIR / "core" / "interfaces" / "web",
]


# =========================
# MEDIA (UPLOADS)
# =========================
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# =========================
# DATABASE
# =========================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# =========================
# INTERNACIONALIZAÇÃO
# =========================
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True


# =========================
# AUTENTICAÇÃO
# =========================
LOGIN_URL = "/login/"
LOGOUT_URL = "/logout/"

# Workspace como landing page
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/login/"


# =========================
# DEFAULTS
# =========================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

