# Generated by Django 4.1.2 on 2022-10-24 15:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0025_historicaldgisrecord_historicalchzrecord'),
    ]

    operations = [
        migrations.AddField(
            model_name='chzrecord',
            name='is_edited_manually',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='dgisrecord',
            name='is_edited_manually',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='historicalchzrecord',
            name='is_edited_manually',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='historicaldgisrecord',
            name='is_edited_manually',
            field=models.BooleanField(default=False),
        ),
    ]
