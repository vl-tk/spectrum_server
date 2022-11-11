import logging

from apps.events.models import Event
from apps.events.serializers import EventSerializer
from django.conf import settings
from django.http import Http404
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger('django')


class EventListView(APIView):

    permission_classes = [AllowAny]

    @extend_schema(
        parameters=[
            # OpenApiParameter(name='search', required=False, type=str),
            # OpenApiParameter(name='year', required=False, type=int),
        ],
        # responses={status.HTTP_200_OK: OrderSerializer()},
        summary='Акции'
    )
    def get(self, request, *args, **kwargs):

        # TODO:
        events = list(Event.objects.all())

        serializer = EventSerializer(
            data=events,
            many=True
        )
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
