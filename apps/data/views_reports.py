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


class CHZRecordRegionFilterView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
        ],
        tags=['data'],
        summary='Список регионов для фильтра',
    )
    def get(self, request, *args, **kwargs):
        values = get_regions()
        return Response(values, status=status.HTTP_200_OK)


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
        else:
            conditions = ''

        cursor = connection.cursor()

        sql = f"""
        SELECT cz.inn, cz.owner_name, SUM(cz.out_retail) AS retail_sales FROM data_chzrecord AS cz
        WHERE 1=1 {conditions}
        GROUP BY cz.inn, cz.owner_name
        HAVING SUM(cz.out_retail) > 0
        ORDER BY retail_sales DESC
        """

        # SELECT * FROM categories c
        # WHERE
        # EXISTS (SELECT 1 FROM article a WHERE c.id = a.category_id);

        try:
            cursor.execute(sql)
            records = cursor.fetchall()
        except Exception as e:
            cursor.close
            raise e

        # SELECT * FROM categories c
        # WHERE
        # EXISTS (SELECT 1 FROM article a WHERE c.id = a.category_id);

        # Use join

        # SELECT
        #     TABLE_A.COLUMN_1,
        #     TABLE_A.COLUMN_2, TABLE_B.COLUMN_A AS COLUMN_3, ABLE_B.COLUMN_B AS COLUMN_4
        # FROM
        #     TABLE_A
        # JOIN
        #     TABLE_B ON TABLE_B.COLUMN_Z LIKE CONCAT('%', TABLE_A.COLUMN_2, '%')

        return Response(records, status=status.HTTP_200_OK)
