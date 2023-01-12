# Generated by Django 4.0.8 on 2023-01-12 08:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0030_alter_dgisrecord_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CityRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city', models.CharField(max_length=2048, verbose_name='Город')),
                ('clat', models.FloatField(blank=True, null=True, verbose_name='Широта')),
                ('clong', models.FloatField(blank=True, null=True, verbose_name='Долгота')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Город',
                'verbose_name_plural': 'Города',
            },
        ),
    ]
