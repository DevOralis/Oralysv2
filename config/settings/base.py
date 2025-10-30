import os
from pathlib import Path
import environ

# ─── Répertoire de base ───────────────────────────────────────────────────────
# BASE_DIR pointe sur la racine du projet (le dossier qui contient manage.py)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ─── Chargement des variables d'environnement ─────────────────────────────────
env = environ.Env()
environ.Env.read_env(BASE_DIR / '.env')

# ─── Sécurité ─────────────────────────────────────────────────────────────────
SECRET_KEY = env('SECRET_KEY', default='dev-insecure-secret-key-change-me')
#SECRET_KEY = env('SECRET_KEY')
# Mode debug (à passer à False en production)
DEBUG = env.bool('DEBUG', default=False)

# Hôtes autorisés (ajustez en production)
ALLOWED_HOSTS = ['*']
# ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*'])
AUTH_USER_MODEL = 'home.User'
AUTHENTICATION_BACKENDS = ['apps.home.backends.CustomUserBackend']
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 1209600  # 2 weeks


# ─── Applications installées ──────────────────────────────────────────────────
INSTALLED_APPS = [
    # Django contrib
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'phonenumber_field',
    'django_countries',
    'apps.home',
    'apps.dashboard.apps.DashboardConfig',
    'apps.hr',
    'apps.formation',
    'apps.purchases',
    'apps.inventory',
    'apps.pharmacy',
    'apps.patient',
    'apps.therapeutic_activities',
    'apps.recruitment',
    'apps.Restauration',
    'apps.hosting',
    'apps.parcauto',
    'apps.maintenance',
    'apps.demandes',
    'widget_tweaks',
    
    
]


# ─── Middleware ───────────────────────────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.hr.middleware.HRAccessMiddleware',
    'apps.home.views.RestrictUnauthorizedAccessMiddleware'
]


# ─── URLs et WSGI ─────────────────────────────────────────────────────────────
ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'


# ─── Templates ────────────────────────────────────────────────────────────────
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ BASE_DIR / 'templates_global',
                  BASE_DIR / 'apps/home/templates',
                  BASE_DIR / 'apps/dashboard/templates',
                  BASE_DIR / 'apps/inventory/templates',
                  BASE_DIR / 'apps/purchases/templates',
                  BASE_DIR / 'apps/recruitment/templates',
                  BASE_DIR / 'apps/hr/templates',
                  BASE_DIR / 'apps/formation/templates',
                  BASE_DIR / 'apps/pharmacy/templates',
                  BASE_DIR / 'apps/patient/templates',
                  BASE_DIR / 'apps/therapeutic_activities/templates',
                  BASE_DIR / 'apps/hosting/templates',
                  BASE_DIR / 'apps/Restauration/templates',
                  BASE_DIR / 'apps/parcauto/templates',
                ],

        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.home.context_processors.user_permissions',
            ],
        },
    },
]

# ─── Base de données PostgreSQL ───────────────────────────────────────────────
#DATABASES = {
   # 'default': {
    #    'ENGINE':   env('DB_ENGINE', default='django.db.backends.sqlite3'),
    #    'NAME':     env('DB_NAME',  default='db.sqlite3'),
   #     'USER':     env('DB_USER',  default=''),
   #     'PASSWORD': env('DB_PASSWORD', default=''),
    #    'HOST':     env('DB_HOST',  default=''),
   #     'PORT':     env('DB_PORT',  default=''),
    #}
#}
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'miniERP',
        'USER': 'root',
        'PASSWORD': '12345',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


# ─── Authentification ─────────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator' },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator' },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator' },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator' },
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}


# ─── Internationalisation ─────────────────────────────────────────────────────
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE     = 'Africa/Casablanca'
USE_I18N      = True
USE_L10N      = True
USE_TZ        = True


# ─── Static & Media ───────────────────────────────────────────────────────────
STATIC_URL = '/static/'
STATICFILES_DIRS = [ BASE_DIR / 'static_global' ]
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

