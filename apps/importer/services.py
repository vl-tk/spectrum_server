import datetime
import difflib
import logging
import os
from collections import OrderedDict
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import List

import pandas as pd
from apps.log_app.models import LogRecord
from eav.models import Attribute
from pandas import Timestamp
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
        # TODO: get all attributes from EAV
        return []


class ExcelImportService:

    def __init__(self, filepath: Path, importer, importer_user):
        self.df = pd.read_excel(filepath)
        self.filepath = filepath
        self.importer = importer
        self.importer_user = importer_user
        self.columns = self.get_columns()

        # if rename columns
        # df.columns = KEYS

    def get_columns(self):

        data = OrderedDict([])

        def _is_date(values):
            for v in values:
                if not isinstance(v, Timestamp) or str(v).isalpha():
                    return False
            return True

        def _is_int(values):
            for v in values:
                if not isinstance(v, int):
                    return False
            return True

        def _is_float(values):
            for v in values:
                if not isinstance(v, float):
                    return False
            return True

        for column_name in self.df.columns:

            values = self.df[column_name].tolist()

            if _is_date(values):
                data[column_name] = Attribute.TYPE_DATE

            # if _is_int(values):
                # return Attribute.TYPE_INT

            # if _is_float(values):
                # return Attribute.TYPE_FLOAT

            else:
                data[column_name] = Attribute.TYPE_TEXT

        return data

    def load_file(self):

        ilogger.info('STARTED import "%s" using %s', self.filepath.name,
                     self.importer.__class__.__name__)

        slugs = self.create_columns()

        result = {}
        success = 0
        for i, row in enumerate(self.df.to_records(), start=1):

            row_values: list = [self.preformat_cell(value, j) for j, value in enumerate(row)]

            res = self.importer.create_record(
                columns=slugs,
                row_values=row_values,
                sort=i,
                importer_user=self.importer_user
            )
            if res:
                success +=1

        LogRecord.objects.create(
            user=self.importer_user,
            message=f'Импортировано {success} записей',
            content_type=self.importer.content_type
        )

        ilogger.info(
            'FINISHED import "%s" (%d imported to db/%d in file)',
            self.filepath.name,
            success,
            len(self.df.to_records())  # TODO: method?
        )

    def preformat_cell(self, value, i) -> str:

        column = list(self.columns.keys())[i - 1]
        column_type = self.columns[column]

        if column_type == 'date':
            dt = datetime.datetime.utcfromtimestamp(value.tolist() / 1e9)
            return dt

        # TODO: int, float

        return str(value) if str(value) != 'nan' else ''

    def create_columns(self):

        ilogger.info('STARTED create_columns for "%s"', self.filepath)

        slugs = []

        for index, column in enumerate(self.df.columns, start=1):

            try:
                slug = translit(column.lower(), 'ru', reversed=True)
                slug = slug.replace(' ', '_').replace('-', '_')
                converted_slug = ''.join([
                    v for v in slug
                    if v.isalpha() or v.isnumeric() or v in ['_']
                ])
            except Exception as e:
                ilogger.info('%s, %s, %s', column, slug, converted_slug)
                ilogger.exception(e)

            try:
                attr, created = Attribute.objects.get_or_create(
                    name=column,
                    slug=converted_slug,
                    datatype=self.columns[column],
                    display_order=index
                )
                attr.entity_ct.set([self.importer.content_type])
            except Exception as e:
                ilogger.info('%s, %s', column, slug, converted_slug)
                ilogger.exception(e)
            else:
                slugs.append(converted_slug)
                if created:
                    ilogger.info('CREATED column "%s" (%s)', column, converted_slug)
                else:
                    ilogger.info('EXIST column "%s" (%s)', column, converted_slug)

        ilogger.info('FINISHED create_columns for "%s". Status: OK', self.filepath)
        return slugs


class BaseImporter:

    def setup(self):

        a, _ = Attribute.objects.get_or_create(
           name='Файл импорта',
           slug='source_filename',
           datatype=Attribute.TYPE_TEXT,
           required=True,
           display_order=500
        )
