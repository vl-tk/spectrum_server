import pytest
from django.urls import reverse

from apps.users.models import Client, Region


@pytest.fixture
def clients():
    clients = []
    for i in range(7):
        clients.append(Client.objects.create(
            name=f'client_name{i}',
            region=Region.region_70
        ))
    for i in range(3):
        clients.append(Client.objects.create(
            name=f'client_name{i}',
            region=Region.region_15
        ))
    return clients
