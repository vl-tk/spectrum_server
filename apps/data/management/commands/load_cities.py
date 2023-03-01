# -*- coding: utf-8 -*-
from pathlib import Path

from apps.data.models import CityRecord
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Load Cities and their coordinates"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):

        file = Path('data_files/cities.csv')

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
