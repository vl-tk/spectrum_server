import logging
from typing import *

from apps.events.models import Event
from apps.events.serializers import EventSerializer
from apps.events.services import EventExporter
from apps.importer.services_data import EAVDataProvider
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.db.models import Q
from django.http import FileResponse, Http404, HttpResponse
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

        # ids = self.request.query_params.get('ids')

        # entity_ids = []
        # for id in ids.split(','):
        #     try:
        #         i = int(id)
        #     except ValueError:
        #         pass
        #     else:
        #         entity_ids.append(i)

        event_ct = ContentType.objects.get(app_label='events', model='event')

        events = EAVDataProvider(
            entity_id=event_ct.pk,
            entity_table='events_event',
            query_params=self.request.query_params,
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
