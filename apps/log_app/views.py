import copy
import logging
from typing import *

from apps.events.models import Event
from apps.events.reports import EventReportBuilder
from apps.events.serializers import EventSerializer
from apps.events.services import EventExporter
from apps.importer.services_data import EAVDataProvider
from apps.log_app.models import LogRecord
from apps.log_app.serializers import LogRecordSerializer
from apps.report.services import ReportBuilder
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
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger('django')


class LogListCreateView(ListCreateAPIView):

    permission_classes = [IsAuthenticated]

    queryset = LogRecord.objects.filter(is_admin_only=False)
    serializer_class = LogRecordSerializer

    @extend_schema(
        parameters=[
        ],
        tags=['logs'],
        summary='Лог',
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):

        data = copy.deepcopy(request.data)

        data['user'] = request.user

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        lr = serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
