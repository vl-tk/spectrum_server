from admin_cursor_paginator import CursorPaginatorAdmin
from apps.data.models import CHZRecord, City, DGisPlace, DGisRecord
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.db.models import Q
from django.utils.html import strip_tags
from simple_history.admin import SimpleHistoryAdmin

# from .admin_opt import OptAdmin


@admin.register(CHZRecord)
class CHZRecordAdmin(SimpleHistoryAdmin, admin.ModelAdmin): # CursorPaginatorAdmin):

    show_full_result_count = False

    list_display = [
        'pk',
        'product_name',
        'gt',
        'owner_name',
        'inn',
        'is_edited_manually',
        # 'pg_name',
        # 'producer_name',
        # 'prid',
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
        'gt'
    ]

    list_filter = [
        'is_edited_manually',
        # 'product_name',
        'producer_name',
        'pg_name',
        'weight',
        'gt',
        'date',
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

        'dgis_place',
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

        # additional, not from imported db
        'dgis_place',
        'clat',
        'clong',
        'city',

        'updated_at',
        'created_at'
    ]

    search_fields = [
        'name',
        'brand',
        'inn',
        'city',
        'unit'
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


@admin.register(City)
class City(admin.ModelAdmin):

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
        'region',
        'created_at',
        'updated_at'
    ]


class CoordsFilter(SimpleListFilter):
    title = 'coords'

    parameter_name = 'clat__isnull'

    def lookups(self, request, model_admin):

        queryset = model_admin.get_queryset(request)

        return (
            (0, f'Has coords'),
            (1, f'Without coords')
        )

    def choices(self, cl):
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == str(lookup),
                'query_string': cl.get_query_string({self.parameter_name: lookup, }, []),
                'display': title,
            }

    def queryset(self, request, queryset):
        if self.value():
            if self.value() == '0':
                return queryset.filter(Q(clat__isnull=False))
            if self.value() == '1':
                return queryset.filter(Q(clat__isnull=True))
        return queryset


class DGisRecordInline(admin.StackedInline):
    model = DGisRecord
    fields = [
        'unit'
    ]
    extra = 0


@admin.register(DGisPlace)
class DGisPlaceAdmin(admin.ModelAdmin):

    list_display = [
        'pk',
        'country',
        'region',
        'city',
        # 'district',
        'street',
        'street_num',
        'clat',
        'clong',
        'updated_at',
        'created_at'
    ]

    search_fields = [
        'country',
        'region',
        'city',
        'district',
        'street',
    ]

    list_filter = [
        CoordsFilter,
        'country',
        'region',
        'created_at',
        'updated_at'
    ]

    inlines = [
        DGisRecordInline,
    ]
