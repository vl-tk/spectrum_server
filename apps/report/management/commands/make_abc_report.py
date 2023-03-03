# -*- coding: utf-8 -*-
from typing import Any

from apps.report.views import CHZReport6View
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Generate ABC-report"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        CHZReport6View().generate_report_records_to_db()
