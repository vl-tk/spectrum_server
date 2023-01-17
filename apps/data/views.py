import logging
import operator
from typing import *

from apps.data.models import CHZRecord, DGisRecord
from apps.data.serializers import CHZRecordSerializer, DGisRecordSerializer
from apps.events.models import Event
from django.db import connection
from django.db.models import ExpressionWrapper, F
from django_filters.rest_framework import FilterSet
from django_filters.rest_framework.filters import CharFilter
from eav.models import Attribute, Value
from main.pagination import StandardResultsSetPagination
from rest_framework import generics, permissions, status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger('django')


class CHZRecordFilterSet(FilterSet):

    class Meta:
        model = CHZRecord
        fields = '__all__'


class CHZListView(ListAPIView):

    permission_classes = [AllowAny]
    serializer_class = CHZRecordSerializer
    queryset = CHZRecord.objects.all()
    pagination_class = StandardResultsSetPagination
    filterset_class = CHZRecordFilterSet


class DGisRecordFilterSet(FilterSet):

    class Meta:
        model = DGisRecord
        fields = ['city']
        exclude = ['inn']


class DGisRecordListView(ListAPIView):

    permission_classes = [AllowAny]
    serializer_class = DGisRecordSerializer
    queryset = DGisRecord.objects.all()
    pagination_class = StandardResultsSetPagination
    filterset_class = DGisRecordFilterSet


class DGisRecordFilterSet(FilterSet):

    class Meta:
        model = DGisRecord
        fields = ['city']
        exclude = ['inn']


class DGisRecordPotentialListView(ListAPIView):

    permission_classes = [AllowAny]
    serializer_class = DGisRecordSerializer
    pagination_class = StandardResultsSetPagination
    filterset_class = DGisRecordFilterSet

    def get_queryset(self, *args, **kwargs):

        # TODO: 'adresid_tochki' is hardcoded for now
        a = Attribute.objects.get(slug='adresid_tochki')

        cursor = connection.cursor()

        sql = """
            SELECT DISTINCT ev.entity_id AS id
            FROM eav_value AS ev
            INNER JOIN events_event AS et ON et.id = ev.entity_id
            WHERE ev.value_text ~ '^\d+(\.\d+)?$' AND ev.attribute_id = {attribute_id}
        """.format(
            attribute_id=a.pk
        )

        try:
            cursor.execute(sql)
            ids_tuples = cursor.fetchall()
        except Exception as e:
            cursor.close
            raise e

        event_ids = [str(v[0]) for v in ids_tuples]

        dgisrecord_ids = [e.eav.adresid_tochki for e in Event.objects.filter(id__in=event_ids)]

        return DGisRecord.objects.exclude(id__in=dgisrecord_ids)
