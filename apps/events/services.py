from pathlib import Path

from apps.events.models import Event
from apps.importer.services import BaseImporter
from eav.models import Attribute
from utils.logger import ilogger


class EventImporter(BaseImporter):

    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.setup()

    def create_record(self, row_values: tuple):

        try:
            event = Event.objects.create()
            event.eav.source_filename = self.filepath.name
            # TODO: assign attributes self.values
            event.save()
        except Exception as e:
            ilogger.exception(e)
            return

        ilogger.info(f'{event} CREATED')
        return True
