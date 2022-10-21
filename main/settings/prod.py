from .common import *

DEBUG = False

# Удаляем не нужные зависимости для прода
INSTALLED_APPS.remove('drf_spectacular')

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
SECURE_AUTH_SALT = os.environ.get('SECURE_AUTH_SALT')

BASE_URL = os.environ.get('BASE_URL')
BASE_CLIENT_URL = os.environ.get('BASE_CLIENT_URL')
BASE_RTMP_SERVER_HOST = os.environ.get('BASE_RTMP_SERVER_URL')

# AWS_S3_URL_PROTOCOL = 'https:'
# AWS_S3_URL_DOMAIN = 'hb.bizmrg.com'
# AWS_LOCATION = 'media'
# AWS_STORAGE_BUCKET_NAME = 'media-cdn'
# AWS_S3_ENDPOINT_URL = '%s//%s' % (AWS_S3_URL_PROTOCOL, AWS_S3_URL_DOMAIN)
# AWS_S3_CUSTOM_DOMAIN = '%s.%s' % (AWS_STORAGE_BUCKET_NAME, AWS_S3_URL_DOMAIN)
# MEDIA_URL = '%s//%s/%s/' % (AWS_S3_URL_PROTOCOL, AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)
# DEFAULT_FILE_STORAGE = 'main.storage_backends.MediaStorage'

# SECURITY WARNING: update this when you have the production host
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1,admin.spectrum.ru').split(',')

# Emails Settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_HOST = os.environ.get('EMAIL_HOST', '')
EMAIL_PORT = os.environ.get('EMAIL_PORT', '25')
EMAIL_USE_SSL = os.environ.get('EMAIL_USE_SSL', True)
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', False)
EMAIL_FROM = os.environ.get('EMAIL_FROM', '')

STATIC_URL = '/static/'
MEDIA_PATH = 'media'
MEDIA_URL = '%s/%s/' % (BASE_URL, MEDIA_PATH)
STATIC_ROOT = os.path.join(PROJECT_DIR, 'static')
MEDIA_ROOT = os.path.join(PROJECT_DIR, 'media')
