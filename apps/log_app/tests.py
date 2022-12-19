import pytest
from apps.log_app.models import LogRecord
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from utils.test import get_test_excel_file


@pytest.mark.django_db
def test_list_logs(authorized_client, user):

    LogRecord.objects.create(
        user=user,
        message='123456',
        content_type_id=16
    )

    LogRecord.objects.create(
        user=user,
        message='12345678',
        content_type_id=16
    )

    resp = authorized_client.get(
        reverse('logs:list_logs')
    )
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.data) == 2


@pytest.mark.django_db
def test_create_logs(authorized_client, user):

    LogRecord.objects.create(
        user=user,
        message='123456',
        content_type_id=16
    )

    # resp = authorized_client.post(
    #     reverse('logs:list_logs'),
    #     {
    #         'message': 'log message'
    #     }
    # )
    # assert resp.status_code == status.HTTP_200_OK
    # assert len(resp.data) == 2
