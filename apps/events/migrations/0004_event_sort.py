# Generated by Django 4.0.8 on 2022-11-18 13:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0003_event_created_at_event_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='sort',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
