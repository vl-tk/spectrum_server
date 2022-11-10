import logging

from django.conf import settings
from django.http import Http404
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger('django')


class ImportExcelView(APIView):

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):

        # res = ImportSerializer(s).data

        res = {}

        return Response(res, status=status.HTTP_200_OK)
