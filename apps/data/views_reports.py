import logging
from datetime import datetime
from typing import *

import pytz
from apps.data.models import CHZRecord
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
from drf_spectacular.utils import OpenApiParameter, extend_schema
from eav.models import Attribute, Value
from main.pagination import StandardResultsSetPagination
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from utils.info import REGION

logger = logging.getLogger('django')


class CHZReport1View(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
        ],
        tags=['events'],
        summary='Розничные продажи по GTIN',
    )
    def get(self, request, *args, **kwargs):

        CHZRecord.objects.all() \
          .values('country__name') \
          .aggregate(country_population=Sum('population')) \
          .order_by('-country_population')

        data = {}

        return Response(data, status=status.HTTP_200_OK)
