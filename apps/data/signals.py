import logging
import re

from apps.data.models import CHZRecord, City, DGisPlace, DGisRecord
from apps.data.services import OSMProvider
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger('django')


def _clean(text:str) -> str:
    return text.replace('обл.', 'область').replace('респ.', '').replace(' город фед. значения', '')


def get_coordinates(country, city, instance):

    try:
        city = City.objects.get(city=city)
    except City.DoesNotExist:
        clat, clong = OSMProvider().get_coords(
            address=f'{country} {city}'
        )
    else:
        clat, clong = city.clat, city.clong

    return clat, clong


@receiver(post_save, sender=DGisRecord)
def dgis_save(sender, instance, created, **kwargs):

    inns = []
    for value in instance.inn_ogrn.split('/'):
        if len(value) == 12 and value.isdigit():
            try:
                inn = int(value)
            except ValueError as e:
                logger.exception(e)
            else:
                inns.append(inn)

    if instance.inn != inns:
        DGisRecord.objects.filter(pk=instance.pk).update(inn=inns)  # won't trigger signal
        print(instance)

    # DGisPlace
    # TODO: if values simply changed
    if created or instance.dgis_place is None:

        # EXAMPLE: "unit":
        # Октябрьский рп. (Люберцы городской округ, Московская обл., Россия)
        # Сальск г. (Сальский район, Ростовская обл., Россия)
        # Москва г. (Москва город фед. значения, Россия)

        try:
            city = instance.unit.split(' (')[0].strip().replace(' г.', '')
        except Exception as e:
            logger.error(instance.unit)
            logger.exception(e)
            city = ''

        try:
            country = instance.unit.split(', ')[-1].strip().replace(')', '')
        except Exception as e:
            logger.error(instance.unit)
            logger.exception(e)
            country = ''

        inside_text = instance.unit.split(' (')[1]

        region = ''
        if inside_text.count(', ') > 1:
            try:
                region = _clean(inside_text.split(', ')[1])
            except Exception as e:
                logger.error(instance.unit)
                logger.exception(e)
        elif inside_text.count(', ') == 1:
            try:
                region = _clean(inside_text.split(', ')[0])
            except Exception as e:
                logger.error(instance.unit)
                logger.exception(e)

        subregion = ''
        if inside_text.count(', ') > 1:
            try:
                subregion = instance.unit.split(', ')[-3].split('(')[1]
            except Exception as e:
                logger.error(instance.unit)
                logger.exception(e)

        clat, clong = get_coordinates(country, city, instance)

        dgis_place = DGisPlace.objects.create(
            country=country,
            region=region,
            city=city,
            subregion=subregion,
            district='',
            street=instance.street,
            street_num=instance.address,
            clat=clat,
            clong=clong
        )

        DGisRecord.objects.filter(pk=instance.pk).update(
            dgis_place=dgis_place
        )


@receiver(post_save, sender=CHZRecord)
def chz_save(sender, instance, created, **kwargs):

    if created or (instance.weight is None and instance.product_name is not None):

        weight = re.findall(r"\s(\d+)\sгр", instance.product_name)

        if weight:

            weight = weight[0]

            CHZRecord.objects.filter(pk=instance.pk).update(
                weight=weight
            )

    if created or (instance.position is None and instance.product_name is not None):

        position = instance.product_name.split(',')[1].strip()

        if position:

            CHZRecord.objects.filter(pk=instance.pk).update(
                position=position
            )
