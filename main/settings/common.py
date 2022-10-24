import os
from datetime import timedelta

from corsheaders.defaults import default_headers

BASE_URL = os.environ.get('BASE_URL', 'http://localhost:4096')
BASE_CLIENT_URL = os.environ.get('BASE_CLIENT_URL', 'http://localhost:8030')
# Build paths inside the main like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'q2*_*ek4s28DE0pNc1AyIk(*e=i4(cn)uju5x_c!98r&hvbiayf3')
SECURE_AUTH_SALT = '1_n=qJO51@iolpCftKukjvWeotd8rYSLu40-ELvNxq/{e9.BMR)U"?%SL:pBtA52G9T'

DEBUG = bool(os.environ.get('DJANGO_DEBUG', True))

ALLOWED_HOSTS = ['0.0.0.0', 'localhost', '127.0.0.1', 'main']

# Application definition
INSTALLED_APPS = [
    # system apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'drf_spectacular',
    'corsheaders',
    'multiselectfield',
    'debug_toolbar',
    'admin_cursor_paginator',
    'simple_history',

    # User apps
    'apps',
    'apps.users',
    'apps.data',
]

MIDDLEWARE = [
    'main.middleware.TimezoneMiddleware',
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
]

AUTH_USER_MODEL = 'users.User'

CORS_ALLOW_ALL_ORIGINS = True
CORS_EXPOSE_HEADERS = ['Content-Range']
CORS_ALLOW_HEADERS = default_headers + (
    'Range',
    'Content-Range'
)

ROOT_URLCONF = 'main.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, '../templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.csrf',
                'django.template.context_processors.tz',
                'django.template.context_processors.i18n',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

INTERNAL_IPS = [
    # ...
    "127.0.0.1",
    # ...
]

LOG_PATH = os.path.join(BASE_DIR, '../logs')
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs/debug.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': True,
        },
    },
}

WSGI_APPLICATION = 'main.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': os.environ.get('DB_HOST', 'localhost,spectrum-postgres'),
        'NAME': os.environ.get('DB_NAME', 'main'),
        'USER': os.environ.get('DB_USER', 'main'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 's50XgW4'),
        'PORT': os.environ.get('DB_PORT', 5432),
    }
}

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = os.path.join(PROJECT_DIR, 'app-messages')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'localhost')
EMAIL_PORT = os.environ.get('EMAIL_PORT', '2525')
EMAIL_USE_SSL = os.environ.get('EMAIL_USE_SSL', False)
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', False)
EMAIL_FROM = os.environ.get('EMAIL_FROM', 'info@gmail.com')

# https://www.django-rest-framework.org/api-guide/permissions/#setting-the-permission-policy
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        # 'users.tokens.authentication.JWTAuthentication', # TODO
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    # 'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# TODO!!!!
# SWAGGER_SETTINGS = {
#     'SECURITY_DEFINITIONS': {
#         'Bearer': {
#             'type': 'apiKey',
#             'name': 'Authorization',
#             'in': 'header'
#         }
#     }
# }

SPECTACULAR_SETTINGS = {
    'TITLE': 'spectrum Api',
    'DESCRIPTION': '',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    # OTHER SETTINGS

    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "persistAuthorization": True,
        "displayOperationId": True,
    },

}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# Translation settings
# https://docs.wagtail.io/en/stable/advanced_topics/i18n.html#configuration
USE_I18N = True
LANGUAGE_CODE = 'ru'
USE_L10N = True


TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = False

USE_TZ = False

STATIC_URL = '/static/'
MEDIA_PATH = 'media'
MEDIA_URL = '%s/%s/' % (BASE_URL, MEDIA_PATH)
STATIC_ROOT = os.path.join(PROJECT_DIR, 'static')
MEDIA_ROOT = os.path.join(PROJECT_DIR, 'media')
TEMPLATES_ROOT = os.path.join(PROJECT_DIR, 'templates')

REDIS = {
    'host': 'spectrum-redis',
    'port': '6379',
    'db': '1',
}

# Channels
ASGI_APPLICATION = "main.websocket_routing.application"
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [(REDIS['host'], REDIS['port'])],
        },
    },
}

CELERY_ENABLE_UTC = True
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'amqp://main:WHQ56DASU4H3xUL4AS4wsGMsWQp4@spectrum-rabbit'),
CELERY_BROKER_TRANSPORT = 'amqp'

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

TESTS_VCR_FOR_REQUESTS_ENABLED = os.environ.get('TESTS_VCR_FOR_REQUESTS_ENABLED', False)

TEST_FILES_ROOT = os.path.join(PROJECT_DIR, 'test_files')

FROM_EMAIL = ''

# django4
CSRF_TRUSTED_ORIGINS = ['https://*.goodbit.dev']
