from pathlib import Path

import pytest
from apps.users.models import User
from apps.users.tokens.serializers import TokenObtainPairSerializer
from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from utils.test import UserFactoryMixin, get_test_excel_file


@pytest.fixture
def user():
    return User.objects.create(
        email='cratemaking@overshave.edu',
        password='password'
    )


@pytest.fixture
@pytest.mark.django_db
def unauthorized_client(user):
    client = APIClient()
    return client


@pytest.fixture
@pytest.mark.django_db
def authorized_client(user):
    user = UserFactoryMixin().create_random_user()
    token = TokenObtainPairSerializer.get_token(user)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION='Bearer %s' % token.access_token)
    return client


@pytest.fixture()
def test_file_remove():
    yield None
    for file in Path(settings.PROJECT_DIR).joinpath('media_files').iterdir():
        if file.is_file():
            if '_test_' in file.name:
                file.unlink()


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
