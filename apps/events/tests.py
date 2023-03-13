import datetime

import pytest
from apps.events.models import Event
from django.urls import reverse
from rest_framework import status
from utils.test import get_test_excel_file


@pytest.mark.django_db
@pytest.mark.vcr()
def test_list_events(authorized_client, imported_events_5, test_file_remove):

    assert Event.objects.count() == 5

    resp = authorized_client.get(
        reverse('events:list_events')
    )
    assert resp.status_code == status.HTTP_200_OK


@pytest.mark.django_db
@pytest.mark.vcr()
def test_list_events_single_filter(authorized_client, imported_events_5, test_file_remove):

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
    assert Event.objects.count() == 20

    # 2. test list filtered

    resp = authorized_client.get(
        reverse('events:list_events'),
        {
            'field_obuchenie': 'да'
        }
    )
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.data['results']) == 18
    assert resp.data['count'] == 18


@pytest.mark.django_db
@pytest.mark.vcr()
def test_list_events_pagination(authorized_client, imported_events, test_file_remove):

    # 2. test retrieval

    resp = authorized_client.get(
        reverse('events:list_events'),
        {
            'page_size': 7,
            'page': 1
        }
    )
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.data['results']) == 7
    assert resp.data['count'] == 15
    assert resp.data['next'] == 2
    assert resp.data['previous'] is None
    first = resp.data

    resp = authorized_client.get(
        reverse('events:list_events'),
        {
            'page_size': 7,
            'page': 2
        }
    )
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.data['results']) == 7
    assert resp.data['count'] == 15
    assert resp.data['next'] == 3
    assert resp.data['previous'] == 1
    assert first != resp.data

    resp = authorized_client.get(
        reverse('events:list_events'),
        {
            'page_size': 7,
            'page': 3
        }
    )
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.data['results']) == 1
    assert resp.data['count'] == 15
    assert resp.data['next'] is None
    assert resp.data['previous'] == 2


@pytest.mark.django_db
@pytest.mark.vcr()
def test_list_events_multi_filter(authorized_client, imported_events, test_file_remove):

    assert Event.objects.count() == 15

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
    assert Event.objects.count() == 30

    # 2. test list filtered

    resp = authorized_client.get(
        reverse('events:list_events'),
        {
            'field_source_filename': 'events_test_mini_15_2_version.xlsx',
            'field_bjudzhet': '500',
        }
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data['count'] == 4
    assert len(resp.data['results']) == 4


@pytest.mark.django_db
@pytest.mark.vcr()
def test_list_events_filter_same_field_for_checkbox(authorized_client, imported_events, test_file_remove):

    assert Event.objects.count() == 15

    resp = authorized_client.get(
        reverse('events:list_events'),
        {
            'field_source_filename': 'events_test_mini_15.xlsx',
            'field_bjudzhet': '500||1100'
        }
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data['count'] == 7
    assert len(resp.data['results']) == 7


@pytest.mark.django_db
@pytest.mark.vcr()
def test_list_events_filter_datetime(authorized_client, imported_events, test_file_remove):

    assert Event.objects.count() == 15

    resp = authorized_client.get(
        reverse('events:list_events'),
        {
            'field_source_filename': 'events_test_mini_15.xlsx',
            'field_data_nachala': '2022-01-04',
        }
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data['count'] == 1
    assert len(resp.data['results']) == 1

    resp = authorized_client.get(
        reverse('events:list_events'),
        {
            'field_source_filename': 'events_test_mini_15.xlsx',
            'field_data_nachala__gt': '2022-01-04',
            'field_data_okonchanija__lte': '2022-02-14'
        }
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data['count'] == 10
    assert len(resp.data['results']) == 10


@pytest.mark.django_db
@pytest.mark.vcr()
def test_list_events_multi_filter_pagination(authorized_client, imported_events, test_file_remove):

    assert Event.objects.count() == 15

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
    assert Event.objects.count() == 30

    # 2. test retrieval

    resp = authorized_client.get(
        reverse('events:list_events'),
        {
            'field_source_filename': 'events_test_mini_15_2_version.xlsx',
            'page_size': 14,
            'page': 1
        }
    )
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.data['results']) == 14
    assert resp.data['count'] == 15
    assert resp.data['next'] == 2
    assert resp.data['previous'] is None
    first = resp.data

    resp = authorized_client.get(
        reverse('events:list_events'),
        {
            'field_source_filename': 'events_test_mini_15_2_version.xlsx',
            'page_size': 14,
            'page': 2
        }
    )
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.data['results']) == 1
    assert resp.data['count'] == 15
    assert resp.data['next'] == None
    assert resp.data['previous'] == 1
    assert first != resp.data


@pytest.mark.django_db
@pytest.mark.vcr()
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
    assert Event.objects.count() == 30

    # 2. test list filtered

    resp = authorized_client.get(
        reverse('events:list_events'),
        {
            'search': 'да'
        }
    )
    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.data['results']) == 13
    assert resp.data['count'] == 26


@pytest.mark.django_db
@pytest.mark.vcr()
def test_list_events_search_2(authorized_client, imported_events, test_file_remove):

    assert Event.objects.count() == 15

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
    assert resp.data['count'] == 6


@pytest.mark.django_db
@pytest.mark.vcr()
def test_update_event(authorized_client, imported_events, test_file_remove):

    event = Event.objects.first()
    assert event.eav.primechanie == 'коробка для Аркадия Горелова'

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
    assert event2.eav.primechanie == 'new'


@pytest.mark.django_db
@pytest.mark.vcr()
def test_export_events(authorized_client, imported_events, test_file_remove):

    assert Event.objects.count() == 15

    # 2. test retrieval

    resp = authorized_client.get(
        reverse('events:export_events'),
        {
            'field_source_filename': 'events_test_mini_15.xlsx',
        }
    )
    assert resp.status_code == status.HTTP_200_OK


# graphs endpoints

@pytest.mark.django_db
@pytest.mark.vcr()
def test_graph(authorized_client, imported_events_5, test_file_remove):

    resp = authorized_client.get(
        reverse('events:event_region_graph'),
        {
        }
    )
    assert resp.status_code == status.HTTP_200_OK


@pytest.mark.django_db
@pytest.mark.vcr()
def test_get_coords_in_map_graph(authorized_client, imported_events_5, test_file_remove):

    resp = authorized_client.get(
        reverse('events:event_map_graph'),
        {
        }
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data['results'][0]['fields']['clat'] is not None
    assert resp.data['results'][0]['fields']['clong'] is not None


@pytest.mark.django_db
@pytest.mark.vcr()
def test_import_force_insert(authorized_client, imported_events_5, test_file_remove):

    assert Event.objects.count() == 5

    for e in Event.objects.all():
        assert e.eav.source_filename == 'events_test_mini_5.xlsx'

    resp = authorized_client.post(
        reverse('importer:import_file'),
        {
            'data_type': 'event',
            'file': get_test_excel_file()[2]
        },
        format='multipart'
    )

    assert resp.status_code == status.HTTP_400_BAD_REQUEST

    resp = authorized_client.post(
        reverse('importer:import_file'),
        {
            'data_type': 'event',
            'file': get_test_excel_file()[2],
            'force_rewrite': 'Y'
        },
        format='multipart'
    )

    assert resp.status_code == status.HTTP_200_OK
    assert Event.objects.count() == 5

    for e in Event.objects.all():
        assert e.eav.source_filename == 'events_test_mini_5.xlsx'


@pytest.mark.django_db
@pytest.mark.vcr()
def test_filter_events(authorized_client, imported_events_5, test_file_remove):

    resp = authorized_client.get(
        reverse('events:filter_events'),
        {
        }
    )
    assert resp.status_code == status.HTTP_200_OK

    assert resp.data == [
        {
            'slug': 'period',
            'name': 'Период',
            'values': [
                'Январь'
            ]
        },
        {
            'slug': 'gorod',
            'name': 'Город',
            'values': [
                'Калининград',
                'Москва',
                'Самара, Тольятти',
                'Санкт-Петербург',
                'Саратов'
            ]
        },
        {
            'slug': 'strana',
            'name': 'Страна',
            'values': [
                'Россия'
            ]
        },
        {
            'slug': 'postavschik',
            'name': 'Поставщик',
            'values': [
                'ДЮС'
            ]
        },
        {
            'slug': 'adresid_tochki',
            'name': 'Адрес/ID точки',
            'values': ['152984', 'ул Генделя 5', 'ул Пионерская 35']
        },
        {
            'slug': 'data_nachala',
            'name': 'Дата начала',
            'values': [
                datetime.datetime(2022, 1, 1, 0, 0),
                datetime.datetime(2022, 1, 2, 0, 0),
                datetime.datetime(2022, 1, 3, 0, 0),
                datetime.datetime(2022, 1, 4, 0, 0)
            ]
        },
        {
            'slug': 'data_okonchanija',
            'name': 'Дата окончания',
            'values': [
                datetime.datetime(2022, 2, 1, 0, 0),
                datetime.datetime(2022, 2, 2, 0, 0),
                datetime.datetime(2022, 2, 3, 0, 0),
                datetime.datetime(2022, 2, 4, 0, 0)
            ]
        },
        {
            'slug': 'tip_meroprijatija',
            'name': 'Тип мероприятия',
            'values': []
        },
        {
            'slug': 'nazvanie_meroprijatija',
            'name': 'Название мероприятия',
            'values': []
        },
        {
            'slug': 'obuchenie',
            'name': 'Обучение',
            'values': ['да']
        },
        {
            'slug': 'mehanika',
            'name': 'Механика',
            'values': [
                'Акция на прирост 5 призовых мест. Первое место - 8000, 2 место - 6000, 3 - 4000, 4 - 3000, 5 — 2000'
            ]
        },
        {
            'slug': 'chto_otpravljaem',
            'name': 'Что отправляем',
            'values': [
                'Значки 350 шт, мундштуки 150 шт, сумка поясная 20 шт, панама 10 шт, щипцы 10 шт'
            ]
        },
        {
            'slug': 'data_dobavlenija_k_zakazu',
            'name': 'Дата добавления к заказу',
            'values': [
                datetime.datetime(2022, 1, 15, 0, 0)
            ]
        },
        {
            'slug': 'sposob_otpravki',
            'name': 'Способ отправки',
            'values': []
        },
        {
            'slug': 'opisanie',
            'name': 'Описание',
            'values': []
        },
        {
            'slug': 'bjudzhet',
            'name': 'Бюджет',
            'values': ['100']
        },
        {
            'slug': 'primechanie',
            'name': 'Примечание',
            'values': ['коробка для Аркадия Горелова']
        },
        {
            'slug': 'kol_vo_vzaimodejstvujuschih',
            'name': 'Кол-во взаимодействующих',
            'values': ['1', '2', '3', '4']
        },
        {
            'slug': 'source_filename',
            'name': 'Файл импорта',
            'values': [
                'events_test_mini_5.xlsx'
            ]
        },
        {
            'slug': 'status',
            'name': 'Статус',
            'values': []
        }
    ]

    resp = authorized_client.get(
        reverse('events:filter_events'),
        {
            'field_adresid_tochki': '152984'
        }
    )
    assert resp.status_code == status.HTTP_200_OK

    cities_limited = {'slug': 'gorod', 'name': 'Город', 'values': ['Москва', 'Санкт-Петербург', 'Саратов']}

    assert cities_limited in resp.data


@pytest.mark.django_db
@pytest.mark.vcr()
def test_import_more_columns(authorized_client, imported_events_5, test_file_remove):

    assert Event.objects.count() == 5

    resp = authorized_client.post(
        reverse('importer:import_file'),
        {
            'data_type': 'event',
            'file': get_test_excel_file()[3],
        },
        format='multipart'
    )

    assert Event.objects.count() == 10

    resp = authorized_client.get(
        reverse('events:list_events')
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data['results'][0]['fields']['new_column'] is None
    assert resp.data['results'][-1]['fields']['new_column'] == '5'


@pytest.mark.django_db
@pytest.mark.vcr()
def test_import_less_columns(authorized_client, imported_events_5, test_file_remove):

    assert Event.objects.count() == 5

    resp = authorized_client.post(
        reverse('importer:import_file'),
        {
            'data_type': 'event',
            'file': get_test_excel_file()[4],
        },
        format='multipart'
    )

    assert Event.objects.count() == 10

    resp = authorized_client.get(
        reverse('events:list_events')
    )
    assert resp.status_code == status.HTTP_200_OK
    assert [resp.data['results'][0]['fields'][k] for k in resp.data['results'][0]['fields'].keys() if k in ['aaa', 'bbb', 'ccc']] == [None, None, None]
    assert [resp.data['results'][-1]['fields'][k] for k in resp.data['results'][-1]['fields'].keys() if k in ['aaa', 'bbb', 'ccc', 'status']] != [None, None, None]


@pytest.mark.django_db
@pytest.mark.vcr()
def test_suggestions_for_fields(authorized_client, imported_events_5, test_file_remove):

    assert Event.objects.count() == 5

    resp = authorized_client.get(
        reverse('events:events_suggestions'),
        {
            'field': 'some field'
        }
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST

    resp = authorized_client.get(
        reverse('events:events_suggestions'),
        {
            'field': 'gorod'
        }
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data == ['Калининград', 'Москва', 'Самара, Тольятти', 'Санкт-Петербург', 'Саратов']

    resp = authorized_client.get(
        reverse('events:events_suggestions'),
        {
            'field': 'data_nachala'
        }
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data == [
        '01.01.2022',
        '02.01.2022',
        '03.01.2022',
        '04.01.2022',
    ]


@pytest.mark.django_db
@pytest.mark.vcr()
def test_typos(authorized_client, imported_events_5, test_file_remove):

    assert Event.objects.count() == 5

    resp = authorized_client.get(
        reverse('events:events_typos_columns'),
        {
            'columns': 'Период,Город,Страна,Поставщик,Адрес/ID точки,Дата начала,Дата окончания,Тип мероприятия,Название мероприятие,Обучение,Механика,Что отправляем,Дата добавления к заказу,Способ отправки,Описание,Бюджет,Примечание,Кол-во взаимодействующих,Файл импорта,Статус'
        }
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data['Название мероприятие'] == {
        'msg': 'Column NOT found in DB. Possible column found in DB',
        'column_name': 'Название мероприятия',
        'column_slug': 'nazvanie_meroprijatija'
    }


@pytest.mark.django_db
@pytest.mark.vcr()
def test_typos_cells(authorized_client, imported_events_5, test_file_remove):

    assert Event.objects.count() == 5

    resp = authorized_client.post(
        reverse('events:events_typos_cells'),
        {
            'file': get_test_excel_file()[5]
        },
        format='multipart'
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data == {
        'Страна': {
            'value': 'Россия', 'ratio': 0.91, 'orig_value': 'Росси'
        },
        'Поставщик': {
            'value': 'ДЮС', 'ratio': 0.86, 'orig_value': 'ДЮСs'
        }
    }
