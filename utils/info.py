from pathlib import Path

from django.conf import settings


def get_region_codes_by_short_name():

    REGION_CODES = {}

    file = Path(settings.PROJECT_DIR) / 'data_files/regions_01032023.csv'

    with open(file) as f:
        lines = [l.strip() for l in f.readlines()]

        for l in lines[1:]:
            items = l.split(',')
            REGION_CODES[l[0]] = l[2]

    return REGION_CODES


def get_region_coords():

    REGION_CODES = {}

    file = Path(settings.PROJECT_DIR) / 'data_files/regions_01032023.csv'

    with open(file) as f:

        lines = [l.strip() for l in f.readlines()]

        for l in lines[1:]:
            items = l.split(',')

            coords = items[-1].replace('"', '')

            REGION_CODES[items[1]] = {
                "lat": coords.split(';')[0],
                "long": coords.split(';')[1]
            }

    return REGION_CODES
