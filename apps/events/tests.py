import pytest
from apps.events.models import Event
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from utils.test import get_test_excel_file


@pytest.mark.django_db
def test_list_events(authorized_client, imported_events, test_file_remove):

    assert Event.objects.count() == 42

    # 2. test retrieval

    resp = authorized_client.get(
        reverse('events:list_events')
    )
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.data['results']) == 20  # default page size


@pytest.mark.django_db
def test_list_events(authorized_client, imported_events, test_file_remove):

    assert Event.objects.count() == 42

    # 2. test list

    resp = authorized_client.get(
        reverse('events:list_events')
    )
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.data['results']) == 20  # default page size


@pytest.mark.django_db
def test_list_events_single_filter(authorized_client, imported_events, test_file_remove):

    # 2nd file after the 1st (with other columns)

    resp = authorized_client.post(
        reverse('importer:import_file'),
        {
            'data_type': 'event',
            'file': get_test_excel_file()[1]
        },
        format='multipart'
    )

    assert resp.status_code == status.HTTP_200_OK
    assert Event.objects.count() == 84

    # 2. test list filtered

    resp = authorized_client.get(
        reverse('events:list_events'),
        {
            'field_obuchenie': 'да'
        }
    )
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.data['results']) == 20
    assert resp.data['count'] == 26


@pytest.mark.django_db
def test_list_events_pagination(authorized_client, imported_events, test_file_remove):

    # 2. test retrieval

    resp = authorized_client.get(
        reverse('events:list_events'),
        {
            'page_size': 15,
            'page': 1
        }
    )
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.data['results']) == 15
    assert resp.data['count'] == 42
    assert resp.data['next'] == 2
    assert resp.data['previous'] is None
    first = resp.data

    resp = authorized_client.get(
        reverse('events:list_events'),
        {
            'page_size': 15,
            'page': 2
        }
    )
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.data['results']) == 15
    assert resp.data['count'] == 42
    assert resp.data['next'] == 3
    assert resp.data['previous'] == 1
    assert first != resp.data

    resp = authorized_client.get(
        reverse('events:list_events'),
        {
            'page_size': 15,
            'page': 3
        }
    )
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.data['results']) == 12
    assert resp.data['count'] == 42
    assert resp.data['next'] is None
    assert resp.data['previous'] == 2


@pytest.mark.django_db
def test_list_events_multi_filter(authorized_client, imported_events, test_file_remove):

    assert Event.objects.count() == 42

    # 2nd file after the 1st (with other columns)

    resp = authorized_client.post(
        reverse('importer:import_file'),
        {
            'data_type': 'event',
            'file': get_test_excel_file()[1]
        },
        format='multipart'
    )

    assert resp.status_code == status.HTTP_200_OK
    assert Event.objects.count() == 84

    # 2. test list filtered

    resp = authorized_client.get(
        reverse('events:list_events'),
        {
            'field_source_filename': 'events_test_mini_2.xlsx',
            'field_bjudzhet': '500',
        }
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data['count'] == 4
    assert len(resp.data['results']) == 4


@pytest.mark.django_db
def test_list_events_multi_filter_pagination(authorized_client, imported_events, test_file_remove):

    assert Event.objects.count() == 42

    # 2nd file after the 1st (with other columns)

    resp = authorized_client.post(
        reverse('importer:import_file'),
        {
            'data_type': 'event',
            'file': get_test_excel_file()[1]
        },
        format='multipart'
    )

    assert resp.status_code == status.HTTP_200_OK
    assert Event.objects.count() == 84

    # 2. test retrieval

    resp = authorized_client.get(
        reverse('events:list_events'),
        {
            'field_source_filename': 'events_test_mini_2.xlsx',
            'page_size': 15,
            'page': 1
        }
    )
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.data['results']) == 15
    assert resp.data['count'] == 42
    assert resp.data['next'] == 2
    assert resp.data['previous'] is None
    first = resp.data

    resp = authorized_client.get(
        reverse('events:list_events'),
        {
            'field_source_filename': 'events_test_mini_2.xlsx',
            'page_size': 15,
            'page': 2
        }
    )
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.data['results']) == 15
    assert resp.data['count'] == 42
    assert resp.data['next'] == 3
    assert resp.data['previous'] == 1
    assert first != resp.data

    resp = authorized_client.get(
        reverse('events:list_events'),
        {
            'field_source_filename': 'events_test_mini_2.xlsx',
            'page_size': 15,
            'page': 3
        }
    )
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.data['results']) == 12
    assert resp.data['count'] == 42
    assert resp.data['next'] is None
    assert resp.data['previous'] == 2


@pytest.mark.django_db
def test_list_events_search(authorized_client, imported_events, test_file_remove):

    # 2nd file after the 1st (with other columns)

    resp = authorized_client.post(
        reverse('importer:import_file'),
        {
            'data_type': 'event',
            'file': get_test_excel_file()[1]
        },
        format='multipart'
    )

    assert resp.status_code == status.HTTP_200_OK
    assert Event.objects.count() == 84

    # 2. test list filtered

    resp = authorized_client.get(
        reverse('events:list_events'),
        {
            'search': 'да'
        }
    )
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.data['results']) == 20
    assert resp.data['count'] == 26


@pytest.mark.django_db
def test_list_events_search_2(authorized_client, imported_events, test_file_remove):

    assert Event.objects.count() == 42

    # 2. test list filtered

    resp = authorized_client.get(
        reverse('events:list_events'),
        {
            'search': '1500'
        }
    )
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.data['results']) == 2
    assert resp.data['count'] == 2

    # 2. 500 twice in one line: 7 found in 6 lines

    resp = authorized_client.get(
        reverse('events:list_events'),
        {
            'search': '500'
        }
    )
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.data['results']) == 6
    assert resp.data['count'] == 7  # TODO: bug


@pytest.mark.django_db
def test_update_event(authorized_client, imported_events, test_file_remove):

    event = Event.objects.first()
    assert event.eav.primechanie == 'коробка для Евгения Горелова'

    resp = authorized_client.patch(
        reverse('events:update_event', args=(event.pk,)),
        {
            'fields': {
                'primechanie': 'new'
            }
        },
        format='json'
    )

    event2 = Event.objects.get(pk=event.pk)
    assert event.eav.primechanie == 'new'


@pytest.mark.django_db
def test_export_events(authorized_client, imported_events, test_file_remove):

    assert Event.objects.count() == 42

    # 2. test retrieval

    resp = authorized_client.get(
        reverse('events:export_events'),
        {
            'field_source_filename': 'events_test_mini.xlsx',
        }
    )
    assert resp.status_code == status.HTTP_200_OK
