import logging

from apps.importer.serializers import ImportSerializer
from django.conf import settings
from django.http import Http404
from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger('django')


class ImportExcelView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(name='data_type', required=True, type=str),
            OpenApiParameter(name='file', required=True, type=OpenApiTypes.BINARY), # TODO:
            OpenApiParameter(name='force_rewrite', required=False, type=str)
        ],
        tags=['import'],
        summary="Импорт"
    )
    def post(self, request, *args, **kwargs):

        serializer = ImportSerializer(
            data=request.data,
            context={
                'request': request,
            }
        )
        serializer.is_valid(raise_exception=True)
        imported, total = serializer.import_data()

        if imported > 0:
            return Response(f'Imported: {imported}/{total}', status=status.HTTP_200_OK)

        return Response(f'Imported {imported}/{total}. Please contact administrator', status=status.HTTP_500_INTERNAL_SERVER_ERROR)
