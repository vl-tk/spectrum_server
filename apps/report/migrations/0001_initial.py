# Generated by Django 4.0.8 on 2023-03-01 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ABCGTINRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gtin', models.CharField(max_length=16, verbose_name='GTIN')),
                ('product_name', models.CharField(max_length=1024)),
                ('retail_sales', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('total_sales', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('retail_sales_share', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('acc_retail_sales_share', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('region', models.CharField(blank=True, max_length=512, null=True, verbose_name='Регион')),
                ('group', models.CharField(max_length=16, verbose_name='Группа')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Запись Отчета: ABC-анализ розничные продажи по регионам',
                'verbose_name_plural': 'Записи Отчета: ABC-анализ розничные продажи по регионам',
                'unique_together': {('gtin', 'region')},
            },
        ),
    ]
