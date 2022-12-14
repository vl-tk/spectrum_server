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

    MAX_PAGE_SIZE = 250

    def get_count(self):

        sql = self._get_entity_ids_sql(limit='NULL', offset=0)

        if self.filter_params:

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

    def get_filter(self, query_params: dict) -> dict:
        """
        1) remove 'field_' prefix from keys:
        >>> {filter_number_of_people:5} => {number_of_people:5}

        2) remove keys not in entity fields (table columns)
        """

        filter_params = {}
        for field in query_params.keys():
            if field.startswith('field_'):
                filter_params[field[6:]] = query_params[field]

        logger.info('FILTER BEFORE REMOVING UNKNOWN FIELDS: %s', filter_params)

        filter_params = {
            k: v
            for k, v in filter_params.items()
            if k in self.entity_fields.keys()
        }

        logger.info('ENTITY FIELDS: %s', self.entity_fields)
        logger.info('FILTER: %s', filter_params)

        return filter_params

    def get_single_filter_sql(self, value: str, attr_id: int) -> str:

        sql = """
        (SELECT ev.entity_id
        FROM eav_value AS ev
        WHERE ev.value_text LIKE '%{}%'
          AND ev.attribute_id = {})
        """.format(value, attr_id)

        return sql


class EAVDataProvider(PaginationMixin, FilterMixin):
    """
    Класс получения из БД полей и их значений для сущностей, атрибуты которых стали хранить при помощи схемы EAV
    (чтобы столбцы можно было гибко менять)

    Сущности:
    - Events (Акции)
    - но могут быть и другие сущности которые импортируем через xlsx таблицы

    Вывод в формате привычном для DRF (с пагинацией)
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

        self.filter_params = self.get_filter(query_params)

        self.cursor = connection.cursor()

    def get_columns_info(self):
        """
        Сохранение для данной сущности в self.entity_fields расширенной информации о ее полях
        (колонках импортированной таблицы) для составления запросов:

        Формат:
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

        self.columns_output - для вывода в json-ответе
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

    def _get_entity_ids_sql(self, limit=None, offset=None):
        """
        Вспомогательный метод составления SQL для получения списка ID entities
        1) без фильтра
        2) или по заданным параметрам фильтра

        Используется в двух случаях:
        1) как первый этап выборки entities (сначала нам нужны ID постранично,
        потом к ним довыберем данные из attribute и value таблиц)
        2) для подсчета count для постранички (полученный SQL выборки ID оборачивается в COUNT)
        """

        page_size = limit if limit is not None else self.page_size
        offset = offset if offset is not None else self.page_size * (self.page - 1)

        if not self.filter_params:

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
            desired result:

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

            i.e.:

            WITH {cond1} AS (sql_filter),
                  {cond2} AS (sql_filter)
            SELECT * FROM {cond1}
            INTERSECT SELECT * FROM {cond2};
            """

            logger.info(self.filter_params)

            cond_names = [f'cond{i}' for i in range(len(self.filter_params))]

            sql_filters = []
            for k, v in self.filter_params.items():

                sql_filter = self.get_single_filter_sql(
                    value=v,
                    attr_id=self.entity_fields[k]['id']
                )

                sql_filters.append(sql_filter)

            sql_block1 = ', '.join([f'{cond_names[i]} AS {sql_filters[i]}' for i in range(len(self.filter_params))])

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

            logger.info('MULTI FILTER SQL: %s', sql)

        return sql

    def get_entity_ids(self) -> List[str]:
        """
        Метод получения IDs

        Фильтр задается заранее в EAVDataProvider
        Результат с учетом переданных параметров в EAVDataProvider постранички
        """

        sql = self._get_entity_ids_sql()

        logger.info('ENTITY IDS SQL: %s', sql)

        try:
            self.cursor.execute(sql)
            ids_tuples = self.cursor.fetchall()
        except Exception as e:
            self.cursor.close
            raise e

        ids = [str(v[0]) for v in ids_tuples]

        logger.info('ENTITY IDS: %s', ids)

        return ids

    def get_entities(self, ids: list = None):
        """
        Метод получения всех field:value для полученных ранее entity ID
        """

        # 1. фильтрация по всем values сущностей и получение ID entity (постранично)

        if not ids:
            ids = self.get_entity_ids()

        if not ids:
            return []

        # получение field:value найденных entity

        sql = """
            SELECT ev.entity_id AS id,
                    (select slug from eav_attribute AS attr where attr.id = ev.attribute_id) AS field,
                   ev.value_text AS value,
                   ev.attribute_id AS field_id,
                   ev.id AS value_id,
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

        logger.info(sql)

        try:
            self.cursor.execute(sql)
            res2 = self.cursor.fetchall()
        except Exception as e:
            self.cursor.close
            raise e

        # 2. вывода в API в нужном формате

        results = {}
        for row in res2:
            if row[0] not in results:
                results[row[0]] = {}
            results[row[0]][row[1]] = row[2]  # results[id][eav_attribute] = [eav_value]
            results[row[0]]['created_at'] = row[-2].isoformat().replace('T', ' ').split('.')[0]
            results[row[0]]['updated_at'] = row[-1].isoformat().replace('T', ' ').split('.')[0]
            results[row[0]]['sort'] = row[-3]

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
            entities.append(res)

        logger.info(sql)

        result = {
            "count": self.get_count(),
            "next": self.get_next_page(),
            "previous": self.get_previous_page(),
            "results": entities,
            "columns": self.columns_output
        }

        return result
