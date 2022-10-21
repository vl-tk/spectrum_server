from apps.users.models import Client
from django.db import models
from rest_framework import serializers


class ClientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Client
        fields = [
            'pk',
            'name',
            'region',
            "logo",
        ]
        read_only_fields = ['pk']
