from django.contrib import admin

from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [
        'pk',
        'source_file',
        'created_at',
        'updated_at'
    ]

    # TODO: почему не работает obj.eav.source_filename как в документации?
    # TODO: подумать как ускорить вывод
    def source_file(self, obj):
        return obj.eav.get_values_dict()['source_filename']
