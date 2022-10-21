from __future__ import absolute_import, unicode_literals

import os
from datetime import timedelta

from celery import Celery
from celery.schedules import crontab
# set the default Django settings module for the 'celery' program.
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings.prod')
os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')

app = Celery('tasks')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Conf
app.conf.broker_transport_options = {'visibility_timeout': 3600, 'max_retries': 5}
app.conf.worker_max_memory_per_child = 12000

app.conf.beat_schedule = {
    'update_search_index': {
        'task': 'apps.blog.tasks.update_search_index',
        'schedule': crontab(minute='*/15')
    },
}
