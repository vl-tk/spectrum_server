import copy
import logging
from pathlib import Path
from typing import *

from apps.log_app.models import LogRecord
from apps.users.serializers import UserSerializer
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

logger = logging.getLogger('django')


class LogRecordSerializer(serializers.ModelSerializer):

    user = UserSerializer(read_only=True)

    class Meta:
        model = LogRecord
        fields = [
            'message',
            'user',
            'content_type',
            'object_id',
            'created_at',
            'updated_at'
        ]
