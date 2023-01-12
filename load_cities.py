import os
from pathlib import Path

import requests
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings.local')  # isort:skip

import django   # isort:skip
django.setup()
from apps.data.models import CityRecord   # isort:skip
from django.conf import settings   # isort:skip
from apps.users.models import User   # isort:skip
from apps.users.tokens.serializers import TokenObtainPairSerializer   # isort:skip
from django.core.files import File  # isort:skip


def load_cities():

    file = Path('test_files/cities.csv')

    with open(file, 'r') as f:

        for line in f.readlines():

            items = [i for i in line.strip().split(';')]

            if len(items) == 4:

                CityRecord.objects.create(
                    city=items[0],
                    region=items[3],
                    clat=items[1],
                    clong=items[2]
                )


if __name__ == '__main__':
    load_cities()
