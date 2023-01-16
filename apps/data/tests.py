import pytest
from apps.data.models import CHZRecord, CityRecord, DGisRecord
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase


@pytest.mark.django_db
def test_dgis_record_coords_on_save():

    dr = DGisRecord.objects.create(
        name = 'test',
        brand = 'test',
        legal_name = 'test',
        org_form = 'test',
        extension = 'test',
        project_publications = 'Калининград',
        unit = 'test',
        street = 'Генделя',
        address = '5',
        number_of_floors = 'test',
        building_purpose = 'test',
        phone_area_code = 'test',
        phones = 'test',
        emails = 'test',
        inn_ogrn = 'test'
    )

    record = DGisRecord.objects.get(pk=dr.pk)

    assert record.clong is not None
    assert record.clat is not None
