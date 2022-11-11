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
