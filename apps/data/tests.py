import pytest
from apps.data.models import DGisRecord


@pytest.mark.django_db
@pytest.mark.vcr()
def test_dgis_record_coords_on_save():

    dr = DGisRecord.objects.create(
        name = 'test',
        brand = 'test',
        legal_name = 'test',
        org_form = 'test',
        extension = 'test',
        project_publications = 'Калининград',
        unit = 'Калининград г. (Калининград городской округ, Калининградская обл., Россия)',
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

    assert record.clong is None
    assert record.clat is None

    assert record.dgis_place is not None
