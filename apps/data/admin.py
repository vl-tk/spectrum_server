from admin_cursor_paginator import CursorPaginatorAdmin
from django.contrib import admin

from apps.data.models import CHZRecord

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
