from django.contrib import admin
from eav.admin import BaseEntityAdmin
from eav.forms import BaseDynamicEntityForm

from .models import Event


class EventAdminForm(BaseDynamicEntityForm):
    model = Event

    # TODO: make source_file non editable


@admin.register(Event)
class EventAdmin(BaseEntityAdmin):

    form = EventAdminForm

    search_fields = []

    list_display = [
        'pk',
        # 'field_naimenovanie_organizatsii',
        # 'field_brend',
        # 'field_juridicheskoe_nazvanie',
        # 'field_organizatsionno_pravovaja_forma',
        # 'field_source_filename',
        # 'field_test',
        'sort',
        'created_at',
        'updated_at'
    ]

    def field_naimenovanie_organizatsii(self, obj):
        return obj.eav.Naimenovanie_organizatsii

    def field_brend(self, obj):
        return obj.eav.Brend

    def field_juridicheskoe_nazvanie(self, obj):
        return obj.eav.Juridicheskoe_nazvanie

    def field_organizatsionno_pravovaja_forma(self, obj):
        return obj.eav.Organizatsionno_pravovaja_forma

    def field_source_filename(self, obj):
        return obj.eav.source_filename

    # def field_test(self, obj):
    #     try:
    #         return obj.eav.test
    #     except AttributeError:
    #         pass
