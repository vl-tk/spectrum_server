from admin_cursor_paginator import CursorPaginatorAdmin
from apps.data.models import CHZRecord, CityRecord, DGisRecord
from django.contrib import admin
from django.utils.html import strip_tags
from simple_history.admin import SimpleHistoryAdmin

# from .admin_opt import OptAdmin


@admin.register(CHZRecord)
class CHZRecordAdmin(SimpleHistoryAdmin, admin.ModelAdmin): # CursorPaginatorAdmin):

    show_full_result_count = False

    list_display = [
        'pk',
        'product_name',
        'owner_name',
        'inn',
        'is_edited_manually',
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
        'date',
        'updated_at',
        'created_at'
    ]

    search_fields = [
        'product_name',
        'owner_name',
        'inn',
    ]

    list_filter = [
        'is_edited_manually',
        'created_at',
        'updated_at'
    ]

    def save_model(self, request, obj, form, change):
        changed_fields = [f for f in form.changed_data if f != 'is_edited_manually']
        if changed_fields:
            obj.is_edited_manually = True
        super().save_model(request, obj, form, change)


def make_short_text(text: str) -> str:
    text = strip_tags(text).replace('&nbsp;', ' ')
    if len(text) > 100:
        return text[0:100] + '...'
    return text


@admin.register(DGisRecord)
class DGisRecordAdmin(SimpleHistoryAdmin):

    show_full_result_count = False

    list_display = [
        'pk',
        'name',
        'brand',
        'inn',
        'is_edited_manually',
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

        'sh_phone_area_code',
        'sh_phones',
        'emails',
        'web_alias',
        'web_sites',
        'categories',
        'inn_ogrn',
        'updated_at',
        'created_at'
    ]

    search_fields = [
        'name',
        'brand',
        'inn'
    ]

    list_filter = [
        'is_edited_manually',
        'created_at',
        'updated_at'
    ]

    def sh_phone_area_code(self, obj):
        if obj.phone_area_code:
            return make_short_text(obj.phone_area_code)
        return ""

    sh_phone_area_code.short_description = 'Код телефонной зоны'

    def sh_phones(self, obj):
        if obj.phones:
            return make_short_text(obj.phones)
        return ""

    sh_phones.short_description = 'Телефоны'

    def save_model(self, request, obj, form, change):
        changed_fields = [f for f in form.changed_data if f != 'is_edited_manually']
        if changed_fields:
            obj.is_edited_manually = True
        super().save_model(request, obj, form, change)


@admin.register(CityRecord)
class CityRecord(admin.ModelAdmin):

    list_display = [
        'pk',
        'city',
        'region',
        'clat',
        'clong',
        'updated_at',
        'created_at'
    ]

    search_fields = [
        'city',
        'region'
    ]

    list_filter = [
        'created_at',
        'updated_at'
    ]
