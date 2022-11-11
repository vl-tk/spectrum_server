import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from utils.test import get_test_excel_file


@pytest.mark.django_db
def test_list_clients(authorized_client):
    resp = authorized_client.get(
        reverse('events:list_events')
    )
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.data) == 0
