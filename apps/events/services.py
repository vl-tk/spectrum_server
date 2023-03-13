import datetime
import io
import tempfile
from pathlib import Path
from typing import *

import xlsxwriter
from apps.events.models import Event
from apps.importer.services import BaseImporter
from apps.log_app.models import LogRecord
from django.contrib.contenttypes.models import ContentType
from eav.models import Attribute
from utils.logger import ilogger


class EventImporter(BaseImporter):

    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.setup()
        self.content_type = ContentType.objects.get(
            app_label='events',
            model='event'
        )

    def create_record(self, columns, row_values: List[str], sort: int = 0, importer_user = None, total = 0):

        ilogger.info(f'STARTED: create_record: {sort}/{total}')
        ilogger.debug(f'{columns = }')
        ilogger.debug(f'{row_values = }')
        ilogger.debug(f'{sort = }')
        ilogger.debug(f'{importer_user = }')

        row_values = row_values[1:]  # except for line number

        # print(f'{len(columns)}')
        # print(f'{len(row_values)}')
        # print(f'{"; ".join(columns)}')
        # print(f'{";".join([str(i) for i in row_values])}')

        assert len(columns) == len(row_values), \
            f'{len(columns)}, {len(row_values)}, {";".join(columns)}, {";".join([str(i) for i in row_values])}'

        column_names = [f'eav__{c}' for c in columns]

        values = dict(zip(column_names, row_values))

        values['eav__source_filename'] = self.filepath.name
        values['sort'] = sort
        values['importer_user'] = importer_user

        try:
            event = Event.objects.create(**values)
        except Exception as e:

            ilogger.exception(e)
            ilogger.error(values)

            msg = f'{e}\n{values}'

            LogRecord.objects.create(
                message=msg,
                content_type=self.content_type,
                is_admin_only=True
            )

            return False

        ilogger.info(f'FINISHED: create_record {event}. Status: OK')

        return True


class EventExporter:

    def __init__(self, events):
        self.events = events

        self.data = self.events.get('results', [])
        self.columns = self.events.get('columns', [])
        self.column_names = [c['name'] for c in self.events.get('columns', []) if not c.get('is_hidden')]
        self.column_slugs = [c['slug'] for c in self.events.get('columns', []) if not c.get('is_hidden')]

        self.filename = None

    def get_row_values(self, row) -> list:

        values = []
        for slug in self.column_slugs:
            values.append(row['fields'].get(slug, ''))

        ilogger.debug(self.column_names)
        ilogger.debug(f'{values}')

        return values

    def get_filename(self, data):
        filename = data[-1]['fields'].get('source_filename', '')
        if len(filename) >= 8 and filename[-8] == '_':
            filename = filename[0:-8]
        if not filename:
            filename = 'table_{}'.format(datetime.datetime.now().strftime('%H%M%S_%d%m%Y'))
        return filename

    def export_to_excel(self):

        buffer = io.BytesIO()
        workbook = xlsxwriter.Workbook(buffer)

        worksheet = workbook.add_worksheet()

        # TODO: worksheet.write_row('A1', self.column_names)

        self.filename = self.get_filename(self.data)

        for i, row in enumerate(self.data, start=1):
            worksheet.write_row(f'A{i}', self.get_row_values(row))

        workbook.close()

        buffer.seek(0)

        return buffer, f'{self.filename}.xlsx'
