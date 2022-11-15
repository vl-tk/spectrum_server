from pathlib import Path

from apps.events.models import Event
from apps.importer.services import BaseImporter
from eav.models import Attribute
from utils.logger import ilogger


class EventImporter(BaseImporter):

    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.setup()

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
