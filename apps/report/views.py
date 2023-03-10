import logging
from collections import defaultdict
from datetime import datetime
from typing import *

import pytz
from apps.data.models import CHZRecord, DGisPlace, DGisRecord, GTINRecordMV
from apps.data.serializers import CHZRecordSerializer
from apps.data.utils import (get_cities, get_positions, get_products,
                             get_regions)
from apps.importer.services_data import EAVDataProvider
from apps.log_app.models import LogRecord
from apps.report.models import ABCGTINRecord
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
from utils.info import get_region_coords

logger = logging.getLogger('django')


def str_value(value):
    res = [v for v in str(value) if v.isalpha() or v == ' ']
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
        summary='Список регионов 2ГИС для фильтра',
    )
    def get(self, request, *args, **kwargs):
        values = get_regions()
        return Response(values, status=status.HTTP_200_OK)


class CHZRecordCityFilterView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
        ],
        tags=['data'],
        summary='Список городов 2ГИС для фильтра',
    )
    def get(self, request, *args, **kwargs):
        values = get_cities()
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

        name = request.query_params.get('name')

        if name:
            records = GTINRecordMV.objects.filter(Q(product_name__icontains=name)|Q(id__icontains=name))
        else:
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

        cities = []
        for v in request.query_params.get('city', '').split(','):
            if v.strip():
                cities.append(str_value(v.strip()))

        if regions:
            regions = ', '.join([f"'{v}'" for v in regions][0:MAX_ITEMS])
            conditions += f' AND dgp.region::text IN ({regions})'
            dgis_joined = True

        if cities:
            cities = ', '.join([f"'{v}'" for v in cities][0:MAX_ITEMS])
            conditions += f' AND dgp.city::text IN ({cities})'
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

            dgis_join = """
            RIGHT OUTER JOIN data_dgisrecord AS dg ON cz.inn = ANY(dg.inn)
            INNER JOIN data_dgisplace AS dgp ON dgp.id = dg.dgis_place_id
            """

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

        cities = []
        for v in request.query_params.get('city', '').split(','):
            if v.strip():
                cities.append(str_value(v.strip()))

        if regions:
            regions = ', '.join([f"'{v}'" for v in regions][0:MAX_ITEMS])
            conditions += f' AND dgp.region::text IN ({regions})'
            dgis_joined = True

        if cities:
            cities = ', '.join([f"'{v}'" for v in cities][0:MAX_ITEMS])
            conditions += f' AND dgp.city::text IN ({cities})'
            dgis_joined = True

        if inns:
            inns = ', '.join([str(v) for v in inns][0:MAX_ITEMS])
            conditions = f'AND cz.inn IN ({inns})'

        if gtins:
            gtins = ', '.join([f"'{v}'" for v in gtins][0:MAX_ITEMS])
            conditions += f' AND cz.gt::text IN ({gtins})'

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

            dgis_join = """
            RIGHT OUTER JOIN data_dgisrecord AS dg ON cz.inn = ANY(dg.inn)
            INNER JOIN data_dgisplace AS dgp ON dgp.id = dg.dgis_place_id
            """

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

        if inns:
            inns = ', '.join([str(v) for v in inns][0:MAX_ITEMS])
            conditions = f'AND cz.inn IN ({inns})'

        if gtins:
            gtins = ', '.join([f"'{v}'" for v in gtins][0:MAX_ITEMS])
            conditions += f' AND cz.gt::text IN ({gtins})'

        regions = []
        for v in request.query_params.get('region', '').split(','):
            if v.strip():
                regions.append(str_value(v.strip()))

        cities = []
        for v in request.query_params.get('city', '').split(','):
            if v.strip():
                cities.append(str_value(v.strip()))

        if regions:
            regions = ', '.join([f"'{v}'" for v in regions][0:MAX_ITEMS])
            conditions += f' AND dgp.region::text IN ({regions})'
            dgis_joined = True

        if cities:
            cities = ', '.join([f"'{v}'" for v in cities][0:MAX_ITEMS])
            conditions += f' AND dgp.city::text IN ({cities})'
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

            dgis_join = """
            RIGHT OUTER JOIN data_dgisrecord AS dg ON cz.inn = ANY(dg.inn)
            INNER JOIN data_dgisplace AS dgp ON dgp.id = dg.dgis_place_id
            """

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

        if inns:
            inns = ', '.join([str(v) for v in inns][0:MAX_ITEMS])
            conditions = f'AND cz.inn IN ({inns})'

        if gtins:
            gtins = ', '.join([f"'{v}'" for v in gtins][0:MAX_ITEMS])
            conditions += f' AND cz.gt::text IN ({gtins})'

        regions = []
        for v in request.query_params.get('region', '').split(','):
            if v.strip():
                regions.append(str_value(v.strip()))

        cities = []
        for v in request.query_params.get('city', '').split(','):
            if v.strip():
                cities.append(str_value(v.strip()))

        if regions:
            regions = ', '.join([f"'{v}'" for v in regions][0:MAX_ITEMS])
            conditions += f' AND dgp.region::text IN ({regions})'
            dgis_joined = True

        if cities:
            cities = ', '.join([f"'{v}'" for v in cities][0:MAX_ITEMS])
            conditions += f' AND dgp.city::text IN ({cities})'
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

            dgis_join = """
            RIGHT OUTER JOIN data_dgisrecord AS dg ON cz.inn = ANY(dg.inn)
            INNER JOIN data_dgisplace AS dgp ON dgp.id = dg.dgis_place_id
            """

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

        cities = []
        for v in request.query_params.get('city', '').split(','):
            if v.strip():
                cities.append(str_value(v.strip()))

        if regions:
            regions = ', '.join([f"'{v}'" for v in regions][0:MAX_ITEMS])
            conditions += f' AND dgp.region::text IN ({regions})'
            dgis_joined = True

        if cities:
            cities = ', '.join([f"'{v}'" for v in cities][0:MAX_ITEMS])
            conditions += f' AND dgp.city::text IN ({cities})'
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
        INNER JOIN data_dgisplace AS dgp ON dgp.id = dg.dgis_place_id
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


class CHZReport6View(APIView):
    """
    АВС-анализ относительно розничных продаж по регионам
    """

    permission_classes = [IsAuthenticated]

    def generate_report_records_to_db(self):
        """
        TODO: БАГ - не обновляются значения, если значения поменялись
        """

        ABCGTINRecord.objects.all().delete()

        for (country, region) in get_regions():

            if not region:
                continue

            regions = f"'{region}'"
            conditions = f" AND dgp.region::text IN ({regions})"

            sql = """
            SELECT
                cz.gt,
                cz.product_name,
                SUM(cz.out_retail) AS retail_sales
            FROM data_chzrecord AS cz
            RIGHT OUTER JOIN data_dgisrecord AS dg ON cz.inn = ANY(dg.inn)
            INNER JOIN data_dgisplace AS dgp ON dgp.id = dg.dgis_place_id
            WHERE 1=1 {conditions}
            GROUP BY cz.gt, cz.product_name
            HAVING SUM(cz.out_retail) > 0
            ORDER BY retail_sales DESC
            """.format(
                conditions=conditions
            )

            cursor = connection.cursor()

            try:
                cursor.execute(sql)
                records = cursor.fetchall()
            except Exception as e:
                cursor.close
                raise e

            res = []

            total = sum([r[2] for r in records])
            current_total = 0

            for r in records:

                current_total += r[2]
                percent = (r[2] / total) * 100
                acc_percent = (current_total / total) * 100

                if acc_percent <= 80:
                    group = 'A'
                elif acc_percent > 80 and acc_percent < 95:
                    group = 'B'
                else:
                    group = 'C'

                ABCGTINRecord.objects.create(
                    gtin=r[0],
                    product_name=r[1],
                    retail_sales=r[2],
                    total_sales=total,
                    retail_sales_share=percent,
                    acc_retail_sales_share=acc_percent,
                    region=region,
                    group=group
                )

    @extend_schema(
        parameters=[
        ],
        tags=['data'],
        summary='АВС-анализ относительно розничных продаж по регионам',
    )
    def get(self, request, *args, **kwargs):

        REGION_POINTS = get_region_coords()

        regions = []
        for v in request.query_params.get('region', '').split(','):
            if v.strip():
                regions.append(str_value(v.strip()))

        if regions:
            records = ABCGTINRecord.objects.filter(region__in=regions)
        else:
            records = ABCGTINRecord.objects.all()

        res = {}
        for r in records:

            region = r.region.strip()

            res[region] = {}
            res[region]['data'] = []
            res[region]['point'] = REGION_POINTS.get(region.strip(), '')

        for r in records:
            res[region]['data'].append({
                'gtin': r.gtin,
                'product_name': r.product_name,
                'retail_sales': r.retail_sales,
                'total_sales': r.total_sales,
                'retail_sales_share': r.retail_sales_share,
                'acc_retail_sales_share': r.acc_retail_sales_share,
                'group': r.group
            })

        return Response(res, status=status.HTTP_200_OK)


class CHZReport7View(APIView):
    """
    Справочник юниверса производителя

    РОЗНИЦА АДРЕС ИНН РЕГИОН

    Показывает список адресов розничных торговых точек, в которых продавался
    товар производителя за один выбранный период.

    Для работы данный раздел полезно синхронизировать с 2гис чтобы были видны
    контактные данные и выгрузка необходимой информации с фильтрацией по
    регионам.

    TODO: БАГ - Башляков - нет при фильтре по дате 2022-03-07
    """

    permission_classes = [IsAuthenticated]

    def make_condition(self, request):

        MAX_ITEMS = 5

        conditions = ''
        dgis_joined = False

        regions = []
        for v in request.query_params.get('region', '').split(','):
            if v.strip():
                regions.append(str_value(v.strip()))

        cities = []
        for v in request.query_params.get('city', '').split(','):
            if v.strip():
                cities.append(str_value(v.strip()))

        if regions:
            regions = ', '.join([f"'{v}'" for v in regions][0:MAX_ITEMS])
            conditions += f' AND dgp.region::text IN ({regions})'
            dgis_joined = True

        if cities:
            cities = ', '.join([f"'{v}'" for v in cities][0:MAX_ITEMS])
            conditions += f' AND dgp.city::text IN ({cities})'
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
        summary='Справочник юниверса производителя',
    )
    def get(self, request, *args, **kwargs):

        conditions, dgis_joined = self.make_condition(self.request)

        sql = """
        SELECT
            cz.inn,
            cz.owner_name,
            dgp.country,
            dgp.region,
            dgp.city,
            dgp.street,
            dgp.street_num
        FROM data_chzrecord AS cz
        RIGHT OUTER JOIN data_dgisrecord AS dg ON cz.inn = ANY(dg.inn)
        INNER JOIN data_dgisplace AS dgp ON dgp.id = dg.dgis_place_id
        WHERE 1=1 {conditions}
        GROUP BY
            cz.inn,
            cz.owner_name,
            dgp.country,
            dgp.region,
            dgp.city,
            dgp.street,
            dgp.street_num
        HAVING SUM(cz.out_retail) > 0
        ORDER BY cz.inn DESC
        """.format(
            conditions=conditions
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
                'inn': r[0],
                'name': r[1],
                'country': r[2],
                'region': r[3],
                'city': r[4],
                'street': r[5],
                'street_num': r[6]
            })

        return Response(res, status=status.HTTP_200_OK)
