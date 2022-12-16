import logging
from typing import *

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.db.models import Q
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404, render
from drf_spectacular.utils import OpenApiParameter, extend_schema
from eav.models import Attribute
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.events.models import Event
from apps.events.reports import EventReportBuilder
from apps.events.serializers import EventSerializer
from apps.events.services import EventExporter
from apps.importer.services_data import EAVDataProvider
from apps.report.services import ReportBuilder
from main.pagination import StandardResultsSetPagination

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

        return Response(events, status=status.HTTP_200_OK)


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
            page_size=1000  # estimate. should be enough
        ).get_entities()

        if events:
            ee = EventExporter(events=events)
            file, name = ee.export_to_excel()
            return FileResponse(file, as_attachment=True, filename=f'{name}')

        data = {
            'status': 'no events found'
        }

        return Response(data, status=status.HTTP_400_BAD_REQUEST)

        # response = HttpResponse(content_type='application/vnd.ms-excel')
        # response['Content-Disposition'] = f'attachment; filename=excel_filename.xlsx'


class EventReportView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(name='type', required=True, type=str, description='Тип отчета: avg_per_month, avg_per_day, total_per_month, total_per_day'),
            OpenApiParameter(name='value_field', required=True, type=str, description='Поле значения по которому строится отчет, например: bjudzhet'),
            OpenApiParameter(name='date_field', required=True, type=str, description='Поле даты, например: data_nachala'),
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
