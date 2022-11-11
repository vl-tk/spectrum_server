from pathlib import Path

import pytest
from apps.users.models import User
from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase


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
    client = APIClient()
    return client


@pytest.fixture()
def test_file_remove():
    yield None
    for file in Path(settings.PROJECT_DIR).joinpath('media_files').iterdir():
        if file.is_file():
            if '_test_' in file.name:
                file.unlink()
