import operator

from apps.users.enums import Region
from apps.users.models import Client
from apps.users.serializers import ClientSerializer
from django.db.models import ImageField, Q
from django.db.models.fields.files import ImageFieldFile
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.html import format_html, strip_tags
# from django_filters.rest_framework import FilterSet
# from django_filters.rest_framework.filters import CharFilter
from rest_framework import generics, permissions, status
from rest_framework.response import Response
