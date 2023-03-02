from apps.data.models import CHZRecord, City, DGisPlace, DGisRecord


def get_region_code_for_city(city: str) -> str:
    from utils.info import get_region_codes_by_short_name
    try:
        c = City.objects.get(city=city)
    except City.DoesNotExist:
        return '-'

    REGION_CODES = get_region_codes_by_short_name()

    return REGION_CODES.get(c.region, '-')[0]


def get_regions():
    """
    TODO: use materialized view

    # old
    regions = list(DGisRecord.objects.all().values_list('project_publications', flat=True).distinct(
         ).order_by('project_publications'))
    """

    regions = DGisPlace.objects.values_list('country', 'region').order_by('country', 'region').distinct()

    return regions


def get_cities():

    cities = DGisPlace.objects.values_list('country', 'city').order_by('country', 'city').distinct()

    return cities


def get_products():

    prs = list(CHZRecord.objects.all().values_list('product_name', flat=True).distinct(
        ).order_by('product_name'))

    return prs


def get_positions():

    prs = list(CHZRecord.objects.all().values_list('position', flat=True).distinct(
        ).order_by('position'))

    return prs
