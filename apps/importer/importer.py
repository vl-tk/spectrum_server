import difflib
import logging
import os
from pathlib import Path
from typing import List

import pandas as pd
from apps.events.models import Event
from eav.models import Attribute

logger = logging.getLogger('importer')


class ColumnMatcher:
    """
    Run before import
    """

    POSSIBLE_MATCH_VALUE = 0.75

    def __init__(self, new_columns: List[str]):
        self.new_columns = new_columns

    def find_possible_matches(self):

        recommendations = defaultdict()

        existing_columns = self.get_existing_columns()

        for new_column in self.new_columns:

            ratio = difflib.SequenceMatcher(
                None,
                new_column,
                existing_column
            ).quick_ratio()

            if ratio > POSSIBLE_MATCH_VALUE:

                recommendations[new_column].append(existing_column)

        return recommendations

    def get_existing_columns(self):
        # todo: get all attributes from EAV
        return []


Attribute.objects.create(slug='color', datatype=Attribute.TYPE_TEXT)

# Alternatively, assuming you're using default EntityManager:
Attribute.objects.create(slug='color', datatype=Attribute.TYPE_TEXT)
Event.objects.create(eav__color='red')
flower.eav.color = 'red'



class ExcelImporter:

    def __init__(self, filepath: Path):

        df = pd.read_excel(filepath)

        # rename columns
        # df.columns = KEYS

    def create_event_record(item: list):
        try:
            dg = Event.objects.get(
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
        except Event.DoesNotExist:
            try:
                dg = Event.objects.create()
            except Exception as e:
                logger.exception(e)
                for a, i in enumerate(item, start=1):
                    print(a, i)
            else:
                logger.info(f'{dg} CREATED')
        else:
            logger.info(f'{item[0]} exists')


def get_item_value(i):
    if str(i) == 'nan':
        return ''
    return str(i)


# 2. add left lines from dataframe into table
for num, item in enumerate(df.to_records()):
    item = [get_item_value(i) for i in item]
    create_record(item)
