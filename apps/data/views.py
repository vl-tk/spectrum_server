import logging
import operator
from typing import *

from apps.data.models import CHZRecord, DGisRecord
from apps.data.serializers import CHZRecordSerializer, DGisRecordSerializer
from django_filters.rest_framework import FilterSet
from django_filters.rest_framework.filters import CharFilter
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
