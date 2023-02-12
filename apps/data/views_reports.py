import logging
from datetime import datetime
from typing import *

import pytz
from apps.data.models import (CHZRecord, DGisRecord, GTINRecordMV,
                              get_positions, get_products, get_regions)
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


def str_value(value):
    res = [v for v in str(value) if v.isalpha()]
    return ''.join(res)


def date_value(value):
    res = [v for v in str(value) if v.isdigit() or v in ['-']]
    return ''.join(res)


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


class CHZRecordProductNameFilterView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
        ],
        tags=['data'],
        summary='Список товаров ЧЗ для фильтра',
    )
    def get(self, request, *args, **kwargs):
        values = get_products()
        return Response(values, status=status.HTTP_200_OK)


class CHZRecordPositionsFilterView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
        ],
        tags=['data'],
        summary='Список позиций ЧЗ для фильтра',
    )
    def get(self, request, *args, **kwargs):
        values = get_positions()
        return Response(values, status=status.HTTP_200_OK)


class CHZRecordINNView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
        ],
        tags=['data'],
        summary='Список INN ЧЗ для фильтра',
    )
    def get(self, request, *args, **kwargs):

        values = list(CHZRecord.objects.all().values(
            'inn', 'owner_name'
        ).distinct().order_by('owner_name'))

        res = []
        for v in values:
            if v['owner_name'] == '-':
                v['owner_name'] = v['inn']
            res.append(v)

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

        records = GTINRecordMV.objects.all()

        # TODO: serializer
        res = []
        for r in records:
            res.append({
                'id': r.pk,
                'product_name': r.product_name,
                'total': r.total
            })

        return Response(res, status=status.HTTP_200_OK)


class CHZReport1View(APIView):
    """
    Розничные продавцы по ИНН
    """

    permission_classes = [IsAuthenticated]

    def make_condition(self, request):

        MAX_ITEMS = 5

        conditions = ''
        dgis_joined = False

        product_name = request.query_params.get('product_name', '')
        position = request.query_params.get('position', '')

        gtins = []
        for gtin in request.query_params.get('gtin', '').split(','):
            try:
                gtin_value = int(gtin.strip())
            except ValueError:
                pass
            else:
                gtins.append(gtin.strip())

        inns = []
        for v in request.query_params.get('inn', '').split(','):
            try:
                inn = int(v.strip())
            except ValueError:
                pass
            else:
                inns.append(inn)

        weights = []
        for v in request.query_params.get('weight', '').split(','):
            try:
                weight = int(v.strip())
            except ValueError:
                pass
            else:
                weights.append(weight)

        if weights:
            weights = ', '.join([f"'{v}'" for v in weights][0:MAX_ITEMS])
            conditions += f' AND cz.weight IN ({weights})'

        regions = []
        for v in request.query_params.get('region', '').split(','):
            if v.strip():
                regions.append(str_value(v.strip()))

        if regions:
            regions = ', '.join([f"'{v}'" for v in regions][0:MAX_ITEMS])
            conditions += f' AND dg.project_publications::text IN ({regions})'
            dgis_joined = True

        if inns:
            inns = ', '.join([str(v) for v in inns][0:MAX_ITEMS])
            conditions = f'AND cz.inn IN ({inns})'

        if gtins:
            gtins = ', '.join([f"'{v}'" for v in gtins][0:MAX_ITEMS])
            conditions += f' AND cz.gt::text IN ({gtins})'

        # product_name

        product_names = []
        for v in request.query_params.get('product_name', '').split(','):
            if v.strip():
                product_names.append(v.strip())

        if product_names:
            product_names = ', '.join([f"'{v}'" for v in product_names][0:MAX_ITEMS])
            conditions += f' AND cz.product_name::text IN ({product_names})'

        # position

        positions = []
        for v in request.query_params.get('position', '').split(','):
            if v.strip():
                positions.append(v.strip())

        if positions:
            positions = ', '.join([f"'{v}'" for v in positions][0:MAX_ITEMS])
            conditions += f' AND cz.position::text IN ({positions})'

        # dates

        from_date = date_value(request.query_params.get('from_date'))
        to_date = date_value(request.query_params.get('to_date'))

        if from_date:
            conditions += f' AND cz.date::date >= to_date(\'{from_date}\', \'YYYY-MM-DD\')'

        if to_date:
            conditions += f' AND cz.date::date <= to_date(\'{to_date}\', \'YYYY-MM-DD\')'

        return conditions, dgis_joined

    @extend_schema(
        parameters=[
        ],
        tags=['data'],
        summary='Розничные продавцы по ИНН',
    )
    def get(self, request, *args, **kwargs):

        conditions, dgis_joined = self.make_condition(self.request)

        if dgis_joined:
            dgis_join = 'RIGHT OUTER JOIN data_dgisrecord AS dg ON cz.inn = ANY(dg.inn)'
        else:
            dgis_join = ''

        # query

        cursor = connection.cursor()

        sql = """
        SELECT
            cz.inn,
            cz.owner_name,
            SUM(cz.out_retail) AS retail_sales
        FROM data_chzrecord AS cz
        {dgis_join}
        WHERE 1=1 {conditions}
        GROUP BY cz.inn, cz.owner_name
        HAVING SUM(cz.out_retail) > 0
        ORDER BY retail_sales DESC
        """.format(
            conditions=conditions,
            dgis_join=dgis_join
        )

        try:
            cursor.execute(sql)
            records = cursor.fetchall()
        except Exception as e:
            cursor.close
            raise e

        res = []

        for r in records:
            res.append({
                'name': r[1],
                'total': r[2],
                'inn': r[0]
            })

        return Response(res, status=status.HTTP_200_OK)


class CHZReport2View(APIView):
    """
    Розничные продажи по GTIN
    """

    permission_classes = [IsAuthenticated]

    def make_condition(self, request):

        MAX_ITEMS = 5

        conditions = ''
        dgis_joined = False

        gtins = []
        for gtin in request.query_params.get('gtin', '').split(','):
            try:
                gtin_value = int(gtin.strip())
            except ValueError:
                pass
            else:
                gtins.append(gtin.strip())

        inns = []
        for v in request.query_params.get('inn', '').split(','):
            try:
                inn = int(v.strip())
            except ValueError:
                pass
            else:
                inns.append(inn)

        regions = []
        for v in request.query_params.get('region', '').split(','):
            if v.strip():
                regions.append(str_value(v.strip()))

        if inns:
            inns = ', '.join([str(v) for v in inns][0:MAX_ITEMS])
            conditions = f'AND cz.inn IN ({inns})'

        if gtins:
            gtins = ', '.join([f"'{v}'" for v in gtins][0:MAX_ITEMS])
            conditions += f' AND cz.gt::text IN ({gtins})'

        if regions:
            regions = ', '.join([f"'{v}'" for v in regions][0:MAX_ITEMS])
            conditions += f' AND dg.project_publications::text IN ({regions})'
            dgis_joined = True

        # dates

        from_date = date_value(request.query_params.get('from_date'))
        to_date = date_value(request.query_params.get('to_date'))

        if from_date:
            conditions += f' AND cz.date::date >= to_date(\'{from_date}\', \'YYYY-MM-DD\')'

        if to_date:
            conditions += f' AND cz.date::date <= to_date(\'{to_date}\', \'YYYY-MM-DD\')'

        return conditions, dgis_joined

    @extend_schema(
        parameters=[
        ],
        tags=['data'],
        summary='Розничные продажи по GTIN',
    )
    def get(self, request, *args, **kwargs):

        # query

        conditions, dgis_joined = self.make_condition(self.request)

        if dgis_joined:
            dgis_join = 'RIGHT OUTER JOIN data_dgisrecord AS dg ON cz.inn = ANY(dg.inn)'
        else:
            dgis_join = ''

        sql = """
        SELECT
            cz.gt,
            cz.product_name,
            SUM(cz.out_retail) AS retail_sales
        FROM data_chzrecord AS cz
        {dgis_join}
        WHERE 1=1 {conditions}
        GROUP BY cz.gt, cz.product_name
        HAVING SUM(cz.out_retail) > 0
        ORDER BY retail_sales DESC
        """.format(
            conditions=conditions,
            dgis_join=dgis_join
        )

        cursor = connection.cursor()

        try:
            cursor.execute(sql)
            records = cursor.fetchall()
        except Exception as e:
            cursor.close
            raise e

        res = []

        for r in records:
            res.append({
                'gt': r[0],
                'product_name': r[1],
                'total': r[2]
            })

        return Response(res, status=status.HTTP_200_OK)


class CHZReport3View(APIView):
    """
    Оптовые покупатели
    """

    permission_classes = [IsAuthenticated]

    def make_condition(self, request):

        MAX_ITEMS = 5

        conditions = ''
        dgis_joined = False

        gtins = []
        for gtin in request.query_params.get('gtin', '').split(','):
            try:
                gtin_value = int(gtin.strip())
            except ValueError:
                pass
            else:
                gtins.append(gtin.strip())

        inns = []
        for v in request.query_params.get('inn', '').split(','):
            try:
                inn = int(v.strip())
            except ValueError:
                pass
            else:
                inns.append(inn)

        regions = []
        for v in request.query_params.get('region', '').split(','):
            if v.strip():
                regions.append(str_value(v.strip()))

        if inns:
            inns = ', '.join([str(v) for v in inns][0:MAX_ITEMS])
            conditions = f'AND cz.inn IN ({inns})'

        if gtins:
            gtins = ', '.join([f"'{v}'" for v in gtins][0:MAX_ITEMS])
            conditions += f' AND cz.gt::text IN ({gtins})'

        if regions:
            regions = ', '.join([f"'{v}'" for v in regions][0:MAX_ITEMS])
            conditions += f' AND dg.project_publications::text IN ({regions})'
            dgis_joined = True

        # dates

        from_date = date_value(request.query_params.get('from_date'))
        to_date = date_value(request.query_params.get('to_date'))

        if from_date:
            conditions += f' AND cz.date::date >= to_date(\'{from_date}\', \'YYYY-MM-DD\')'

        if to_date:
            conditions += f' AND cz.date::date <= to_date(\'{to_date}\', \'YYYY-MM-DD\')'

        return conditions, dgis_joined

    @extend_schema(
        parameters=[
        ],
        tags=['data'],
        summary='Оптовые покупатели',
    )
    def get(self, request, *args, **kwargs):

        # query

        conditions, dgis_joined = self.make_condition(self.request)

        if dgis_joined:
            dgis_join = 'RIGHT OUTER JOIN data_dgisrecord AS dg ON cz.inn = ANY(dg.inn)'
        else:
            dgis_join = ''

        sql = """
        SELECT
            cz.inn,
            cz.owner_name,
            SUM(cz.in_russia) AS whosale_purchase
        FROM data_chzrecord AS cz
        {dgis_join}
        WHERE 1=1 {conditions}
        GROUP BY cz.inn, cz.owner_name
        HAVING SUM(cz.in_russia) > 0
        ORDER BY whosale_purchase DESC
        """.format(
            conditions=conditions,
            dgis_join=dgis_join
        )

        cursor = connection.cursor()

        try:
            cursor.execute(sql)
            records = cursor.fetchall()
        except Exception as e:
            cursor.close
            raise e

        res = []

        for r in records:
            res.append({
                'name': r[1],
                'total': r[2],
                'inn': r[0]
            })

        return Response(res, status=status.HTTP_200_OK)


class CHZReport4View(APIView):
    """
    GTIN в опте
    """

    permission_classes = [IsAuthenticated]

    def make_condition(self, request):

        MAX_ITEMS = 5

        conditions = ''
        dgis_joined = False

        gtins = []
        for gtin in request.query_params.get('gtin', '').split(','):
            try:
                gtin_value = int(gtin.strip())
            except ValueError:
                pass
            else:
                gtins.append(gtin.strip())

        inns = []
        for v in request.query_params.get('inn', '').split(','):
            try:
                inn = int(v.strip())
            except ValueError:
                pass
            else:
                inns.append(inn)

        regions = []
        for v in request.query_params.get('region', '').split(','):
            if v.strip():
                regions.append(str_value(v.strip()))

        if inns:
            inns = ', '.join([str(v) for v in inns][0:MAX_ITEMS])
            conditions = f'AND cz.inn IN ({inns})'

        if gtins:
            gtins = ', '.join([f"'{v}'" for v in gtins][0:MAX_ITEMS])
            conditions += f' AND cz.gt::text IN ({gtins})'

        if regions:
            regions = ', '.join([f"'{v}'" for v in regions][0:MAX_ITEMS])
            conditions += f' AND dg.project_publications::text IN ({regions})'
            dgis_joined = True

        # dates

        from_date = date_value(request.query_params.get('from_date'))
        to_date = date_value(request.query_params.get('to_date'))

        if from_date:
            conditions += f' AND cz.date::date >= to_date(\'{from_date}\', \'YYYY-MM-DD\')'

        if to_date:
            conditions += f' AND cz.date::date <= to_date(\'{to_date}\', \'YYYY-MM-DD\')'

        return conditions, dgis_joined

    @extend_schema(
        parameters=[
        ],
        tags=['data'],
        summary='GTIN в опте',
    )
    def get(self, request, *args, **kwargs):

        # query

        conditions, dgis_joined = self.make_condition(self.request)

        if dgis_joined:
            dgis_join = 'RIGHT OUTER JOIN data_dgisrecord AS dg ON cz.inn = ANY(dg.inn)'
        else:
            dgis_join = ''

        sql = """
        SELECT
            cz.gt,
            cz.product_name,
            SUM(cz.in_russia) AS wholesale_sales
        FROM data_chzrecord AS cz
        {dgis_join}
        WHERE 1=1 {conditions}
        GROUP BY cz.gt, cz.product_name
        HAVING SUM(cz.in_russia) > 0
        ORDER BY wholesale_sales DESC
        """.format(
            conditions=conditions,
            dgis_join=dgis_join
        )

        cursor = connection.cursor()

        try:
            cursor.execute(sql)
            records = cursor.fetchall()
        except Exception as e:
            cursor.close
            raise e

        res = []

        for r in records:
            res.append({
                'name': r[1],
                'total': r[2],
                'gt': r[0]
            })

        return Response(res, status=status.HTTP_200_OK)


class CHZReport5View(APIView):
    """
    Динамика продаж розничных продавцов / Розница - ИНН
    """

    permission_classes = [IsAuthenticated]

    def make_condition(self, request):

        MAX_ITEMS = 5

        conditions = ''
        dgis_joined = False

        product_name = request.query_params.get('product_name', '')
        position = request.query_params.get('position', '')

        gtins = []
        for gtin in request.query_params.get('gtin', '').split(','):
            try:
                gtin_value = int(gtin.strip())
            except ValueError:
                pass
            else:
                gtins.append(gtin.strip())

        inns = []
        for v in request.query_params.get('inn', '').split(','):
            try:
                inn = int(v.strip())
            except ValueError:
                pass
            else:
                inns.append(inn)

        weights = []
        for v in request.query_params.get('weight', '').split(','):
            try:
                weight = int(v.strip())
            except ValueError:
                pass
            else:
                weights.append(weight)

        if weights:
            weights = ', '.join([f"'{v}'" for v in weights][0:MAX_ITEMS])
            conditions += f' AND cz.weight IN ({weights})'

        regions = []
        for v in request.query_params.get('region', '').split(','):
            if v.strip():
                regions.append(str_value(v.strip()))

        if regions:
            regions = ', '.join([f"'{v}'" for v in regions][0:MAX_ITEMS])
            conditions += f' AND dg.project_publications::text IN ({regions})'
            dgis_joined = True

        if inns:
            inns = ', '.join([str(v) for v in inns][0:MAX_ITEMS])
            conditions = f'AND cz.inn IN ({inns})'

        if gtins:
            gtins = ', '.join([f"'{v}'" for v in gtins][0:MAX_ITEMS])
            conditions += f' AND cz.gt::text IN ({gtins})'

        # product_name

        product_names = []
        for v in request.query_params.get('product_name', '').split(','):
            if v.strip():
                product_names.append(v.strip())

        if product_names:
            product_names = ', '.join([f"'{v}'" for v in product_names][0:MAX_ITEMS])
            conditions += f' AND cz.product_name::text IN ({product_names})'

        # position

        positions = []
        for v in request.query_params.get('position', '').split(','):
            if v.strip():
                positions.append(v.strip())

        if positions:
            positions = ', '.join([f"'{v}'" for v in positions][0:MAX_ITEMS])
            conditions += f' AND cz.position::text IN ({positions})'

        # dates

        from_date = date_value(request.query_params.get('from_date'))
        to_date = date_value(request.query_params.get('to_date'))

        if from_date:
            conditions += f' AND cz.date::date >= to_date(\'{from_date}\', \'YYYY-MM-DD\')'

        if to_date:
            conditions += f' AND cz.date::date <= to_date(\'{to_date}\', \'YYYY-MM-DD\')'

        return conditions, dgis_joined

    @extend_schema(
        parameters=[
        ],
        tags=['data'],
        summary='Динамика продаж розничных продавцов / Розница - ИНН'
    )
    def get(self, request, *args, **kwargs):

        conditions, dgis_joined = self.make_condition(self.request)

        # query

        cursor = connection.cursor()

        sql = """
        SELECT
            cz.inn,
            cz.owner_name,
            SUM(cz.out_retail) AS retail_sales,
            dg.clat,
            dg.clong,
            dg.project_publications,
            to_char(date, 'YYYY-MM') AS month_year
        FROM data_chzrecord AS cz
        RIGHT OUTER JOIN data_dgisrecord AS dg ON cz.inn = ANY(dg.inn)
        WHERE 1=1 {conditions}
        GROUP BY cz.inn, cz.owner_name, dg.clat, dg.clong, dg.project_publications, month_year
        ORDER BY month_year DESC
        """.format(
            conditions=conditions
        )

        try:
            cursor.execute(sql)
            records = cursor.fetchall()
        except Exception as e:
            cursor.close
            raise e

        res = []

        for r in records:
            res.append({
                'name': r[1],
                'total': r[2],
                'inn': r[0],
                'date': r[6],
                'lat': r[3],
                'long': r[4],
                'city': r[5]
            })

        return Response(res, status=status.HTTP_200_OK)
