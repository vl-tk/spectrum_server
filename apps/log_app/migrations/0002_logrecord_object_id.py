# Generated by Django 4.0.8 on 2022-12-19 15:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('log_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='logrecord',
            name='object_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
