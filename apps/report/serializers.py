import copy
import logging
from pathlib import Path
from typing import *

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

logger = logging.getLogger('django')
