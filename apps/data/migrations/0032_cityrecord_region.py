# Generated by Django 4.0.8 on 2023-01-12 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0031_cityrecord'),
    ]

    operations = [
        migrations.AddField(
            model_name='cityrecord',
            name='region',
            field=models.CharField(blank=True, max_length=512, null=True, verbose_name='Регион'),
        ),
    ]
