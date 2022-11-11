import logging

from apps.importer.serializers import ImportSerializer
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

    @extend_schema(
        parameters=[ImportSerializer],
        # request={'application/json': ImportSerializer},
        # parameters=[
        #     OpenApiParameter(name='backend', description="'google-oauth2', 'facebook'", required=True, type=str),
        # ],
        # responses={
        #     status.HTTP_200_OK: ImportSerializer(),
        #     status.HTTP_403_FORBIDDEN: '',
        # },
        summary=""
    )
    def post(self, request, *args, **kwargs):

        serializer = ImportSerializer(
            data=request.data,
            context={
                'request': request,
            }
        )
        serializer.is_valid(raise_exception=True)
        res = serializer.import_data()

        return Response(res, status=status.HTTP_200_OK)
