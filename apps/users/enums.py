from enum import Enum

from django.db import models
from django.utils.translation import gettext_lazy as _


class UserStatuses(Enum):
    ACTIVE = 0
    HARD_BANNED = 1


class UserTypes(models.IntegerChoices):
    CLIENT = 0
    PUBLISHER = 1
    STAFF = 2
