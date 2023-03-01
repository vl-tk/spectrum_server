def get_region_codes_by_short_name():

    REGION_CODES = {}

    with open('data_files/regions_01032023.csv') as f:
        lines = [l.strip() for l in f.readlines()]

        for l in lines[1:]:
            items = l.split(',')
            REGION_CODES[l[0]] = l[2]

    return REGION_CODES
