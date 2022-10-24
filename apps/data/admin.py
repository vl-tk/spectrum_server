from admin_cursor_paginator import CursorPaginatorAdmin
from apps.data.models import CHZRecord, DGisRecord
from django.contrib import admin

# from .admin_opt import OptAdmin


@admin.register(CHZRecord)
class CHZRecordAdmin(CursorPaginatorAdmin):

    show_full_result_count = False

    list_display = [
        'pk',
        'product_name',
        'owner_name',
        'inn',
        'prid',
        'gt',
        'pg_name',
        'producer_name',
        'mrp',
        'in_russia',
        'out_total',
        'out_whosale',
        'out_retail',
        'out_recycle',
        'date'
    ]

    search_fields = [
        'product_name',
        'owner_name',
        'inn',
    ]

    list_filter = [
    ]


@admin.register(DGisRecord)
class DGisRecordAdmin(admin.ModelAdmin):

    show_full_result_count = False

    list_display = [
        'name',
        'brand',
        'legal_name',
        'org_form',
        'branch_legal_name',
        'branch_org_name',
        'extension',
        'extension_addition',
        'division',
        'division_extension',
        'project_publications',
        'unit',
        'street',
        'address',
        'number_of_floors',
        'building_purpose',
        'phone_area_code',
        'phones',
        'emails',
        'web_alias',
        'web_sites',
        'categories',
        'inn_ogrn',
        'inn',
    ]

    search_fields = [
    ]

    list_filter = [
    ]
