import copy
import logging
from pathlib import Path
from typing import *

from apps.events.services import EventImporter
from apps.importer.services import ExcelImportService
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

logger = logging.getLogger('django')


class ImportSerializer(serializers.Serializer):

    VALID_IMPORT_DATA_TYPES = [
        'event'
    ]

    data_type = serializers.CharField(required=True)
    file = serializers.FileField(required=True)

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

    def validate(self, attrs):

        in_memory_file_obj = attrs['file']

        location = Path(settings.PROJECT_DIR) / "media_files"

        filename = FileSystemStorage(location=location).save(
            in_memory_file_obj.name,
            in_memory_file_obj
        )

        file = location / filename

        if not self.is_excel_file(file):
            file.unlink()
            raise ValidationError(
                {'file': "Incorrect file. Excel file (xls/xlsx) is expected"})
        else:
            attrs['file'] = file

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
            importer=importer
        )

        try:
            rows_imported = eis.load_file()
        except Exception as e:
            logger.exception(e)
            return

        return rows_imported
