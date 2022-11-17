import logging

from apps.events.models import Event
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

logger = logging.getLogger('django')


class EventSerializer(serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = [
            'pk',
            'created_at',
            'updated_at'
        ]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # ret['naimenovanie_organizatsii'] = instance.eav.naimenovanie_organizatsii
        # ret['brend'] = instance.eav.brend
        # ret['juridicheskoe_nazvanie'] = instance.eav.juridicheskoe_nazvanie
        # ret['organizatsionno_pravovaja_forma'] = instance.eav.organizatsionno_pravovaja_forma
        # ret['source_filename'] = instance.eav.source_filename
        return ret
