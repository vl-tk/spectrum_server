import logging
from typing import *

from apps.events.models import Event
from apps.events.serializers import EventSerializer
from apps.importer.services_data import EAVDataProvider
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


class EventListView(ListAPIView):

    permission_classes = [AllowAny]

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

        event_ct = ContentType.objects.get(
            app_label='events',
            model='event'
        )

        events = EAVDataProvider(
            entity_id=event_ct.pk,
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
