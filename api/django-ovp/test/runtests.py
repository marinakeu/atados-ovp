#!/usr/bin/env python3
import glob
import os
import sys
import django
import threading
import dj_database_url

from dotenv import load_dotenv

from django.conf import settings
from django.core.management import execute_from_command_line

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(
    0,
    (os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."))))

load_dotenv(os.path.join(BASE_DIR, '.env'))

# Unfortunately, apps can not be installed via ``modify_settings``
# decorator, because it would miss the database setup.
CUSTOM_INSTALLED_APPS = (
    'ovp.apps.core',
    'ovp.apps.admin',
    'ovp.apps.uploads',
    'ovp.apps.users',
    'ovp.apps.projects',
    'ovp.apps.organizations',
    'ovp.apps.faq',
    'ovp.apps.search',
    'ovp.apps.channels',
    'ovp.apps.catalogue',
    'ovp.apps.items',
    'ovp.apps.ratings',
    'ovp.apps.gallery',
    'ovp.apps.digest',
    'ovp.apps.donations',
    'django.contrib.admin',
    'jet',
    'jet.dashboard',
    'haystack',
    'vinaigrette',
    'oauth2_provider',
    'social_django',
    'rest_framework_social_oauth2',
)

ALWAYS_INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

ALWAYS_MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'ovp.apps.channels.middlewares.channel.ChannelRecognizerMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'ovp.apps.channels.middlewares.channel.ChannelProcessorMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'PAGINATE_BY_PARAM': 'page_size',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
        'django.contrib.auth.backends.ModelBackend',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework_csv.renderers.CSVRenderer',
    )}

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

DATABASES = {
    'default': dj_database_url.parse(os.getenv('DATABASE_URL'))
}


def gettext(s): return s

HS_ENDPOINT = os.environ.get('HS_SEARCH_ENDPOINT', None)
if HS_ENDPOINT:
    HAYSTACK_CONNECTIONS = {
        'default': {
            'ENGINE': 'ovp.apps.search.backends.ConfigurableElasticSearchEngine',
            'URL': 'http://%s/' % (
                os.environ.get('HS_SEARCH_ENDPOINT', '127.0.0.1:9200')
            ),
            'INDEX_NAME': 'atadosovp'
        },
    }
else:
    HAYSTACK_CONNECTIONS = {
        'default': {
            'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
            'PATH': os.path.join('/tmp', 'ovp_test_whoosh_index'),
        },
    }


settings.configure(
    SECRET_KEY="django_tests_secret_key",
    DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage",
    MEDIA_ROOT="/tmp",
    DEBUG=True,
    TEMPLATE_DEBUG=False,
    ALLOWED_HOSTS=[".localhost"],
    INSTALLED_APPS=ALWAYS_INSTALLED_APPS + CUSTOM_INSTALLED_APPS,
    MIDDLEWARE=ALWAYS_MIDDLEWARE_CLASSES,
    ROOT_URLCONF='test.urls',
    DATABASES=DATABASES,
    LANGUAGES=(
        ('en', gettext('English')),
        ('pt-br', gettext('Portuguese')),
    ),
    LANGUAGE_CODE='en',
    TIME_ZONE='UTC',
    USE_I18N=True,
    USE_L10N=True,
    USE_TZ=True,
    STATIC_URL='/static/',
    # Use a fast hasher to speed up tests.
    PASSWORD_HASHERS=(
        'django.contrib.auth.hashers.MD5PasswordHasher',
    ),
    FIXTURE_DIRS=glob.glob(BASE_DIR + '/' + '*/fixtures/'),
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    TEMPLATES=[
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [os.path.abspath(os.path.join(BASE_DIR, '../../templates'))],
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
    ],
    DEFAULT_SEND_EMAIL='sync',
    REST_FRAMEWORK=REST_FRAMEWORK,
    AUTH_PASSWORD_VALIDATORS=AUTH_PASSWORD_VALIDATORS,
    AUTH_USER_MODEL='users.User',
    OVP_CORE={
        'VALID_CONTACT_RECIPIENTS': ['testemail@1.com', 'testemail@2.com'],
    },
    HAYSTACK_CONNECTIONS=HAYSTACK_CONNECTIONS,
    HAYSTACK_SIGNAL_PROCESSOR='ovp.apps.search.signals.TiedModelRealtimeSignalProcessor',
    SILENCED_SYSTEM_CHECKS=["auth.E003", "auth.W004"],
    AUTHENTICATION_BACKENDS=[
        'ovp.apps.users.auth.oauth2.backends.facebook.FacebookOAuth2',
        'ovp.apps.users.auth.oauth2.backends.google.GoogleOAuth2',
        'rest_framework_social_oauth2.backends.DjangoOAuth2',
        'ovp.apps.users.auth.backends.ChannelBasedAuthentication'],
    TEST_CHANNELS=["test-channel", "channel1"],
    ZOOP_MARKETPLACE_ID=os.environ.get('ZOOP_MARKETPLACE_ID', None),
    ZOOP_PUB_KEY=os.environ.get('ZOOP_PUB_KEY', None),
    ZOOP_SELLER_ID=os.environ.get('ZOOP_SELLER_ID', None),
    ZOOP_STATEMENT_DESCRIPTOR='Test OVP donation',
    AWS_DEFAULT_REGION=os.getenv('AWS_DEFAULT_REGION'),
    AWS_ACCESS_KEY_ID=os.getenv('AWS_ACCESS_KEY_ID'),
    AWS_SECRET_ACCESS_KEY=os.getenv('AWS_SECRET_ACCESS_KEY'),
)

django.setup()
args = [sys.argv[0], 'test']
test_cases = [
    'ovp.apps.core',
    'ovp.apps.uploads',
    'ovp.apps.users',
    'ovp.apps.organizations',
    'ovp.apps.projects',
    'ovp.apps.search',
    'ovp.apps.faq',
    'ovp.apps.channels',
    'ovp.apps.catalogue',
    'ovp.apps.ratings',
    'ovp.apps.gallery',
    'ovp.apps.digest',
]

# Allow accessing test options from the command line.
offset = 1
try:
    sys.argv[1]
except IndexError:
    pass
else:  # pragma: no cover
    option = sys.argv[1].startswith('-')
    if not option:
        test_cases = sys.argv[1:]

args.extend(test_cases)
# ``verbosity`` can be overwritten from command line.
args.append('--verbosity=2')

execute_from_command_line(args)
