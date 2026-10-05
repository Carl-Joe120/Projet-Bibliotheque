import os
from pathlib import Path
import socket
from django.urls import reverse_lazy as reverse_Lazy

BASE_DIR = Path(__file__).resolve().parent.parent

STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = '/media/'



def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
    except Exception:
        ip = "127.0.0.1"
    return ip

LOCAL_IP = get_local_ip()



SECRET_KEY = 'django-insecure-p^1sfx8)f_r5@e2varlj2w41y!-g3%7fmpnb6*ma!jm@-1t*_&'

DEBUG = True

ALLOWED_HOSTS = ['*']



CSRF_TRUSTED_ORIGINS = [
    f"http://{LOCAL_IP}:8000",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]

CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SAMESITE = "Lax"



SITE_URL = f"http://{LOCAL_IP}:8000"


# ===============================
# AUTH
# ===============================
AUTH_USER_MODEL = 'utilisateurs.Utilisateur'
AUTH_PASSWORD_VALIDATORS = []


# ===============================
# APPS
# ===============================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'employes',
    'livres',
    'notifications',
    'recommandations',
    'reservation',
    'tableau_de_bord',
    'utilisateurs',

    'crispy_forms',
    'widget_tweaks',
    'django_cleanup.apps.CleanupConfig',
]


# ===============================
# MIDDLEWARE
# ===============================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ===============================
# URL CONFIG
# ===============================
ROOT_URLCONF = 'bibliotheque_Project.urls'

LOGIN_URL = 'loginview'
LOGIN_REDIRECT_URL = 'index'
LOGOUT_REDIRECT_URL = 'loginview'


# ===============================
# TEMPLATES
# ===============================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'notifications.context_processors.notifications_nav',
            ],
        },
    },
]

WSGI_APPLICATION = 'bibliotheque_Project.wsgi.application'


# ===============================
# DATABASE
# ===============================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'bibliotheque',
        'USER': 'user',
        'PASSWORD': 'password',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}


# ===============================
# EMAIL (SAN CHANJMAN)
# ===============================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'bibliothequemichelt@gmail.com'
EMAIL_HOST_PASSWORD = 'srlc fsat akpn pbht'
DEFAULT_FROM_EMAIL = 'Bbliotheque Michel Tardieu <bibliothequemichelt@gmail.com>'


# ===============================
# LANG
# ===============================
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
