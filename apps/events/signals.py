import logging

from apps.data.models import DGisRecord
from apps.data.services import OSMProvider
from apps.events.models import Event
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger('django')


@receiver(post_save, sender=Event)
def on_save(sender, instance, created, **kwargs):

    if created:

        attrs = instance.eav.get_all_attributes()

        ADDRESS_NAME = 'Адрес'
        DGIS_ID_NAME = 'ID точки'

        ADDRESS, DGIS_ID = None, None

        for attr in attrs:
            value = getattr(instance.eav, attr.slug)

            if DGIS_ID_NAME in attr.name:
                if value.strip().isdigit():
                    DGIS_ID = int(value)
                    break

            if ADDRESS_NAME in attr.name:
                if value.strip():
                    ADDRESS = value
                    break

        if ADDRESS is not None:

            # TODO: hack
            city = instance.eav.gorod.split(',')[0]

            clat, clong = OSMProvider().get_coords(address=f'{city} {ADDRESS}')

            # won't trigger signal
            Event.objects.filter(pk=instance.pk).update(
                clat=clat,
                clong=clong
            )
            print(instance)

        elif DGIS_ID is not None:

            try:
                dg = DGisRecord.objects.get(pk=DGIS_ID)
            except DGisRecord.DoesNotExist:
                pass
            else:

                if dg.clat is None or dg.clong is None:

                    clat, clong = OSMProvider().get_coords(
                        address=f'{dg.project_publications} {dg.street} {dg.address}'
                    )

                    dg.clat = clat
                    dg.clong = clong
                    dg.save()

                Event.objects.filter(pk=instance.pk).update(
                    clat=dg.clat,
                    clong=dg.clong
                )
                print(instance)
