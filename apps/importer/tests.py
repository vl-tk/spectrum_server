import pytest
from apps.users.models import Region
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from utils.test import get_test_excel_file


@pytest.mark.django_db
def test_import_excel_file_events(unauthorized_client):

    resp = unauthorized_client.get(
        reverse('importer:import_file'),
        {
            'data_type': 'event',
            'file': get_test_excel_file()[0]
        }
    )
    assert resp.status_code == status.HTTP_200_OK
