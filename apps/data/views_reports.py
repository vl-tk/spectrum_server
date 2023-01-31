import logging
from datetime import datetime
from typing import *

import pytz
from apps.data.models import CHZRecord, DGisRecord, get_regions
from apps.data.serializers import CHZRecordSerializer
from apps.importer.services_data import EAVDataProvider
from apps.log_app.models import LogRecord
from apps.report.services import ReportBuilder
from dateutil.parser import parse
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.db.models import Count, Q
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


class CHZRecordRegionFilterView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
        ],
        tags=['data'],
        summary='Список регионов ЧЗ для фильтра',
    )
    def get(self, request, *args, **kwargs):
        values = get_regions()
        return Response(values, status=status.HTTP_200_OK)


class CHZRecordGTINView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
        ],
        tags=['data'],
        summary='Список GTIN ЧЗ для фильтра',
    )
    def get(self, request, *args, **kwargs):

        # TODO: use materialized view

        chz = CHZRecord.objects.all().values('gt', 'product_name')  # .annotate(total=Count('gt')).order_by('-total')

        """
        {"gt":"04660105980858","product_name":"Табак для кальяна, ICE FRUIT GUM, 40 гр, SPECTRUM TOBACCO","total":16457}
        """

        return Response(chz, status=status.HTTP_200_OK)


class CHZReport1View(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
        ],
        tags=['data'],
        summary='Розничные продажи по GTIN',
    )
    def get(self, request, *args, **kwargs):

        args = []
        conditions = ''

        gtins = []
        for gtin in self.request.query_params.get('gtin', '').split(','):
            try:
                gtin = int(gtin.strip())
            except ValueError:
                pass
            else:
                gtins.append(gtin)

        inns = []
        for v in self.request.query_params.get('inn', '').split(','):
            try:
                inn = int(v.strip())
            except ValueError:
                pass
            else:
                inns.append(inn)

        if inns:
            inns = ', '.join([str(v) for v in inns])
            conditions = f'AND cz.inn IN ({inns})'

        if gtins:
            gtins = ', '.join([f"'{v}'" for v in gtins])
            conditions += f' AND cz.gt::text IN ({gtins})'

        cursor = connection.cursor()

        sql = """
        SELECT cz.inn, cz.owner_name, SUM(cz.out_retail) AS retail_sales FROM data_chzrecord AS cz
        -- RIGHT OUTER JOIN data_dgisrecord AS dg ON cz.inn = ANY(dg.inn)
        WHERE 1=1 {conditions}
        GROUP BY cz.inn, cz.owner_name
        HAVING SUM(cz.out_retail) > 0
        ORDER BY retail_sales DESC
        """.format(
            conditions=conditions
        )

        try:
            cursor.execute(sql)
            records = cursor.fetchall()
        except Exception as e:
            cursor.close
            raise e

        return Response(records, status=status.HTTP_200_OK)
