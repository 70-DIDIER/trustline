"""
Django settings for the Trustline (TOGOSHIELD) backend.

Configuration is driven by environment variables through ``django-environ``.

* DATABASE_URL points at **PostgreSQL** — it is the only supported engine.
  Copy ``.env.example`` to ``.env`` and adapt the credentials.
* CACHE_URL defaults to an in-memory cache (Redis used when the URL is
  provided). DRF throttling works with either backend.
"""
from datetime import timedelta
from pathlib import Path

import environ
from corsheaders.defaults import default_headers
from django.core.exceptions import ImproperlyConfigured

# ---------------------------------------------------------------------------
# Paths & environment
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, True),
    SECRET_KEY=(str, "dev-insecure-key-change-me-in-production"),
    ALLOWED_HOSTS=(list, ["*"]),
    CORS_ALLOW_ALL_ORIGINS=(bool, True),
)

# Read a local .env file if present (not required — defaults cover local dev).
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")

# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "drf_spectacular",
    "corsheaders",
]

LOCAL_APPS = [
    "apps.core",
    "apps.scoring",
    "apps.appareils",
    "apps.numeros",
    "apps.signalements",
    # Custom AppConfig sets label="messages_app" to avoid clashing with
    # django.contrib.messages (see apps/messages/apps.py).
    "apps.messages.apps.MessagesConfig",
    "apps.liens",
    "apps.historique",
    "apps.veille",
    "apps.vigie",
    "apps.ussd",
    "apps.bot",
    "apps.moderation",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# ---------------------------------------------------------------------------
# Database — PostgreSQL only (no SQLite fallback)
# ---------------------------------------------------------------------------
DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default="postgres://postgres:postgres@localhost:5432/trustline",
    )
}
DATABASES["default"].setdefault("CONN_MAX_AGE", env.int("CONN_MAX_AGE", default=60))

if not DATABASES["default"]["ENGINE"].endswith("postgresql"):
    raise ImproperlyConfigured(
        "Trustline requires PostgreSQL. Set DATABASE_URL to a postgres:// URL "
        f"(got ENGINE={DATABASES['default']['ENGINE']!r})."
    )

# ---------------------------------------------------------------------------
# Cache — Redis when CACHE_URL is set, in-memory fallback otherwise
# ---------------------------------------------------------------------------
CACHES = {
    "default": env.cache(
        "CACHE_URL",
        default="locmemcache://trustline",
    )
}

# ---------------------------------------------------------------------------
# Password validation
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Africa/Lome"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static files
# ---------------------------------------------------------------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Django REST Framework + throttling (rate limiting via cache backend)
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ),
    "DEFAULT_THROTTLE_RATES": {
        # Public endpoints are rate-limited; backed by whatever CACHES defines.
        "anon": env("THROTTLE_ANON", default="60/min"),
        "user": env("THROTTLE_USER", default="240/min"),
    },
    # Pagination for admin list endpoints (public APIViews return dicts, unaffected).
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=8),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Trustline API",
    "DESCRIPTION": (
        "API de la plateforme **Trustline** (TOGOSHIELD) — détection, prévention "
        "et signalement communautaire des arnaques numériques au Togo.\n\n"
        "**Format de verdict normalisé** (partout) : `score` (0-100), "
        "`niveau_risque` (`faible` | `suspect` | `eleve`), `indices` (liste "
        "explicative), `recommandation` (conseil court).\n\n"
        "Multicanal : Web/API, extension navigateur (liens), USSD, bot de "
        "messagerie et WhatsApp (Gupshup)."
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "CONTACT": {"name": "Équipe Trustline", "email": "contact@trustline.tg"},
    "TAGS": [
        {"name": "Système", "description": "Santé du service."},
        {"name": "Appareils", "description": "Identité anonyme de l'appareil mobile (X-Device-Id) et profil."},
        {"name": "Accueil", "description": "Agrégat unique alimentant l'écran d'accueil de l'application mobile."},
        {"name": "Historique", "description": "Historique des vérifications d'un appareil."},
        {"name": "Alertes", "description": "Campagnes d'arnaque en cours (veille communautaire)."},
        {"name": "Conseils", "description": "Fiches de prévention servies à l'application."},
        {"name": "Mode Vigie", "description": "Catalogue de signaux analysés localement + sessions d'écoute."},
        {"name": "Numéros", "description": "Vérification et consultation des numéros (liste blanche + réputation)."},
        {"name": "Messages", "description": "Analyse de SMS / messages par le moteur de détection."},
        {"name": "Liens", "description": "Analyse d'URL / sites (extension navigateur)."},
        {"name": "Signalements", "description": "Signalement communautaire et mise à jour de la réputation."},
        {"name": "USSD", "description": "Parcours USSD simplifié (menu vérifier / signaler / conseils)."},
        {"name": "Bot", "description": "Webhook bot générique (verdict conversationnel)."},
        {"name": "WhatsApp (Gupshup)", "description": "Webhook WhatsApp entrant via Gupshup Sandbox."},
        {"name": "Statistiques", "description": "Agrégats pour le dashboard."},
    ],
    # Several serializers expose the same choice sets under different field
    # names; pin the generated enum names so clients stay stable.
    "ENUM_NAME_OVERRIDES": {
        "CategorieArnaqueEnum": "apps.core.constants.CategorieCode.choices",
        "NiveauRisqueEnum": "apps.core.constants.NiveauRisque.choices",
    },
    "SWAGGER_UI_SETTINGS": {
        "docExpansion": "list",
        "defaultModelsExpandDepth": 0,
        "persistAuthorization": True,
    },
}

# ---------------------------------------------------------------------------
# CORS (extension Chrome + Web front-end). Permissive in dev.
# ---------------------------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = env("CORS_ALLOW_ALL_ORIGINS")

# The mobile app identifies itself with an anonymous device UUID.
CORS_ALLOW_HEADERS = list(default_headers) + ["x-device-id", "x-app-version"]

# ---------------------------------------------------------------------------
# Sécurité production (HTTPS)
# ---------------------------------------------------------------------------
# La plupart de ces réglages s'ACTIVENT automatiquement quand DEBUG=False, et
# restent NEUTRES en dev local (DEBUG=True). Chacun est surchargeable via .env.
_PROD = not DEBUG

# Origines de confiance pour le CSRF (ex. connexion à /admin/ derrière HTTPS).
# Django 5 exige le schéma : "https://api.mondomaine.tg".
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

# Derrière Nginx : faire confiance à l'en-tête X-Forwarded-Proto pour que Django
# sache que la requête d'origine est en HTTPS (évite les boucles de redirection).
if env.bool("USE_X_FORWARDED_PROTO", default=_PROD):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Rediriger tout le trafic HTTP vers HTTPS (en prod).
# ⚠️ À laisser False tant que le certificat HTTPS n'est pas encore posé (certbot).
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=_PROD)

# Cookies transmis uniquement en HTTPS.
SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=_PROD)
CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE", default=_PROD)

# HSTS : forcer HTTPS côté navigateur (1 an en prod). 0 = désactivé (dev).
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=31536000 if _PROD else 0)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", default=_PROD)
SECURE_HSTS_PRELOAD = env.bool("SECURE_HSTS_PRELOAD", default=_PROD)

# Durcissements généraux (sûrs dans tous les cas).
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = "DENY"

# ---------------------------------------------------------------------------
# Trustline detection thresholds (shared by scoring + reputation)
# ---------------------------------------------------------------------------
SEUIL_SUSPECT = env.int("SEUIL_SUSPECT", default=30)   # score >= this -> "suspect"
SEUIL_ELEVE = env.int("SEUIL_ELEVE", default=70)       # score >= this -> "eleve"

# Modèle ML optionnel (voir apps/scoring/ml.py + ml/train_model.py).
# Vide = moteur en mode règles uniquement. Renseigner le chemin d'un .joblib
# entraîné pour activer le mélange règles + ML automatiquement.
ML_MODEL_PATH = env("ML_MODEL_PATH", default="")
ML_POIDS = env.float("ML_POIDS", default=0.5)  # part du ML dans le mélange (0..1)

# ---------------------------------------------------------------------------
# Gupshup WhatsApp (Sandbox) — webhook /api/webhook/gupshup/
# ---------------------------------------------------------------------------
GUPSHUP_API_KEY = env("GUPSHUP_API_KEY", default="")
GUPSHUP_SOURCE = env("GUPSHUP_SOURCE", default="917834811114")  # sandbox number
GUPSHUP_APP_NAME = env("GUPSHUP_APP_NAME", default="TrustLine")
GUPSHUP_API_URL = env("GUPSHUP_API_URL", default="https://api.gupshup.io/wa/api/v1/msg")
GUPSHUP_TIMEOUT = env.int("GUPSHUP_TIMEOUT", default=10)  # seconds for outbound call

# ---------------------------------------------------------------------------
# Logging — console output so webhook/debug logs are visible during the demo
# ---------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "[{levelname}] {name}: {message}", "style": "{"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "simple"},
    },
    "loggers": {
        # Trustline application logs (webhook Gupshup, etc.).
        "trustline": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
}
