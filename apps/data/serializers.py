from apps.data.models import CHZRecord, DGisRecord
from django.db import models
from rest_framework import serializers


class CHZRecordSerializer(serializers.ModelSerializer):

    class Meta:
        model = CHZRecord
        fields = '__all__'
        read_only_fields = ['pk']
