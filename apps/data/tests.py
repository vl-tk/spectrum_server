import pytest
from apps.users.models import Region
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

# @pytest.mark.django_db
# def test_list_clients(unauthorized_client, clients):
#     resp = unauthorized_client.get(reverse('client:list_clients'))
#     assert resp.status_code == status.HTTP_200_OK
#     assert len(resp.data) == 10


# @pytest.mark.django_db
# def test_retrieve_clients(unauthorized_client, clients):
#     resp = unauthorized_client.get(reverse('client:retrieve_client', kwargs={'pk': clients[0].pk}))
#     assert resp.status_code == status.HTTP_200_OK


# @pytest.mark.django_db
# def test_filter_list_clients(unauthorized_client, clients):

#     resp = unauthorized_client.get(
#         reverse('client:list_clients'),
#         {
#             'region': Region.region_15
#         }
#     )
#     assert resp.status_code == status.HTTP_200_OK
#     assert len(resp.data) == 3
