# Generated by Django 4.0.8 on 2023-03-01 15:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0057_dgisrecord_dgis_place_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dgisplace',
            name='country',
            field=models.CharField(max_length=256, verbose_name='Страна'),
        ),
    ]
