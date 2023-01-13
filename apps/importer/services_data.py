import logging
from typing import *

from apps.events.models import Event
from apps.events.serializers import EventSerializer
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from drf_spectacular.utils import OpenApiParameter, extend_schema
from eav.models import Attribute
from main.pagination import StandardResultsSetPagination
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from utils.logger import sqllogger as logger


class PaginationMixin:

    MAX_PAGE_SIZE = 2000

    def get_count(self, filter_params=None):

        sql = self._get_entities_ids_sql(filter_params=filter_params, limit='NULL', offset=0)

        if filter_params:

            count_sql = """WITH ids AS ({}) SELECT COUNT(*) FROM ids;""".format(
                sql.replace(';', '')
            )

        else:

            count_sql = """WITH ids AS ({}) SELECT COUNT(*) FROM ids;""".format(
                sql.replace(';', '')
            )

        logger.info('COUNT SQL: %s', count_sql)

        try:
            self.cursor.execute(count_sql)
            res = self.cursor.fetchone()
        except Exception as e:
            self.cursor.close
            raise e

        logger.info('COUNT: %s', res)

        self.count = res[0]

        return res[0]

    def get_next_page(self):
        if self.count - (self.page * self.page_size) < 0:
            return None
        return self.page + 1

    def get_previous_page(self):
        if self.page == 1:
            return None
        return self.page - 1


class FilterMixin:

    MAX_FILTERS_NUM = 10

    def prepare_filter(self, query_params: dict = None) -> dict:
        """
        1) убрать 'field_' префикс из ключа:
        {filter_number_of_people:5}
        =>
        {number_of_people:5}

        2) убрать ключи не из столбцов таблицы
        """

        def _get_op(key):
            if '__' in key:
                return key.split('__')[-1]

        def _get_key_without_op(key):
            if '__' in key:
                return key.split('__')[0]
            return key

        if query_params is None:
            query_params = {}

        filter_params = {}
        index = 0
        for key in query_params.keys():

            if key.startswith('field_'):
                index += 1
                if index > self.MAX_FILTERS_NUM:
                    continue
                filter_params[key[6:]] = {'value': query_params[key], 'op': _get_op(key[6:])}

            elif key == 'search':
                filter_params['search'] = {'value': query_params[key]}

        logger.info('FILTER BEFORE REMOVING UNKNOWN FIELDS: %s', filter_params)

        filter_params = {
            _get_key_without_op(k): v
            for k, v in filter_params.items()
            if (_get_key_without_op(k) in self.entity_fields.keys() or k == 'search')
        }

        logger.info('ENTITY FIELDS: %s', self.entity_fields)
        logger.info('FILTER: %s', filter_params)

        return filter_params

    def get_single_filter_sql(self, value: str, attr_id: int, column_type: str, op:str = None) -> str:
        """
        Получить SQL условие по одному из фильтров

        Например, из запроса приходит:
        query_params = {"field_name": "Тест"}

        filter_params = {"name": "Тест"}

        Для генерации SQL нужно:
        value = "Тест"
        attr_id - это attribute_id поля name в таблице eav_attribute
        column_type = text
        op - это возможный оператор сравнения
        """

        sql = """
        SELECT ev.entity_id
        FROM eav_value AS ev
        WHERE
        """

        if op == 'gt':
            op = '>'
        elif op == 'gte':
            op = '>='
        elif op == 'lt':
            op = '<'
        elif op == 'lte':
            op = '<='
        else:
            op = '='

        if column_type == 'date':
            sql += "ev.value_date::date {} '{}'::date".format(op, value)
        else:
            if '||' in value:
                sql += "ev.value_text IN ({})".format(','.join([f'\'{v}\'' for v in value.split('||')]))
            else:
                sql += "ev.value_text ILIKE '%{}%'".format(value)

        if attr_id is not None:

            sql += f"\nAND ev.attribute_id = {attr_id}"

        return f'({sql})'


class EAVDataProvider(PaginationMixin, FilterMixin):
    """
    Класс получения из БД сущностей, атрибуты которых стали хранить при помощи схемы EAV

    (Основной смысл: заранее не известно с какими таблицами будет работать
    клиент, нет ясности форматов.

    Поэтому приходится закладывать гибкость работы со столбцами на уровне
    прослойки работы с БД вместо стандартных моделей, с большей трудоемкостью
    изменений

    Сущности с которыми изначально работаем (=таблицы клиента):
    - Акции (Events)

    (возможность других сущностей которые начнем импортировать через
    xlsx таблицы тоже поддерживаем)

    Ответ формируем в формате как в DRF (с пагинацией)
    """

    def __init__(self, entity_id: int, entity_table: str, query_params=None, page=None, page_size=None):

        try:
            self.page_size = int(page_size)
        except TypeError:
            self.page_size = 20

        if self.page_size > self.MAX_PAGE_SIZE:
            self.page_size = 20

        try:
            self.page = int(page)
        except TypeError:
            self.page = 1

        self.entity_id = entity_id
        self.entity_table = entity_table

        # logger.info('QUERY PARAMS: %s', query_params)

        self.get_columns_info()

        self.filter_params = self.prepare_filter(query_params)

        self.cursor = connection.cursor()

    def get_columns_info(self):
        """
        Сохранение в поле self.entity_fields расширенной информации о полях сущности
        (колонках импортированной таблицы) для составления запросов и для выдачи фронтэнду

        Формат self.entity_fields:
        {
            'inn': {
                'slug': 'inn',
                'type': 'text',
                'name': 'ИНН',
                'id': 123
            },
            'brand': {
                'slug': 'brand',
                'type': 'text',
                'name': 'Брэнд',
                'id': 124
            }
        }

        Формат self.columns_output - для вывода в json-ответе фронтэнду
        [
            {
                'slug': 'inn',
                'type': 'text',
                'name': 'ИНН',
                'id': 123
            },
            {
                'slug': 'brand',
                'type': 'text',
                'name': 'Брэнд',
                'id': 124
            }
        ]
        """

        self.entity_fields = {}

        for attr in Attribute.objects.filter(
                Q(entity_ct__id=self.entity_id)|Q(slug='source_filename')
            ).values_list('id', 'slug', 'datatype', 'name', 'display_order').order_by('display_order'):

            data = {
                'slug': attr[1],
                'type': attr[2],
                'name': attr[3],
                'id': attr[0]
            }

            if attr[1] == 'source_filename':
                data['is_hidden'] = True

            self.entity_fields[attr[1]] = data

        logger.info(self.entity_fields)

        self.columns_output = [v for k,v in self.entity_fields.items()]

        # TODO: hack. подумать что делать со статусами

        # status
        self.columns_output.append({
            'slug': 'status',
            'type': 'text',
            'name': 'Статус',
            'id': 1
        })

        return self.columns_output

    def _get_entities_ids_sql(self, filter_params=None, limit=None, offset=None):
        """
        Базовый метод составления SQL для получения списка ID entities
        1) без фильтра
        2) с заданными параметрами фильтра

        Используется в двух случаях:
        1) как первый этап выборки entities (сначала здесь берем нужны ID постранично,
        ниже в методе к ним довыберем данные из attribute и value таблиц)
        2) для подсчета count для постранички (полученный из п.1 SQL оборачивается в COUNT)
        """

        page_size = limit if limit is not None else self.page_size
        offset = offset if offset is not None else self.page_size * (self.page - 1)

        if not filter_params:

            sql = """
                SELECT DISTINCT ev.entity_id AS id, et.sort
                FROM eav_value AS ev
                INNER JOIN {entity_table} AS et ON et.id = ev.entity_id
                ORDER BY et.sort ASC
                LIMIT {page_size} OFFSET {offset};
            """.format(
                entity_table=self.entity_table,
                page_size=page_size,
                offset=offset
            )

        else:

            """
            общая схема:

            WITH {cond1} AS (sql_filter_code),
                  {cond2} AS (sql_filter_code),
                   {cond3} AS (sql_filter_code),
            SELECT * FROM {cond1}
            INTERSECT
            SELECT * FROM {cond2}
            INTERSECT
            SELECT * FROM {cond3};


            пример запроса:

            WITH

                first_ids AS

              (SELECT ev.entity_id
               FROM eav_value AS ev
               WHERE ev.value_text LIKE '%торг%'
                 AND ev.attribute_id = 269),

                second_ids AS

              (SELECT ev.entity_id
               FROM eav_value AS ev
               WHERE ev.value_text LIKE '%ООО%'
                 AND ev.attribute_id = 272 )

            SELECT * FROM first_ids
            INTERSECT
            SELECT * FROM second_ids;
            """

            logger.info(filter_params)

            cond_names = [f'cond{i}' for i in range(len(filter_params))]

            sql_filters = []
            for field_name, data in filter_params.items():

                sql_filter = self.get_single_filter_sql(
                    value=data['value'],
                    attr_id=self.entity_fields.get(field_name, {}).get('id'),
                    column_type=self.entity_fields.get(field_name, {}).get('type'),
                    op=data.get('op')
                )

                sql_filters.append(sql_filter)

            sql_block1 = ', '.join([f'{cond_names[i]} AS {sql_filters[i]}' for i in range(len(filter_params))])

            sql = f'WITH {sql_block1}'
            sql += ' INTERSECT '.join([f'SELECT * FROM {cond_name}' for cond_name in cond_names])

            sql + """
            INNER JOIN {entity_table} AS et ON et.id = ev.entity_id
            ORDER BY et.sort ASC
            """.format(entity_table=self.entity_table)

            sql += " LIMIT {page_size} OFFSET {offset};".format(
                page_size=page_size,
                offset=offset
            )

            logger.info('>>> MULTI FILTER SQL: %s', sql)

        return sql

    def get_entities_ids(self, filter_params=None) -> List[str]:
        """
        Метод получения entity IDs

        Фильтр задается заранее (при инициализации EAVDataProvider)

        Результат с учетом переданных параметров постранички
        """

        sql = self._get_entities_ids_sql(filter_params=filter_params)

        logger.info('ENTITY IDS SQL: %s', sql)

        try:
            self.cursor.execute(sql)
            ids_tuples = self.cursor.fetchall()
        except Exception as e:
            self.cursor.close
            raise e

        ids = [str(v[0]) for v in ids_tuples]

        return ids

    def get_entities(self, ids: list = None):
        """
        Метод получения всех атрибутов attribute:value для получаемых ранее entity ID
        """

        # 1. фильтрация по всем values сущностей и получение ID отфильтрованных из них (постранично)

        if not ids:

            ids = self.get_entities_ids(filter_params=self.filter_params)

        if ids:

            # выборка attribute:value для найденных ранее entity ids

            # TODO: clat не универсально для всех сущностей
            sql = """
                SELECT ev.entity_id AS id,
                        (select slug from eav_attribute AS attr where attr.id = ev.attribute_id) AS field,
                       (select COALESCE(value_date::text, value_text) from eav_value as ev2 where ev2.id = ev.id) AS value,
                       ev.id AS value_id,
                       ev.attribute_id AS field_id,
                       et.clat,
                       et.clong,
                       et.sort,
                       et.created_at,
                       et.updated_at
                FROM eav_value AS ev
                INNER JOIN {entity_table} AS et ON et.id = ev.entity_id
                WHERE ev.entity_id IN ({ids})
                ;
            """.format(
                entity_table=self.entity_table,
                ids=','.join(ids)
            )

            logger.info('get_entities SQL: %s', sql)

            try:
                self.cursor.execute(sql)
                res2 = self.cursor.fetchall()
            except Exception as e:
                self.cursor.close
                raise e

            # 2. формирование вывода в нужном формате, ожидаемом от API

            results = {}
            for row in res2:
                if row[0] not in results:
                    results[row[0]] = {}
                results[row[0]][row[1]] = row[2]  # results[id][eav_attribute] = [eav_value]
                results[row[0]]['created_at'] = row[-2].isoformat().replace('T', ' ').split('.')[0]
                results[row[0]]['updated_at'] = row[-1].isoformat().replace('T', ' ').split('.')[0]
                results[row[0]]['sort'] = row[-3]

                results[row[0]]['clat'] = row[-5] # not universal
                results[row[0]]['clong'] = row[-4]

            entities = []
            for event_id, entity_dict in results.items():
                res = {}
                res['id'] = event_id
                res['fields'] = {}
                for field in self.entity_fields.keys():
                    if field not in entity_dict.keys():
                        res['fields'][field] = None
                    else:
                        res['fields'][field] = entity_dict[field]
                res['sort'] = entity_dict['sort']
                res['created_at'] = entity_dict['created_at']
                res['updated_at'] = entity_dict['updated_at']
                res['clat'] = entity_dict['clat']  # not universal
                res['clong'] = entity_dict['clong']
                entities.append(res)

            logger.info(sql)

        else:

            entities = []

        result = {
            "count": self.get_count(filter_params=self.filter_params),
            "next": self.get_next_page(),
            "previous": self.get_previous_page(),
            "results": entities,
            "columns": self.columns_output
        }

        return result
