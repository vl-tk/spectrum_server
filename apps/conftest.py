import os

import pytest
from apps.data.models import CHZRecord
from apps.users.models import User
from apps.users.tokens.serializers import TokenObtainPairSerializer
from django.conf import settings
from django.urls import reverse
from rest_framework.test import APIClient
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


@pytest.fixture
@pytest.mark.django_db
def imported_events_5(authorized_client):

    resp = authorized_client.post(
        reverse('importer:import_file'),
        {
            'data_type': 'event',
            'file': get_test_excel_file()[2]
        },
        format='multipart'
    )

    yield


@pytest.fixture
@pytest.mark.django_db
def chz_records_mini():

    records = '2022-05-15;3811470644;"ООО ""ААА""";7806292496;04660105982173;Альтернативная табачная продукция;"Табак для кальяна, DRUNK CHERRY, 40 гр, SPECTRUM TOBACCO";"ООО ""СПЕКТРУМ ТБК""";0;0;7;7;0;0\n' \
        '2022-05-15;1660327244;"ООО ""BBS""";7806292496;04660105982173;Альтернативная табачная продукция;"Табак для кальяна, DRUNK CHERRY, 40 гр, SPECTRUM TOBACCO";"ООО ""СПЕКТРУМ ТБК""";0;0;7;7;0;0\n' \
        '2022-05-15;550710307000;"ООО ""CCC""";7806292496;04660105982173;Альтернативная табачная продукция;"Табак для кальяна, DRUNK CHERRY, 40 гр, SPECTRUM TOBACCO";"ООО ""СПЕКТРУМ ТБК""";0;0;7;7;0;0\n' \
        '2021-12-03;2723213300;"ООО ""ДОКА ДВ""";7806292496;04660105983149;Альтернативная табачная продукция;"Табак для кальяна BASIL STRAWBERRY 100 гр, SPECTRUM TOBACCO";"ООО ""СПЕКТРУМ ТБК""";0;10;0;0;0;0\n' \
        '2021-12-03;2723213300;"ООО ""ДОКА ДВ""";7806292496;04660105980056;Альтернативная табачная продукция;"Табак для кальяна BLUE GUM HL 40 гр, SPECTRUM TOBACCO";"ООО ""СПЕКТРУМ ТБК""";0;25;0;0;0;0\n' \
        '2021-12-03;2723213300;"ООО ""ДОКА ДВ""";7806292496;04660105983026;Альтернативная табачная продукция;"Табак для кальяна BASIL STRAWBERRY 40 гр, SPECTRUM TOBACCO";"ООО ""СПЕКТРУМ ТБК""";0;25;0;0;0;0\n' \
        '2021-12-03;2723213300;"ООО ""ДОКА ДВ""";7806292496;04660105981817;Альтернативная табачная продукция;"Табак для кальяна BERGATEA 40 гр, SPECTRUM TOBACCO";"ООО ""СПЕКТРУМ ТБК""";0;25;0;0;0;0\n' \
        '2021-12-03;2723213300;"ООО ""ДОКА ДВ""";7806292496;04660105980322;Альтернативная табачная продукция;"Табак для кальяна COOKIES&MILK 40 гр, SPECTRUM TOBACCO";"ООО ""СПЕКТРУМ ТБК""";0;25;0;0;0;0\n' \
        '2021-12-03;2723213300;"ООО ""ДОКА ДВ""";7806292496;04603720851967;Альтернативная табачная продукция;"Табак для кальяна BLUE BERRY HL 100 гр, SPECTRUM TOBACCO";"ООО ""СПЕКТРУМ ТБК""";0;10;0;0;0;0\n' \
        '2021-12-03;2723213300;"ООО ""ДОКА ДВ""";7806292496;04660105981176;Альтернативная табачная продукция;"Табак для кальяна OBLEPIHA 100 гр, SPECTRUM TOBACCO";"ООО ""СПЕКТРУМ ТБК""";0;10;0;0;0;0\n' \
        '2021-12-03;2723213300;"ООО ""ДОКА ДВ""";7806292496;04660105980339;Альтернативная табачная продукция;"Табак для кальяна DEZZERT CHERRY 100 гр, SPECTRUM TOBACCO";"ООО ""СПЕКТРУМ ТБК""";0;10;0;0;0;0\n' \
        '2021-12-03;2723213300;"ООО ""ДОКА ДВ""";7806292496;04660105981053;Альтернативная табачная продукция;"Табак для кальяна LEMON HURRICANE HL 40 гр, SPECTRUM TOBACCO";"ООО ""СПЕКТРУМ ТБК""";0;50;0;0;0;0\n' \
        '2021-12-03;2723213300;"ООО ""ДОКА ДВ""";7806292496;04660105981763;Альтернативная табачная продукция;"Табак для кальяна RYE BREAD 40 гр, SPECTRUM TOBACCO";"ООО ""СПЕКТРУМ ТБК""";0;50;0;0;0;0\n' \
        '2021-12-03;2723213300;"ООО ""ДОКА ДВ""";7806292496;04660105983040;Альтернативная табачная продукция;"Табак для кальяна APPLE STRUDEL 40 гр, SPECTRUM TOBACCO";"ООО ""СПЕКТРУМ ТБК""";0;25;0;0;0;0\n' \
        '2021-12-03;2723213300;"ООО ""ДОКА ДВ""";7806292496;04603720851752;Альтернативная табачная продукция;"Табак для кальяна AGAVA CACTUS HL 100 гр, SPECTRUM TOBACCO";"ООО ""СПЕКТРУМ ТБК""";0;10;0;0;0;0\n' \
        '2021-12-03;2723213300;"ООО ""ДОКА ДВ""";7806292496;04660105983118;Альтернативная табачная продукция;"Табак для кальяна BASIL STRAWBERRY HL 40 гр, SPECTRUM TOBACCO";"ООО ""СПЕКТРУМ ТБК""";0;25;0;0;0;0\n' \
        '2021-12-03;9701128291;"ООО ""ДСМ""";7806292496;04660105980957;Альтернативная табачная продукция;"Табак для кальяна JUNGLE MIX HL 100 гр, SPECTRUM TOBACCO";"ООО ""СПЕКТРУМ ТБК""";0;10;0;0;0;0\n' \
        '2021-12-03;6234181240;"ООО ""ДЫМ""";7806292496;04660105981176;Альтернативная табачная продукция;"Табак для кальяна OBLEPIHA 100 гр, SPECTRUM TOBACCO";"ООО ""СПЕКТРУМ ТБК""";0;1;0;0;0;0\n' \
        '2021-12-03;6316268950;"ООО ""ДЮС""";7806292496;04660105983194;Альтернативная табачная продукция;"Табак для кальяна CHICKEN RAMEN 200 гр, SPECTRUM TOBACCO";"ООО ""СПЕКТРУМ ТБК""";0;12;0;0;0;0\n' \
        '2021-12-03;6316268950;"ООО ""ДЮС""";7806292496;04660105983200;Альтернативная табачная продукция;"Табак для кальяна CHICKEN RAMEN 40 гр, SPECTRUM TOBACCO";"ООО ""СПЕКТРУМ ТБК""";0;400;0;0;0;0\n' \
        '2021-12-03;5406809232;"ООО ""ЛАЙН-АП""";7806292496;04660105983200;Альтернативная табачная продукция;"Табак для кальяна CHICKEN RAMEN 40 гр, SPECTRUM TOBACCO";"ООО ""СПЕКТРУМ ТБК""";0;350;0;0;0;0\n' \
        '2021-12-03;7806536030;"ООО ""НАША СЕТЬ СПБ""";7806292496;04660105980711;Альтернативная табачная продукция;"Табак для кальяна GRAPE SODA 40 гр, SPECTRUM TOBACCO";"ООО ""СПЕКТРУМ ТБК""";0;2;0;0;0;0\n' \
        '2021-12-03;7017218618;"ООО ""Проект""";7806292496;04660105983163;Альтернативная табачная продукция;"Табак для кальяна TROPIC GUM 40 гр, SPECTRUM TOBACCO";"ООО ""СПЕКТРУМ ТБК""";0;2;0;0;0;0\n' \
        '2021-12-03;7017218618;"ООО ""Проект""";7806292496;04660105983156;Альтернативная табачная продукция;"Табак для кальяна PUMPKIN CHEESE 40 гр, SPECTRUM TOBACCO";"ООО ""СПЕКТРУМ ТБК""";0;2;0;0;0;0\n' \
        '2021-12-03;9710020488;"ООО ""СИРИУС""";7806292496;04660105980698;Альтернативная табачная продукция;"Табак для кальяна GRAPE SODA 100 гр, SPECTRUM TOBACCO";"ООО ""СПЕКТРУМ ТБК""";0;1;0;0;0;0\n' \
        '2021-12-03;7202235008;"ООО ""Султан""";7806292496;04660105983095;Альтернативная табачная продукция;"Табак для кальяна DUCHESS HL 200 гр, SPECTRUM TOBACCO";"ООО ""СПЕКТРУМ ТБК""";0;1;0;0;0;0\n' \
        '2021-12-03;7202235008;"ООО ""Султан""";7806292496;04660105982524;Альтернативная табачная продукция;"Табак для кальяна RUSSIAN RASPBERRY HL 200 гр, SPECTRUM TOBACCO";"ООО ""СПЕКТРУМ ТБК""";0;1;0;0;0;0\n' \
        '2021-12-03;7202235008;"ООО ""Султан""";7806292496;04660105982418;Альтернативная табачная продукция;"Табак для кальяна GRAPE SODA HL 200 гр, SPECTRUM TOBACCO";"ООО ""СПЕКТРУМ ТБК""";0;1;0;0;0;0\n' \
        '2021-12-03;4345427922;"ООО ""ТК ""ФОРАС""";7806292496;04660105980650;Альтернативная табачная продукция;"Табак для кальяна GRANNY APPLE 40 гр, SPECTRUM TOBACCO";"ООО ""СПЕКТРУМ ТБК""";0;2;0;0;0;0'

    for rec in records.split('\n'):
        values = rec.split(';')

        c = CHZRecord(
            date=values[0],
            owner_name=values[2],
            inn=int(values[1]),
            gt=int(values[3]),
            pg_name=values[4],
            product_name=values[5],
            producer_name=values[6],
            prid=values[7],
            mrp=int(values[8]),
            in_russia=int(values[9]),
            out_total=int(values[10]),
            out_whosale=int(values[11]),
            out_retail=int(values[12]),
            out_recycle=int(values[13])
        )
        c.save()


@pytest.fixture(scope='module')
def vcr_cassette_dir(request):
    return os.path.join(settings.PROJECT_DIR, 'cassettes')
