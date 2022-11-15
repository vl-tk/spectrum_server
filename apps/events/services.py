from pathlib import Path

from apps.events.models import Event
from apps.importer.services import BaseImporter
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

    def get_content_type(self):
        return ContentType.objects.get_for_model(obj)

    def create_record(self, columns, row_values):

        row_values = row_values[1:]  # except for line number

        assert len(columns) == len(row_values), f'{len(columns)}, {";".join(columns)}, {len(row_values)}, {";".join(row_values)}'

        columns = [f'eav__{c}' for c in columns]
        values = dict(zip(columns, row_values))
        values['eav__source_filename'] = self.filepath.name

        try:
            event = Event.objects.create(**values)
        except Exception as e:
            ilogger.exception(e)
            return

        ilogger.info(f'{event} CREATED')
        return True
