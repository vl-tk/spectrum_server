import datetime
from collections import OrderedDict
from pathlib import Path

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
        self.columns = self._get_columns()
        self.force_rewrite = force_rewrite

        # if rename columns
        # df.columns = KEYS

    def _get_columns(self):

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

            ilogger.debug(column_name)
            ilogger.debug(values)
            ilogger.debug(_is_date(values))

            if _is_date(values):
                data[column_name] = Attribute.TYPE_DATE

            # if _is_int(values):
                # return Attribute.TYPE_INT

            # if _is_float(values):
                # return Attribute.TYPE_FLOAT

            else:
                data[column_name] = Attribute.TYPE_TEXT

        return data

    def _handle_rewrite(self):

        if self.force_rewrite:

            objs = self.importer.content_type.model_class().objects.filter(
                eav__source_filename=self.filepath.name
            )

            for obj in objs:
                obj.eav.source_filename=f'{self.filepath.name}__TMP_RENAMED'
                obj.save()

    def _handle_post_rewrite(self, count_to_load: int):

        if self.force_rewrite:

            new_records = self.importer.content_type.model_class().objects.filter(
                eav__source_filename=self.filepath.name
            ).count()

            if count_to_load == new_records:

                self.importer.content_type.model_class().objects.filter(
                    eav__source_filename=f'{self.filepath.name}__TMP_RENAMED'
                ).delete()

    def load_file(self):
        """
        Основной метод загрузки файла.

        Внутри - обращается к импортеру конкретной сущности и в ней создаются записи в БД
        """

        ilogger.info(
            'STARTED import "%s" using %s',
            self.filepath.name,
            self.importer.__class__.__name__
        )

        self._handle_rewrite()

        slugs = self.create_columns()

        success = 0
        for i, row in enumerate(self.df.to_records(), start=1):

            row_values: list = [self.preformat_cell(value, j) for j, value in enumerate(row)]

            res = self.importer.create_record(
                columns=slugs,
                row_values=row_values,
                sort=i,
                importer_user=self.importer_user,
                total=len(self.df.to_records())
            )
            if res:
                success +=1

        self._handle_post_rewrite(count_to_load=len(self.df.to_records()))

        ilogger.info(
            'FINISHED import "%s" (%d to db/%d from file)',
            self.filepath.name,
            success,
            len(self.df.to_records())  # TODO: len method exists for this?
        )

        if success > 0:

            LogRecord.objects.create(
                user=self.importer_user,
                message=f'Импортировано {success}/{len(self.df.to_records())} записей',
                content_type=self.importer.content_type
            )

            return success, len(self.df.to_records())

        LogRecord.objects.create(
            user=self.importer_user,
            message=f'Ошибка импорта файла {self.filepath.name} (0 записей импортировано). Обратитесь к администратору',
            content_type=self.importer.content_type
        )

        return 0, len(self.df.to_records())

    def preformat_cell(self, value, i) -> str:

        # ilogger.info(f'PREFORMAT_CELL')

        column = list(self.columns.keys())[i - 1]
        column_type = self.columns[column]

        # ilogger.info(f'value: {value}, i: {i}')
        # ilogger.info(f'{column}')
        # ilogger.info(f'{self.columns}')

        if column_type == 'date':
            dt = datetime.datetime.utcfromtimestamp(value.tolist() / 1e9)
            # import pdb; pdb.set_trace()
            # ilogger.info(f'RETURNING date: {dt}')
            return dt

        # TODO: int, float

        value = str(value) if str(value) != 'nan' else ''

        # ilogger.info(f'RETURNING str: {value}')

        return value

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
