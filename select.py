#!/usr/bin/env python

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings.local')  # isort:skip

import django   # isort:skip
django.setup()
from apps.events.models import Event   # isort:skip


# sql = """
# select * from events_event
# """

# events = Event.objects.raw(sql)
events = Event.objects.all()

print(len(events))
print(events)

for e in events:
    print(e)
    print(e.eav.naimenovanie_organizatsii)
    print(e.eav.source_filename)
