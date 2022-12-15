import pytest
from apps.events.models import Event
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from utils.test import get_test_document_files, get_test_excel_file


@pytest.mark.django_db
def test_report_events(authorized_client, imported_events, test_file_remove):

    assert Event.objects.count() == 42

    # 2. test retrieval

    resp = authorized_client.get(
        reverse('events:event_report'),
        {
            'type': 'budget_per_month'
        }
    )
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.data['results']) == 20  # default page size
