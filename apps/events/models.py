import eav
from django.db import models
from django.utils.translation import gettext_lazy as _


class Event(models.Model):

    # historical records - with who changed

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:

        verbose_name = _('Акция')
        verbose_name_plural = _('Акции')

    def __str__(self):
        return f'Акция #{self.pk}'


eav.register(Event)
