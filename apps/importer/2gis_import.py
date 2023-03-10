import os

import pandas as pd

os.environ.setdefault('DJANGO_SETTINGS_MODULE',
 'main.settings.local')  # isort:skip

import django   # isort:skip
django.setup()
from apps.data.models import DGisRecord   # isort:skip



KEYS = [
    'name',
    'brand',
    'legal_name',
    'org_form',
    'branch_legal_name',
    'branch_org_name',
    'extension',
    'extension_addition',
    'division',
    'division_extension',
    'project_publications',
    'unit',
    'street',
    'address',
    'number_of_floors',
    'building_purpose',
    'phone_area_code',
    'phones',
    'emails',
    'web_alias',
    'web_sites',
    'soc_skype',
    'soc_icq',
    'soc_vk',
    'soc_twitter',
    'soc_facebook',
    'soc_instagram',
    'soc_linkedin',
    'soc_pinterest',
    'soc_youtube',
    'soc_google_plus',
    'soc_odnoklassniki',
    'soc_whatsapp',
    'soc_viber',
    'soc_telegram',
    'soc_work_time',
    'categories',
    'inn_ogrn'
]

df = pd.read_excel('2gis.xlsx')

df.columns = KEYS


def create_dgis_record(item: list):
    try:
        dg = DGisRecord.objects.get(
            # [0,
            # 'Табакерка, сеть магазинов',
            name=item[1],
            # 'Табакерка',
            brand=item[2],
            # nan,
            legal_name=item[3],
            # nan,
            org_form=item[4],
            # nan,
            branch_legal_name=item[5],
            # nan,
            branch_org_name=item[6],
            # 'сеть магазинов',
            extension=item[7],
            # nan,
            extension_addition=item[8],
            # nan,
            division=item[9],
            # nan,
            division_extension=item[10],
            # 'Одесса',
            project_publications=item[11],
            # 'Одесса г. (Одесский район, Одесская обл., Украина)'
            unit=item[12],
            # , 'Люстдорфская дорога'
            # , '55з',
            street=item[13],
            # 4.0,
            address=item[14],
            # 'Административное здание',
            number_of_floors=item[15],
            # nan,
            building_purpose=item[16],
            # '952794733 [Обработан, Действующий, Контакт организации] [Олег]',
            phone_area_code=item[17],
            # nan,
            phones=item[18],
            # nan,
            emails=item[19],
            # 'www.fortunacigars.com.ua [Обработан, Действующий, Контакт организации]',
            web_alias=item[20],
            # nan,
            web_sites=item[21],
            # nan,
            soc_skype=item[22],
            # nan,
            soc_icq=item[23],
            # nan,
            soc_vk=item[24],
            soc_twitter=item[25],
            soc_facebook=item[26],
            soc_instagram=item[27],
            soc_linkedin=item[28],
            soc_pinterest=item[29],
            soc_youtube=item[30],
            soc_google_plus=item[31],
            soc_odnoklassniki=item[32],
            soc_whatsapp=item[33],
            soc_viber=item[34],
            soc_telegram=item[35],
            soc_work_time=item[36],
            categories=item[37],
            inn_ogrn=item[38]
        )
    except DGisRecord.DoesNotExist:
        try:
            dg = DGisRecord.objects.create(
                # [0,
                # 'Табакерка, сеть магазинов',
                name=item[1],
                # 'Табакерка',
                brand=item[2],
                # nan,
                legal_name=item[3],
                # nan,
                org_form=item[4],
                # nan,
                branch_legal_name=item[5],
                # nan,
                branch_org_name=item[6],
                # 'сеть магазинов',
                extension=item[7],
                # nan,
                extension_addition=item[8],
                # nan,
                division=item[9],
                # nan,
                division_extension=item[10],
                # 'Одесса',
                project_publications=item[11],
                # 'Одесса г. (Одесский район, Одесская обл., Украина)'
                unit=item[12],
                # , 'Люстдорфская дорога'
                # , '55з',
                street=item[13],
                # 4.0,
                address=item[14],
                # 'Административное здание',
                number_of_floors=item[15],
                # nan,
                building_purpose=item[16],
                # '952794733 [Обработан, Действующий, Контакт организации] [Олег]',
                phone_area_code=item[17],
                # nan,
                phones=item[18],
                # nan,
                emails=item[19],
                # 'www.fortunacigars.com.ua [Обработан, Действующий, Контакт организации]',
                web_alias=item[20],
                # nan,
                web_sites=item[21],
                # nan,
                soc_skype=item[22],
                # nan,
                soc_icq=item[23],
                # nan,
                soc_vk=item[24],
                soc_twitter=item[25],
                soc_facebook=item[26],
                soc_instagram=item[27],
                soc_linkedin=item[28],
                soc_pinterest=item[29],
                soc_youtube=item[30],
                soc_google_plus=item[31],
                soc_odnoklassniki=item[32],
                soc_whatsapp=item[33],
                soc_viber=item[34],
                soc_telegram=item[35],
                soc_work_time=item[36],
                categories=item[37],
                inn_ogrn=item[38]
            )
        except Exception as e:
            for a, i in enumerate(item, start=1):
                print(a, i)
            print('ERROR:', e)
            # import pdb; pdb.set_trace()
        else:
            print(f'{dg} CREATED')
    else:
        print(f'{item[0]} exists')


def get_item_value(i):
    if str(i) == 'nan':
        return ''
    return str(i)


# 2. add left lines from dataframe into table
for num, item in enumerate(df.to_records()):
    item = [get_item_value(i) for i in item]
    create_dgis_record(item)
