from apps.data.models import CHZRecord, City, DGisRecord


def get_region_code_for_city(city: str) -> str:
    from utils.info import REGION_CODES
    try:
        c = City.objects.get(city=city)
    except City.DoesNotExist:
        return '-'

    return REGION_CODES.get(c.region, '-')


def get_regions():
    """
    TODO: use materialized view
    """

    regions = list(DGisRecord.objects.all().values_list('project_publications', flat=True).distinct(
        ).order_by('project_publications'))

    return regions


def get_products():

    prs = list(CHZRecord.objects.all().values_list('product_name', flat=True).distinct(
        ).order_by('product_name'))

    return prs


def get_positions():

    prs = list(CHZRecord.objects.all().values_list('position', flat=True).distinct(
        ).order_by('position'))

    return prs
