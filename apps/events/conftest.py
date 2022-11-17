import pytest
from django.urls import reverse
from utils.test import get_test_excel_file


@pytest.fixture
@pytest.mark.django_db
def imported_events(authorized_client):

    resp = authorized_client.post(
        reverse('importer:import_file'),
        {
            'data_type': 'event',
            'file': get_test_excel_file()[0]
        },
        format='multipart'
    )

    yield
