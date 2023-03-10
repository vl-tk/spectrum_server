import copy
import logging
import math
from pathlib import Path
from typing import *

import pandas as pd
from apps.events.models import Event
from apps.events.services import EventImporter
from apps.importer.services import ExcelImportService
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils import timezone
from eav.models import Attribute
from pandas import Timestamp
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from utils.text_format import strfdelta

logger = logging.getLogger('django')


class ValidatorMixin:

    def is_excel_file(self, file):
        """
        source: https://stackoverflow.com/questions/23515791/how-to-check-the-uploaded-file-is-csv-or-xls-in-python
        """

        excelSigs = [
            ('xlsx', b'\x50\x4B\x05\x06', 2, -22, 4),
            ('xls', b'\x09\x08\x10\x00\x00\x06\x05\x00', 0, 512,
             8),  #Saved from Excel
            ('xls', b'\x09\x08\x10\x00\x00\x06\x05\x00', 0, 1536,
             8),  #Saved from LibreOffice Calc
            ('xls', b'\x09\x08\x10\x00\x00\x06\x05\x00', 0, 2048, 8
             )  #Saved from Excel then saved from Calc
        ]

        for sigType, sig, whence, offset, size in excelSigs:
            with open(file, 'rb') as f:
                f.seek(offset, whence)
                bytes = f.read(size)
                if bytes == sig:
                    return True
        return False


class ImportSerializer(serializers.Serializer, ValidatorMixin):

    VALID_IMPORT_DATA_TYPES = [
        'event'
    ]

    data_type = serializers.CharField(required=True)
    file = serializers.FileField(required=True)

    force_rewrite = serializers.BooleanField(default=False, required=False)

    def validate(self, attrs):

        in_memory_file_obj = attrs['file']

        location = Path(settings.PROJECT_DIR) / "media_files"
        location.mkdir(exist_ok=True)

        self.file = location / in_memory_file_obj.name

        # fix?
        if not self.file.endswith('.xlsx'):
            self.file += '.xlsx'

        with open(self.file, 'wb+') as f:
            for chunk in in_memory_file_obj.chunks():
                f.write(chunk)

        try:
            Attribute.objects.get(slug='source_filename')
        except Attribute.DoesNotExist:
            pass
        else:

            is_file_loaded = Event.objects.filter(
                eav__source_filename__startswith=in_memory_file_obj.name
            ).exists()

            if is_file_loaded and not attrs.get('force_rewrite'):

                event = Event.objects.filter(
                    eav__source_filename__startswith=in_memory_file_obj.name
                ).order_by('-created_at').first()

                timedelta_ago = timezone.now() - event.created_at

                timedelta = strfdelta(timedelta_ago, '%H:%M:%S')

                raise ValidationError(
                    {'file_loaded': f"File is already loaded ({timedelta} ago)."})

        if not self.is_excel_file(self.file):
            self.file.unlink()
            raise ValidationError(
                {'file': "Incorrect file. Excel file (xls/xlsx) is expected"})
        else:
            attrs['file'] = self.file

        if attrs.get('data_type') not in self.VALID_IMPORT_DATA_TYPES:
            raise ValidationError({'data_type': "Unknown data type"})

        return super().validate(attrs)

    def import_data(self):

        if self.validated_data['data_type'] == 'event':
            importer = EventImporter(
                filepath=self.validated_data['file']
            )
        else:
            raise NotImplementedError

        eis = ExcelImportService(
            filepath=self.validated_data['file'],
            importer=importer,
            importer_user=self.context['request'].user,
            force_rewrite=self.validated_data['force_rewrite']
        )

        try:
            rows_imported, total = eis.load_file()
        except Exception as e:
            logger.exception(e)
            return 0, 0

        self.file.unlink()

        return rows_imported, total


class PreImportSerializer(serializers.Serializer, ValidatorMixin):

    file = serializers.FileField(required=True)

    def validate(self, attrs):

        in_memory_file_obj = attrs['file']

        location = Path(settings.PROJECT_DIR) / "tmp"
        location.mkdir(exist_ok=True)

        self.file = location / in_memory_file_obj.name

        with open(self.file, 'wb+') as f:
            for chunk in in_memory_file_obj.chunks():
                f.write(chunk)

        if not self.is_excel_file(self.file):
            self.file.unlink()
            raise ValidationError(
                {'file': "Incorrect file. Excel file (xls/xlsx) is expected"})
        else:
            attrs['file'] = self.file

        return super().validate(attrs)

    def get_cells_values(self):

        def _is_nan(value):
            if isinstance(value, float):
                if math.isnan(value):
                    return True
            return False

        def _conv_to_date(value):
            if isinstance(value, Timestamp):
                return value.strftime('%d.%m.%Y')
            return value

        filepath = self.validated_data['file']

        self.df = pd.read_excel(filepath)

        res = {}
        for i, column in enumerate(self.df.columns):
            res[column] = list(set([_conv_to_date(v) for v in self.df.transpose().values[i] if not _is_nan(v)]))

        return res
