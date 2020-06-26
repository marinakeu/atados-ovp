import os
import dj_database_url
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

# Sentry
sentry_dsn = os.environ.get('SENTRY_DSN', None)
if sentry_dsn:
    sentry_sdk.init(
        dsn=sentry_dsn,
        integrations=[DjangoIntegration()]
    )

# Base dir
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Disable debug
DEBUG = False

# Allowed hosts
ALLOWED_HOSTS = [
    'api.beta.atados.com.br',
    '.admin.beta.atados.com.br',
    'v2.api.atados.com.br',
    '.admin.atados.com.br',
    '.admin.voluntariadotransforma.com.br',
    '.admin.rederealpanorama.com.br'
]

# Cors
CORS_ORIGIN_WHITELIST = [
    'http://localhost:8080',
    'http://localhost:3000',
    'https://atados.com.br',
    'https://www.atados.com.br',
    'https://www.voluntariado.com.br',
    'https://voluntariado.com.br',
    'https://beta.atados.com.br',

    #
    'https://integri.org',
    'http://integrinodejs.mybluemix.net',
    'https://integrinodejs.mybluemix.net',

    #
    'https://voluntariadotransforma.com.br',
    'http://voluntariadotransforma.com.br',

    #
    'https://rederealpanorama.com.br',

    #
    'https://transformazn.com.br',
    'https://www.transformazn.com.br',
    'http://35.199.70.179',  # transformazn
    'https://channel-client-base.pacheco.now.sh',
    'https://channel-client-base.pacheco.vercel.app',

    #
    'https://www.ambev.com.br',
    'https://novahaus-ambev-novo.adttemp.com.br',
    'https://ambev-institucional.hmlg.novahaus.com.br',
    'https://ambev.working',

    #
    'https://global.good-deeds-day.org',
    'https://diadasboasacoes.com.br',

    #
    'https://demo.atados.now.sh',
    'https://atados.now.sh',
    'https://beta.atados.now.sh',
    'https://jbs.atados.now.sh',
    'https://mrv.atados.now.sh',
    'https://bnp.atados.now.sh',
    'https://heineken.atados.now.sh',
    'https://demo.atados.vercel.app',
    'https://atados.vercel.app',
    'https://beta.atados.vercel.app',
    'https://jbs.atados.vercel.app',
    'https://mrv.atados.vercel.app',
    'https://bnp.atados.vercel.app',
    'https://heineken.atados.vercel.app',

    #
    'https://ligadobemroche.com.br',
    'https://www.ligadobemroche.com.br',

    #
    'https://ovp-shell.now.sh',
    'https://ovp-shell.vercel.app'
]

CORS_ORIGIN_REGEX_WHITELIST = [
    r'^https://[a-zA-Z0-9-]+\.atados\.now\.sh$',
    r'^https://[a-zA-Z0-9-]+\.atados\.vercel\.app$'
]


# Secret key
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

# Email
EMAIL_BACKEND = 'email_log.backends.EmailBackend'
DEFAULT_FROM_EMAIL="Atados <noreply@atados.email>"

# Media and static files
MEDIA_ROOT = '/tmp'

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'ovp.apps.search.backends.ConfigurableElasticSearchEngine',
        'URL': 'http://%s/' % (
            os.environ.get('HS_SEARCH_ENDPOINT', '127.0.0.1:9200')
        ),
        'INDEX_NAME': 'atadosovp'
    },
}

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        }
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/home/ubuntu/api/logs/django.log',
        },
        'rollbar': {
            'filters': ['require_debug_false'],
            'access_token': os.environ.get('ROLLBAR_SERVER_TOKEN'),
            'environment': 'production',
            'class': 'rollbar.logger.RollbarHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'rollbar'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}


# Storage
DEFAULT_FILE_STORAGE = 'django_gcloud_storage.DjangoGCloudStorage'
GCS_PROJECT = 'beta-atados'
GCS_CREDENTIALS_FILE_PATH = os.path.abspath(
    os.path.join(BASE_DIR, '../../../', 'storage.json')
)
GCS_USE_UNSIGNED_URLS = True
GCS_BUCKET = 'atados-v3'

# Database
DATABASES = {
    'default': dj_database_url.parse(os.environ['DATABASE_URL'])
}

# Rollbar

ROLLBAR = {
    'access_token': os.environ.get('ROLLBAR_SERVER_TOKEN'),
    'environment': 'production',
    'branch': 'master',
    'root': BASE_DIR,
}
