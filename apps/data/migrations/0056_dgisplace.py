# Generated by Django 4.0.8 on 2023-03-01 14:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0055_rename_cityrecord_city'),
    ]

    operations = [
        migrations.CreateModel(
            name='DGisPlace',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', models.CharField(max_length=256, verbose_name='Регион')),
                ('region', models.CharField(max_length=256, verbose_name='Регион')),
                ('city', models.CharField(max_length=256, verbose_name='Город')),
                ('district', models.CharField(blank=True, max_length=256, null=True, verbose_name='Район')),
                ('street', models.CharField(blank=True, max_length=2048, null=True, verbose_name='Улица')),
                ('street_num', models.CharField(blank=True, max_length=2048, null=True, verbose_name='Нумерация улицы')),
                ('clat', models.FloatField(blank=True, null=True, verbose_name='Широта')),
                ('clong', models.FloatField(blank=True, null=True, verbose_name='Долгота')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Локация 2ГИС',
                'verbose_name_plural': 'Локации 2ГИС',
            },
        ),
    ]
