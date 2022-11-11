import pytest
from apps.events.models import Event
from apps.users.models import Region
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from utils.test import get_test_document_files, get_test_excel_file


@pytest.mark.django_db
def test_import_excel_file_events(authorized_client, test_file_remove):

    resp = authorized_client.post(
        reverse('importer:import_file'),
        {
            'data_type': 'event',
            'file': get_test_excel_file()[0]
        },
        format='multipart'
    )

    assert resp.status_code == status.HTTP_200_OK
    assert Event.objects.count() == 10


@pytest.mark.django_db
def test_import_incorrect_file_events(authorized_client, test_file_remove):

    resp = authorized_client.post(
        reverse('importer:import_file'),
        {
            'data_type': 'event',
            'file': get_test_document_files()[0]  # document = pdf, docx, not excel
        },
        format='multipart'
    )

    assert resp.status_code == status.HTTP_400_BAD_REQUEST
