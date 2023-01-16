import logging

from apps.data.models import DGisRecord
from apps.data.services import OSMProvider
from django.db.models.signals import post_save
from django.dispatch import receiver

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

    if created:

        if instance.clat is None or instance.clong is None:

            clat, clong = OSMProvider().get_coords(
                address=f'{instance.project_publications} {instance.street} {instance.address}'
            )

            DGisRecord.objects.filter(pk=instance.pk).update(
                clat=clat,
                clong=clong
            )
