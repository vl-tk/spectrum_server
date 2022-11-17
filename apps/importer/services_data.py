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

logger = logging.getLogger('django')


class PaginationMixin:

    def get_count(self):

        sql = self._create_get_entity_ids_sql(limit='NULL', offset=0)

        sql = sql.replace(
            'SELECT DISTINCT ev.entity_id AS id',
            'SELECT COUNT (DISTINCT ev.entity_id) AS count'
        )

        logger.info('COUNT SQL: %s', sql)

        try:
            self.cursor.execute(sql)
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

    def create_filter(self, query_params: dict) -> dict:
        """
        remove 'field_' prefix from keys:
        filter_number_of_people:5 => number_of_people:5

        filter keys not in entity fields
        """

        filter_params = {}
        for field in query_params.keys():
            if field.startswith('field_'):
                filter_params[field[6:]] = query_params[field]

        filter_params = {
            k: v
            for k, v in filter_params.items()
            if k in self.entity_fields.keys()
        }

        logger.info(self.entity_fields)
        logger.info(filter_params)

        return filter_params


class EAVDataProvider(PaginationMixin, FilterMixin):

    def __init__(self, entity_id, page=None, page_size=None):

        try:
            self.page_size = int(page_size)
        except TypeError:
            self.page_size = 20

        try:
            self.page = int(page)
        except TypeError:
            self.page = 1

        self.cursor = connection.cursor()

        self.entity_fields = {
            v[1]: v[0]
            for v in Attribute.objects.filter(
                Q(entity_ct__id=entity_id)|Q(slug='source_filename')
            ).values_list('id', 'slug')
        }

        logger.info(self.entity_fields)

    def _create_get_entity_ids_sql(self, filter_params=None, limit=None, offset=None):

        page_size = limit if limit is not None else self.page_size
        offset = offset if offset is not None else self.page_size * (self.page - 1)

        if not filter_params:

            sql = """
                SELECT DISTINCT ev.entity_id AS id
                FROM eav_value AS ev
                LIMIT {page_size} OFFSET {offset};
            """.format(
                page_size=page_size,
                offset=offset
            )

        else:

            logger.info(filter_params)

            sql = """
                SELECT DISTINCT ev.entity_id AS id
                FROM eav_value AS ev
                WHERE
            """

            sql_parts = []
            for k, v in filter_params.items():

                sql_part = "(ev.value_text LIKE '%{}%' AND ev.attribute_id = {}) ".format(
                    v, self.entity_fields[k])

                sql_parts.append(sql_part)

            sql += " OR ".join(sql_parts)

            sql += "LIMIT {page_size} OFFSET {offset};".format(
                page_size=page_size,
                offset=offset
            )

        return sql

    def get_entity_ids(self, query_params: dict) -> List[str]:

        logger.info(query_params)

        filter_params = self.create_filter(query_params)

        sql = self._create_get_entity_ids_sql(
            filter_params=filter_params
        )

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

    def get_entities(self, query_params: dict = None):

        # 1. фильтрация по всем values сущностей и получение ID entity (постранично)

        ids = self.get_entity_ids(query_params)

        if not ids:
            return []

        # получение field:value нужных entity

        sql = """
            SELECT ev.entity_id AS id,
                    (select slug from eav_attribute AS attr where attr.id = ev.attribute_id) AS field,
                   ev.value_text AS value,
                   ev.attribute_id AS field_id,
                   ev.id AS value_id,
                   e.created_at,
                   e.updated_at
            FROM eav_value AS ev
            INNER JOIN events_event AS e ON e.id = ev.entity_id
            WHERE ev.entity_id IN ({ids});
        """.format(ids=','.join(ids))

        logger.info(sql)

        try:
            self.cursor.execute(sql)
            res2 = self.cursor.fetchall()
        except Exception as e:
            self.cursor.close
            raise e

        results = {}
        for row in res2:
            if row[0] not in results:
                results[row[0]] = {}
            results[row[0]][row[1]] = row[2]  # results[id][eav_attribute] = [eav_value]

        # 2. упаковка в flat dicts для вывода в API

        entities = []
        for event_id, entity_dict in results.items():
            res = {}
            res['id'] = event_id
            res['fields'] = {}
            for field in self.entity_fields:
                if field not in entity_dict.keys():
                    res['fields'][field] = None
            entities.append(res)

        logger.info(sql)

        result = {
            "count": self.get_count(),
            "next": self.get_next_page(),
            "previous": self.get_previous_page(),
            "results": entities
        }

        return result
