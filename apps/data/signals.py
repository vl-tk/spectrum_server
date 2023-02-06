import logging
import re

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.data.models import CHZRecord, DGisRecord
from apps.data.services import OSMProvider

logger = logging.getLogger('django')


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

    city = instance.unit.split('(')[0].replace('г.', '').strip()

    if created or (instance.clat is None or instance.clong is None):

            clat, clong = OSMProvider().get_coords(
                address=f'{city} {instance.street} {instance.address}'
            )

            DGisRecord.objects.filter(pk=instance.pk).update(
                clat=clat,
                clong=clong
            )

    if created or instance.city is None:

        DGisRecord.objects.filter(pk=instance.pk).update(
            city=city
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
