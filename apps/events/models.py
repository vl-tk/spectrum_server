import eav
from django.db import models
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords


class Event(models.Model):

    sort = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    history = HistoricalRecords()

    class Meta:

        verbose_name = _('Акция')
        verbose_name_plural = _('Акции')

    def __str__(self):
        return f'Акция #{self.pk}'


eav.register(Event)
