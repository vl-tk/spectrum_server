import pytest
from apps.events.models import Event
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from utils.test import get_test_document_files, get_test_excel_file


@pytest.mark.django_db
def test_report_events(authorized_client, imported_events, test_file_remove):

    assert Event.objects.count() == 42

    resp = authorized_client.get(
        reverse('events:event_report'),
        {
            'type': 'avg_per_month',
            'value_field': 'bjudzhet',
            'date_field': 'data_nachala',
        }
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == '{"(1, 2022)":151.6129032258,"(2, 2022)":100.0}'

    resp = authorized_client.get(
        reverse('events:event_report'),
        {
            'type': 'total_per_month',
            'value_field': 'bjudzhet',
            'date_field': 'data_nachala',
        }
    )
    assert resp.status_code == status.HTTP_200_OK

    resp = authorized_client.get(
        reverse('events:event_report'),
        {
            'type': 'avg_per_day',
            'value_field': 'bjudzhet',
            'date_field': 'data_nachala',
        }
    )
    assert resp.status_code == status.HTTP_200_OK

    resp = authorized_client.get(
        reverse('events:event_report'),
        {
            'type': 'total_per_day',
            'value_field': 'bjudzhet',
            'date_field': 'data_nachala',
        }
    )
    assert resp.status_code == status.HTTP_200_OK
