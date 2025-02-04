import difflib
import logging
from datetime import datetime
from typing import *

import pytz
from apps.data.utils import get_region_code_for_city
from apps.events.models import Event
from apps.events.reports import EventReportBuilder
from apps.events.serializers import EventSerializer
from apps.events.services import EventExporter
from apps.importer.serializers import PreImportSerializer
from apps.importer.services_data import EAVDataProvider
from apps.log_app.models import LogRecord
from apps.report.services import ReportBuilder
from dateutil.parser import parse
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.db.models import Q
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.utils.timezone import make_aware
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from eav.models import Attribute, Value
from main.pagination import StandardResultsSetPagination
from pandas import Timestamp
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from utils.info import get_region_codes_by_short_name

logger = logging.getLogger('django')


class EventListView(ListAPIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            # OpenApiParameter(name='search', required=False, type=str),
            # OpenApiParameter(name='year', required=False, type=int),
        ],
        tags=['events'],
        summary='Акции',
        # responses={status.HTTP_200_OK: OrderSerializer()},
    )
    def get(self, request, *args, **kwargs):

        event_ct = ContentType.objects.get(app_label='events', model='event')

        events = EAVDataProvider(
            entity_id=event_ct.pk,
            entity_table='events_event',
            query_params=self.request.query_params,
            page_size=self.request.query_params.get('page_size'),
            page=self.request.query_params.get('page'),
        ).get_entities()

        # TODO: hack. переместить

        res = events

        results = []
        for r in events['results']:
            try:
                dt = parse(r['fields']['data_nachala'].split('+')[0])
            except AttributeError:
                r['fields']['status'] = 'Запланирована' if dt > timezone.now() else 'Проведена'
            else:
                r['fields']['status'] = 'Запланирована'
            results.append(r)

        res['results'] = results

        return Response(res, status=status.HTTP_200_OK)


class EventUpdateView(APIView):

    permission_classes = [IsAuthenticated]
    serializer_class = EventSerializer
    queryset = Event.objects.all()

    def get_object(self):
        event_id = self.kwargs.get('id')
        try:
            obj = self.queryset.get(pk=event_id)
        except Event.DoesNotExist:
            raise Http404
        return obj

    @extend_schema(
        tags=['events']
    )
    def patch(self, request, *args, **kwargs):
        event = self.get_object()
        serializer = EventSerializer(event, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        LogRecord.objects.create(
            user=self.request.user,
            message=f'Акция {event.pk} обновлена',
            content_type_id=Event.EVENT_CONTENT_TYPE
        )

        return Response(status=status.HTTP_202_ACCEPTED)


class EventExportView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
        ],
        tags=['events'],
        summary='Экспорт в xlsx',
    )
    def get(self, request, *args, **kwargs):

        event_ct = ContentType.objects.get(app_label='events', model='event')

        events = EAVDataProvider(
            entity_id=event_ct.pk,
            entity_table='events_event',
            query_params=self.request.query_params,  # filter
            page_size=2000  # estimate. should be enough
        ).get_entities()

        if events:
            ee = EventExporter(events=events)
            file, name = ee.export_to_excel()
            return FileResponse(file, as_attachment=True, filename=f'{name}')

        data = {
            'status': 'no events found'
        }

        return Response(data, status=status.HTTP_400_BAD_REQUEST)


class EventReportView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(name='date_field', required=True, type=str, description='Поле "дата", например: data_nachala'),
            OpenApiParameter(name='value_field', required=True, type=str, description='Поле "значение", по которому строится отчет, например: bjudzhet'),
            OpenApiParameter(name='type', required=True, type=str, description='Тип отчета: avg_per_month, avg_per_day, total_per_month, total_per_day'),
        ],
        tags=['events'],
    )
    def get(self, request, *args, **kwargs):

        event_ct = ContentType.objects.get(app_label='events', model='event')

        data = EAVDataProvider(
            entity_id=event_ct.pk,
            entity_table='events_event',
            query_params=self.request.query_params,
            page_size=50  # TODO: max
        ).get_entities()

        value_field = request.query_params.get('value_field')
        date_field = request.query_params.get('date_field')

        columns = [c['slug'] for c in data['columns']]

        if value_field not in columns or date_field not in columns:

            fields = ','.join(columns)
            res = {'msg': f'Incorrect report query: field not found. Possible fields: {fields}'}
            res['params'] = self.request.query_params.copy()

            return Response(res, status=status.HTTP_400_BAD_REQUEST)

        if request.query_params.get('type') == 'avg_per_month':

            res = EventReportBuilder(
                data=data.get('results', [])
            ).report_avg_per_month(value_field, date_field)

            return Response(res, status=status.HTTP_200_OK)

        elif request.query_params.get('type') == 'avg_per_day':

            res = EventReportBuilder(
                data=data.get('results', [])
            ).report_avg_per_day(value_field, date_field)

            return Response(res, status=status.HTTP_200_OK)

        elif request.query_params.get('type') == 'total_per_month':

            res = EventReportBuilder(
                data=data.get('results', [])
            ).report_sum_per_month(value_field, date_field)

            return Response(res, status=status.HTTP_200_OK)

        elif request.query_params.get('type') == 'total_per_day':

            res = EventReportBuilder(
                data=data.get('results', [])
            ).report_sum_per_day(value_field, date_field)

            return Response(res, status=status.HTTP_200_OK)

        res = {'msg': 'Incorrect report query'}
        res['params'] = self.request.query_params.copy()

        return Response(res, status=status.HTTP_400_BAD_REQUEST)


class EventFilterView(APIView):

    permission_classes = [IsAuthenticated]

    def _get_value(self, value):
        if value[0] is not None:
            return value[0]
        return value[1]

    @extend_schema(
        parameters=[
        ],
        tags=['events'],
        summary='Фильтры',
    )
    def get(self, request, *args, **kwargs):

        event_ct = ContentType.objects.get(app_label='events', model='event')

        dp = EAVDataProvider(
            entity_id=event_ct.pk,
            entity_table='events_event',
            query_params=self.request.query_params,
            page_size=2000  # TODO: max
        )

        ids = dp.get_entities_ids(filter_params=dp.filter_params)

        data = dp.get_columns_info()

        columns = [{'slug': d['slug'], 'name': d['name']} for d in data]

        res = []
        for column in columns:

            values = Value.objects.filter(
                attribute__slug=column['slug'],
                entity_id__in=ids
            ).distinct().values_list('value_text', 'value_date')

            values = [self._get_value(v) for v in values if (v[0] is not None or v[1] is not None)]

            column['values'] = sorted(values)
            res.append(column)

        return Response(res, status=status.HTTP_200_OK)


class EventRegionGraphView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(name='data_nachala', required=True, type=str, description='data_nachala'),
            OpenApiParameter(name='data_okonchania', required=True, type=str, description='data_okonchania')
        ],
        tags=['events'],
        summary='График по регионам',
    )
    def get(self, request, *args, **kwargs):

        event_ct = ContentType.objects.get(app_label='events', model='event')

        events = EAVDataProvider(
            entity_id=event_ct.pk,
            entity_table='events_event',
            query_params=self.request.query_params,
            page_size=2000  # estimate. should be enough
        ).get_entities()

        data = {'-': []}

        REGION_CODES = get_region_codes_by_short_name()

        for k, v in REGION_CODES.items():
            data[v[0]] = []

        for event in events['results']:
            region_code = get_region_code_for_city(event['fields']['gorod'])
            data[region_code].append(event)

        return Response(data, status=status.HTTP_200_OK)


class EventMapGraphView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(name='data_nachala', required=True, type=str, description='data_nachala'),
            OpenApiParameter(name='data_okonchania', required=True, type=str, description='data_okonchania')
        ],
        tags=['events'],
        summary='Карта',
    )
    def get(self, request, *args, **kwargs):

        event_ct = ContentType.objects.get(app_label='events', model='event')

        events = EAVDataProvider(
            entity_id=event_ct.pk,
            entity_table='events_event',
            query_params=self.request.query_params,
            page_size=2000  # estimate. should be enough
        ).get_entities()

        return Response(events, status=status.HTTP_200_OK)


class EventStatsView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
        ],
        tags=['events'],
        summary='Статистика',
    )
    def get(self, request, *args, **kwargs):

        count = Event.objects.all().count()

        res = {
            'total': count
        }

        return Response(res, status=status.HTTP_200_OK)


class EventSuggestionView(APIView):

    permission_classes = [IsAuthenticated]

    def _get_value(self, value):
        if value[0] is not None:
            v = value[0]
        else:
            v = value[1]
        if isinstance(v, datetime):
            return v.strftime('%d.%m.%Y')
        return v

    @extend_schema(
        parameters=[
            OpenApiParameter(name='field', required=True, type=str, description='Поле'),
        ],
        tags=['events'],
        summary='Подсказки',
    )
    def get(self, request, *args, **kwargs):

        field_name = self.request.query_params.get('field')

        try:
            at = Attribute.objects.get(slug=field_name)
        except Attribute.DoesNotExist:
            return Response({'error': f'unknown field: "{field_name}"'}, status=status.HTTP_400_BAD_REQUEST)

        values = Value.objects.filter(
            attribute__slug=field_name
        ).distinct().values_list('value_text', 'value_date')

        values = [self._get_value(v) for v in values if (v[0] is not None or v[1] is not None)]

        return Response(sorted(values), status=status.HTTP_200_OK)


def get_ratio(string1, string2):
    ratio = difflib.SequenceMatcher(
        None,
        string1,
        string2
    ).quick_ratio()
    return ratio


class EventTyposColumnView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(name='columns', required=False, type=str, description='Колонки'),
        ],
        tags=['events'],
        summary='Опечатки',
    )
    def get(self, request, *args, **kwargs):

        column_names = self.request.query_params.get('columns', '').split(',')

        res = {}

        ADDITIONAL_COLUMNS = ['Статус']

        if column_names:

            atts = Attribute.objects.all()

            for column_name in [c for c in column_names if c not in ADDITIONAL_COLUMNS]:

                values = {get_ratio(att.name, column_name): att for att in atts}

                if 1 in values.keys():
                    continue

                max_value = max(values.keys())
                att = values[max_value]

                res[column_name] = {
                    'msg': 'Column NOT found in DB. Possible column found in DB',
                    'column_name': att.name,
                    'column_slug': att.slug
                }

        return Response(res, status=status.HTTP_200_OK)


def str_value(value):
    res = [v for v in str(value) if v.isalpha() or v == ' ']
    return ''.join(res)


class EventTypoCellsView(APIView):

    permission_classes = [IsAuthenticated]

    def _get_value(self, value):
        if value[0] is not None:
            v = value[0]
        else:
            v = value[1]
        if isinstance(v, datetime):
            return v.strftime('%d.%m.%Y')
        return v

    def find_match(self, value, db_values):
        THRESHOLD = 0.85
        ratios = {}

        for db_value in db_values:
            ratio = get_ratio(str(value), str(db_value))
            if ratio < 1:
                ratios[round(ratio, 2)] = db_value

        if ratios.keys():
            max_value = max(ratios.keys())
            if max_value >= THRESHOLD:
                return ratios[max_value], max_value, value

        return None, None, None

    @extend_schema(
        parameters=[
            OpenApiParameter(name='file', required=True, type=OpenApiTypes.BINARY),
        ],
        tags=['events'],
        summary='Опечатки',
    )
    def post(self, request, *args, **kwargs):

        serializer = PreImportSerializer(
            data=request.data,
            context={
                'request': request,
            }
        )
        serializer.is_valid(raise_exception=True)
        pre_imported_values = serializer.get_cells_values()

        attrs = Attribute.objects.all()

        db_values = {}

        for att in attrs:

            values = Value.objects.filter(
                attribute__slug=att.slug
            ).distinct().values_list('value_text', 'value_date')

            values = list(set([self._get_value(v) for v in values if (v[0] is not None or v[1] is not None)]))

            db_values[att.name] = values

        res = {}
        for k, pre_values in pre_imported_values.items():
            for v in pre_values:
                if v in db_values[k]:
                    pass
                else:

                    # if 01.01.2021 is different from 01.01.2022 OR 11 is different from 12 - skip
                    if not (str_value(v) or [str_value(v) for v in db_values[k] if str_value(v)]):
                        continue

                    match, ratio, possible_value = self.find_match(v, db_values[k])
                    if match:
                        res[k] = {
                            'value': match,
                            'ratio': ratio,
                            'orig_value': possible_value
                        }

        return Response(res, status=status.HTTP_200_OK)
