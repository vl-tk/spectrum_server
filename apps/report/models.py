from django.db import models


class ABCGTINRecord(models.Model):

    gtin = models.CharField('GTIN', max_length=16)

    product_name = models.CharField(max_length=1024, null=False, blank=False)

    retail_sales = models.PositiveSmallIntegerField(null=True, blank=True)

    total_sales = models.PositiveSmallIntegerField(null=True, blank=True)

    retail_sales_share = models.PositiveSmallIntegerField(null=True, blank=True)

    acc_retail_sales_share = models.PositiveSmallIntegerField(null=True, blank=True)

    region = models.CharField('Регион', max_length=512, null=True, blank=True)

    group = models.CharField('Группа', max_length=16)

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        verbose_name = 'Запись Отчета: ABC-анализ розничные продажи по регионам'
        verbose_name_plural = 'Записи Отчета: ABC-анализ розничные продажи по регионам'

        unique_together = ("gtin", "region")

    def __str__(self):
        return f'#{self.pk} - "{self.region}" - {self.gtin} - {self.group}'
