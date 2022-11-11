import difflib
import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import List

import pandas as pd
from eav.models import Attribute
from transliterate import translit
from utils.logger import ilogger


class ColumnMatcher:
    """
    Запускать перед импортом чтобы определять какие колонки скорее всего с
    опечатками и нужно брать существующие значения в базе
    """

    POSSIBLE_MATCH_VALUE = 0.75

    def __init__(self, new_columns: List[str]):
        self.new_columns = new_columns

    def find_possible_matches(self):

        recommendations = defaultdict()

        existing_columns = self.get_existing_columns()

        for new_column in self.new_columns:

            ratio = difflib.SequenceMatcher(None, new_column,
                                            existing_column).quick_ratio()

            if ratio > POSSIBLE_MATCH_VALUE:

                recommendations[new_column].append(existing_column)

        return recommendations

    def get_existing_columns(self):
        # todo: get all attributes from EAV
        return []


class ExcelImportService:

    def __init__(self, filepath: Path, importer):
        self.df = pd.read_excel(filepath)
        self.filepath = filepath
        self.importer = importer

        # if rename columns
        # df.columns = KEYS

    def load_file(self):

        ilogger.info('STARTED import "%s" using %s', self.filepath.name,
                     self.importer.__class__.__name__)

        self.create_columns()

        result = {}
        success = 0
        for i, row in enumerate(self.df.to_records()):
            row_values: tuple = [self.preformat_cell(value) for value in row]
            res = self.importer.create_record(row_values)
            if res:
                success +=1

        ilogger.info(
            'FINISHED import "%s" (%d imported to db/%d in file)',
            self.filepath.name,
            success,
            len(self.df.to_records())  # TODO: method?
        )

    def preformat_cell(self, i) -> str:
        return str(i) if str(i) != 'nan' else ''

    def create_columns(self):

        ilogger.info('STARTED create_columns for "%s"', self.filepath)

        for column in self.df.columns:

            try:
                slug = translit(column.lower(), 'ru', reversed=True)
                slug = slug.replace(' ', '_')
                converted_slug = ''.join([
                    v for v in slug
                    if v.isalpha() or v.isnumeric() or v in ['-', '_']
                ])
            except Exception as e:
                ilogger.info('%s, %s, %s', column, slug, converted_slug)
                ilogger.exception(e)

            try:
                a, created = Attribute.objects.get_or_create(
                    name=column,
                    slug=converted_slug,
                    datatype=Attribute.TYPE_TEXT)
            except Exception as e:
                ilogger.info('%s, %s', column, slug, converted_slug)
                ilogger.exception(e)
            else:
                if created:
                    ilogger.info('CREATED column "%s" (%s)', column, converted_slug)
                else:
                    ilogger.info('FOUND column "%s" (%s)', column, converted_slug)

        ilogger.info('FINISHED create_columns for "%s"', self.filepath)


class BaseImporter:

    def setup(self):

        a, _ = Attribute.objects.get_or_create(
           name='Файл импорта',
           slug='source_filename',
           datatype=Attribute.TYPE_TEXT
        )
