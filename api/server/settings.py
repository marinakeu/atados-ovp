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

ALLOWED_HOSTS = [".localhost", "api.beta.atados.com.br"]


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
    'django_inlinecss',
    'rest_framework',
    'rest_framework_jwt',
    'debug_toolbar',
    'email_log',
    'docs',
    'channels.pv',
    'channels.default',
    'ckeditor',
    'oauth2_provider',
    'social_django',
    'rest_framework_social_oauth2',
    'import_export',
    'drf_yasg',
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
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'server.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'channels', 'default', 'templates'), os.path.join(BASE_DIR, 'channels', 'pv', 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
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
    'DEFAULT_PAGINATION_CLASS': 'ovp.apps.core.pagination.StandardResultsSetPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
        'django.contrib.auth.backends.ModelBackend',
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

EMAIL_HOST=os.environ.get('EMAIL_HOST', None)
EMAIL_NAME=os.environ.get('EMAIL_FROM_NAME', None)
EMAIL_PORT=465
EMAIL_HOST_USER=os.environ.get('EMAIL_HOST_USER', None)
EMAIL_HOST_PASSWORD=os.environ.get('EMAIL_HOST_PASSWORD', None)
DEFAULT_FROM_EMAIL="{} <{}>".format(EMAIL_NAME, EMAIL_HOST_USER)
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

HAYSTACK_SIGNAL_PROCESSOR='ovp.apps.search.signals.TiedModelRealtimeSignalProcessor'

# Authentication backends

AUTHENTICATION_BACKENDS = [
  # Facebook OAuth2
  'ovp.apps.users.auth.oauth2.backends.facebook.FacebookOAuth2',
  'ovp.apps.users.auth.oauth2.backends.google.GoogleOAuth2',

  # django-rest-framework-social-oauth2
  'rest_framework_social_oauth2.backends.DjangoOAuth2',

  'ovp.apps.users.auth.backends.ChannelBasedAuthentication'
]

# JWT Auth

JWT_AUTH = {
  'JWT_EXPIRATION_DELTA': datetime.timedelta(hours=24),
}

# Facebook configuration

SOCIAL_AUTH_FACEBOOK_KEY = os.environ.get('FACEBOOK_ID', None)
SOCIAL_AUTH_FACEBOOK_SECRET = os.environ.get('FACEBOOK_SECRET', None)
SOCIAL_AUTH_FACEBOOK_USER_FIELDS = ['email', 'response']
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email', 'name', 'picture', 'verified']
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
  'fields': 'id, name, picture, verified, email'
}

# Google

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get('GOOGLE_ID', None)
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get('GOOGLE_SECRET', None)
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
  'https://www.googleapis.com/auth/userinfo.email',
  'https://www.googleapis.com/auth/userinfo.profile'
]

# Social Auth

SOCIAL_AUTH_STRATEGY = 'ovp.apps.users.auth.oauth2.strategy.OVPDjangoStrategy'
SOCIAL_AUTH_PIPELINE = [
  'social_core.pipeline.social_auth.social_details',
  'ovp.apps.users.auth.oauth2.pipeline.social_uid',
  'social_core.pipeline.social_auth.auth_allowed',
  'social_core.pipeline.social_auth.social_user',
  'social_core.pipeline.user.get_username',
  'social_core.pipeline.user.create_user',
  'social_core.pipeline.social_auth.associate_user',
  'social_core.pipeline.social_auth.load_extra_data',
  'social_core.pipeline.user.user_details'
]
SOCIAL_AUTH_PROTECTED_FIELDS = ('username', 'id', 'pk', 'email', 'channel')

OAUTH2_VALIDATOR_CLASS = 'ovp.apps.users.auth.oauth2.validators.OAuth2Validator'

# Password Hashers

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.UnsaltedMD5PasswordHasher',
]

# Cors headers

from corsheaders.defaults import default_headers
CORS_ALLOW_HEADERS = default_headers + (
  'x-unauthenticated-upload',
  'x-ovp-channel',
)

# Jet

JET_INDEX_DASHBOARD = 'ovp.apps.admin.jet.dashboard.CustomIndexDashboard'
JET_INDEX_DASHBOARD = 'channels.pv.admin.jet.dashboard.PVIndexDashboard'

# Docs
SWAGGER_SETTINGS = {
   'SECURITY_DEFINITIONS': {
      'Basic': {
            'type': 'basic'
      },
      'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
      }
   }
}

if env == 'production':
  from .production import *
else:
  from .dev import *
