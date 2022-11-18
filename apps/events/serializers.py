import logging

from apps.events.models import Event
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

logger = logging.getLogger('django')


class EventSerializer(serializers.ModelSerializer):

    fields = serializers.DictField(required=True)

    class Meta:
        model = Event
        fields = [
            'pk',
            'fields',
            'sort',
            'created_at',
            'updated_at'
        ]

        read_only_fields = [
            'pk',
            'created_at',
            'updated_at'
        ]

    def validate(self, attrs):
        return attrs

    def save(self, *args, **kwargs):
        for k, v in self.validated_data.get('fields', {}).items():
            setattr(self.instance.eav, k, v)
        self.instance.save()

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # ret['naimenovanie_organizatsii'] = instance.eav.naimenovanie_organizatsii
        # ret['brend'] = instance.eav.brend
        # ret['juridicheskoe_nazvanie'] = instance.eav.juridicheskoe_nazvanie
        # ret['organizatsionno_pravovaja_forma'] = instance.eav.organizatsionno_pravovaja_forma
        # ret['source_filename'] = instance.eav.source_filename
        return ret
