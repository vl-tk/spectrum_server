from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class CHZRecord(models.Model):
    # 2022-05-15,3811470644,"ООО ""ААА""",7806292496,04660105982173,Альтернативная табачная продукция,"Табак для кальяна, DRUNK CHERRY, 40 гр, SPECTRUM TOBACCO","ООО ""СПЕКТРУМ ТБК""",0,0,7,7,0,0

    date = models.DateField()

    inn = models.CharField('ИНН', max_length=50)

    owner_name = models.CharField(max_length=255)

    prid = models.CharField(max_length=255)

    gt = models.CharField(max_length=255)

    pg_name = models.CharField(max_length=255)

    product_name = models.CharField(max_length=255)

    producer_name = models.CharField(max_length=255)

    mrp = models.PositiveIntegerField()

    in_russia = models.PositiveIntegerField()

    out_total = models.PositiveIntegerField()

    out_whosale = models.PositiveIntegerField()

    out_retail = models.PositiveIntegerField()

    out_recycle = models.PositiveIntegerField()

    class Meta:
        verbose_name = 'Запись ЧЗ'
        verbose_name_plural = 'Записи ЧЗ'

    def __str__(self):
        return f'#{self.pk} - "{self.owner_name}" - {self.inn}'
