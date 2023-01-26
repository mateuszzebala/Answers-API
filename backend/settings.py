from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-ro5yxh#i_va(!n5mpg9p1vgxh*t=+zv3b08k7vxf8_rjxjfrl%'

DEBUG = True

ON_SERVER = False

CORS_ALLOW_CREDENTIALS = True

if not ON_SERVER:
    ALLOWED_HOSTS=['*']
    CSRF_TRUSTED_ORIGINS = ['http://localhost:3000']
    CORS_ORIGIN_WHITELIST = ['http://localhost:3000']
    HOSTNAME_FRONT = 'http://localhost:3000/'
    HOSTNAME_BACK = 'http://localhost:8000/'
else:
    ALLOWED_HOSTS=['api.zmateusz.site', 'www.api.zmateusz.site', '*.zmateusz.site', 'localhost']
    CSRF_TRUSTED_ORIGINS = ['https://zmateusz.site']
    CORS_ORIGIN_WHITELIST = ['https://zmateusz.site']
    HOSTNAME_FRONT = 'https://zmateusz.site'
    HOSTNAME_BACK = 'https://api.zmateusz.site'

EMAIL_USE_TLS = True
EMAIL_HOST = 's190.cyber-folks.pl'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'email@mateuszzebala.pl'
EMAIL_HOST_PASSWORD = '$(MaT).#10'
X_FRAME_OPTIONS = "SAMEORIGIN"
SILENCED_SYSTEM_CHECKS = ["security.W019"]
INSTALLED_APPS = [

    "admin_interface",
    "colorfield",
    'main.apps.MainConfig',
    'corsheaders',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'
STATIC_ROOT = 'static/'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [(os.path.join(BASE_DIR, 'templates')),],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
