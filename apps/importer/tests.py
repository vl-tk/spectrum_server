import pytest
from apps.events.models import Event
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


def test_max_filter_test():
    from apps.importer.services_data import FilterMixin
    f = FilterMixin()

    entity_fields = {
        'inn1': {
            'slug': 'inn',
            'type': 'text',
            'name': 'ИНН',
            'id': 123
        },
        'inn2': {
            'slug': 'inn',
            'type': 'text',
            'name': 'ИНН',
            'id': 123
        },
        'inn3': {
            'slug': 'inn',
            'type': 'text',
            'name': 'ИНН',
            'id': 123
        },
        'inn4': {
            'slug': 'inn',
            'type': 'text',
            'name': 'ИНН',
            'id': 123
        },
        'inn5': {
            'slug': 'inn',
            'type': 'text',
            'name': 'ИНН',
            'id': 123
        }
    }

    setattr(f, 'entity_fields', entity_fields)

    query_params = {
        'field_inn1': 'test',
        'field_inn2': 'test',
        'field_inn3': 'test',
        'field_inn4': 'test',
        'field_inn5': 'test'
    }

    filter_params = f.get_filter(query_params)

    res = {
        'inn1': 'test',
        'inn2': 'test',
        'inn3': 'test'
    }

    assert filter_params == res
