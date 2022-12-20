import eav
from apps.users.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords


class Event(models.Model):

    EVENT_CONTENT_TYPE = 16

    sort = models.IntegerField(null=True, blank=True)

    importer_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    history = HistoricalRecords()

    class Meta:

        verbose_name = _('Акция')
        verbose_name_plural = _('Акции')

    def __str__(self):
        return f'Акция #{self.pk}'


eav.register(Event)
