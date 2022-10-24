# Generated by Django 4.1.2 on 2022-10-24 13:48

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0019_alter_dgisrecord_inn'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dgisrecord',
            name='inn',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.PositiveSmallIntegerField(), blank=True, null=True, size=None, verbose_name='ИНН'),
        ),
    ]
