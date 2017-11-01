"""
Django settings for server project.

Generated by 'django-admin startproject' using Django 1.10.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""
import os
import datetime
from dj_git_submodule import submodule

try:
  with open('/env', 'r') as f:
    env = f.read().strip()
    f.close()
except FileNotFoundError:
  env = 'dev'

if env in ['production', 'homolog']:
  submodule.prop = '__name__' # Gotta read __name__ instead of __file__ if running through gunicorn

# Submodules
submodule.add(submodule.locate('django-*'))


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '0o55a_%0s2t6)+j9+7wj5e^-z=t0ql#7-+ncrtnn8q(kl+em6v'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [".localhost"]


# Application definition
from ovp import get_core_apps
INSTALLED_APPS = get_core_apps() + [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'rest_framework',
    'rest_framework_jwt',
    'rest_framework_swagger',
    'debug_toolbar',
    'email_log',
    'docs',
    'channels.pv',
    'ckeditor'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'ovp.apps.channels.middlewares.channel.ChannelRecognizerMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'ovp.apps.channels.middlewares.channel.ChannelProcessorMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'server.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'server.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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


# Rest framework

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'PAGINATE_BY_PARAM': 'page_size',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'ovp.apps.users.auth.jwt_authenticator.ChannelJSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    )
}


CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline'],
            ['Link', 'Unlink'],
        ]
    }
}

# User models

AUTH_USER_MODEL = 'users.User'
SILENCED_SYSTEM_CHECKS = ["auth.E003", "auth.W004"]


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

# Email

EMAIL_HOST='smtp.zoho.com'
EMAIL_PORT=465
EMAIL_HOST_USER=os.environ.get('EMAIL_HOST_USER', None)
EMAIL_HOST_PASSWORD=os.environ.get('EMAIL_HOST_PASSWORD', None)
DEFAULT_FROM_EMAIL="Atados <{}>".format(EMAIL_HOST_USER)
EMAIL_USE_SSL=True
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/tmp/atados-ovp-messages'


# Media

DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Haystack

HAYSTACK_CONNECTIONS = {
  'default': {
    'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
    'PATH': os.path.join('/tmp', 'atados_whoosh_index'),
  },
}

# Authentication backends

AUTHENTICATION_BACKENDS = ["ovp.apps.users.auth.backends.ChannelBasedAuthentication"]

# JWT Auth

JWT_AUTH = {
  'JWT_EXPIRATION_DELTA': datetime.timedelta(hours=24),
}

# Cors headers

from corsheaders.defaults import default_headers
CORS_ALLOW_HEADERS = default_headers + (
  'x-unauthenticated-upload',
  'x-ovp-channel',
)

# Jet

JET_INDEX_DASHBOARD = 'ovp.admin.jet.dashboard.CustomIndexDashboard'

if env == 'production':
  from .production import *
else:
  from .dev import *
