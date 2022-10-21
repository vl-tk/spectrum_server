import pytest
from apps.users.models import User
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
