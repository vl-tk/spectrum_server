import pytest
from apps.data.models import CHZRecord
from apps.events.models import Event
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
@pytest.mark.vcr()
def test_report_events(authorized_client, imported_events, test_file_remove):

    assert Event.objects.count() == 15

    resp = authorized_client.get(
        reverse('events:event_report'),
        {
            'type': 'avg_per_month',
            'value_field': 'bjudzhet',
            'date_field': 'data_nachala',
        }
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() =={'01.2022': '338.71', '02.2022': '100.00'}

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


@pytest.mark.django_db
def test_chz_report_filter(authorized_client):

    resp = authorized_client.get(
        reverse('reports:chz_report_filter_regions')
    )
    assert resp.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_chz_report1(authorized_client, chz_records_mini):

    CHZRecord.objects.count() == 6

    resp = authorized_client.get(
        reverse('reports:chz_report1'),
        {
            # 'inn': ''
        }
    )
    assert resp.status_code == status.HTTP_200_OK
