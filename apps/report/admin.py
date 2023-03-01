from apps.data.tasks import rebuild_abc_report
from apps.report.models import ABCGTINRecord
from django.contrib import admin


@admin.register(ABCGTINRecord)
class ABCGTINRecordAdmin(admin.ModelAdmin):

    def rebuild_report(self, request, queryset):
        from apps.data.views_reports import CHZReport6View
        CHZReport6View().prepare_report()

        # rebuild_abc_report.delay()
        # check_translate_task.delay("Recipe", pks_of_model)

    rebuild_report.short_description = "Сгенерировать все записи отчета заново"

    actions = [rebuild_report]

    list_display = [
        'pk',
        'gtin',
        'product_name',
        'retail_sales',
        'total_sales',
        'retail_sales_share',
        'acc_retail_sales_share',
        'region',
        'group',
        'updated_at',
        'created_at'
    ]

    search_fields = [
        'gtin',
        'region',
        'group',
        'product_name'
    ]

    list_filter = [
        'region',
        'group',
        'created_at',
        'updated_at'
    ]
