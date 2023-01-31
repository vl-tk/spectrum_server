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


class ExcelImportService:

    def __init__(self, filepath: Path, importer, importer_user, force_rewrite=False):
        self.df = pd.read_excel(filepath)
        self.filepath = filepath
        self.importer = importer
        self.importer_user = importer_user
        self.columns = self.get_columns()
        self.force_rewrite = force_rewrite

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

    def handle_rewrite(self):

        if self.force_rewrite:

            objs = self.importer.content_type.model_class().objects.filter(
                eav__source_filename=self.filepath.name
            )

            objs.update(eav__source_filename=f'{self.filepath.name}__TMP_RENAMED')

    def handle_post_rewrite(self, count_to_load):

        if self.force_rewrite:

            new_records = self.importer.content_type.model_class().objects.filter(
                eav__source_filename=self.filepath.name
            ).count()

            if count_to_load == new_records:

                objs = self.importer.content_type.model_class().objects.filter(
                    eav__source_filename=f'{self.filepath.name}__TMP_RENAMED'
                ).delete()

    def load_file(self):

        ilogger.info('STARTED import "%s" using %s', self.filepath.name,
                     self.importer.__class__.__name__)

        self.handle_rewrite()

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

        self.handle_post_rewrite(count_to_load=self.df.to_records())

        LogRecord.objects.create(
            user=self.importer_user,
            message=f'Импортировано {success} записей',
            content_type=self.importer.content_type
        )

        ilogger.info(
            'FINISHED import "%s" (%d to db/%d from file)',
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

        ilogger.info('STARTED create_columns')

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
                    slug=converted_slug,
                    defaults={
                        'name': column,
                        'datatype': self.columns[column],
                        'display_order': index
                    }
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
