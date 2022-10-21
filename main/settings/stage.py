from .common import *

DEBUG = True

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'stage)(r$zokmzkv)6=jrde6fUDo9omya4inm%#b1^_gf+')
SECURE_AUTH_SALT = os.environ.get('SECURE_AUTH_SALT',
                                  'stage1_n=qJO51@GWsTObrRV8EdIFPqF$@6336H7sxhogE5tSO|aoM|3Q(zD3.+%E}~p<L')

BASE_URL = os.environ.get('BASE_URL', 'https://api.spectrum.goodbit.dev')
BASE_CLIENT_URL = os.environ.get('BASE_CLIENT_URL', 'https://spectrum.goodbit.dev')

# SECURITY WARNING: update this when you have the production host
ALLOWED_HOSTS = os.environ.get(
    'ALLOWED_HOSTS',
    'api.spectrum.goodbit.dev,admin.spectrum.goodbit.dev,spectrum.goodbit.dev,localhost').split(',')

# Emails Settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'nitsenko94@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'WZEdF9CJ6J')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = os.environ.get('EMAIL_PORT', '587')
EMAIL_USE_SSL = os.environ.get('EMAIL_USE_SSL', False)
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', True)
EMAIL_FROM = os.environ.get('EMAIL_FROM', 'nitsenko94@gmail.com')

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
        'level': 'DEBUG',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': True,
        },
    },
}


STATIC_URL = '/static/'
MEDIA_PATH = 'media'
MEDIA_URL = '%s/%s/' % (BASE_URL, MEDIA_PATH)
STATIC_ROOT = os.path.join(PROJECT_DIR, 'static')
MEDIA_ROOT = os.path.join(PROJECT_DIR, 'media')

DATA_UPLOAD_MAX_NUMBER_FIELDS = 10240 # higher than the count of fields
