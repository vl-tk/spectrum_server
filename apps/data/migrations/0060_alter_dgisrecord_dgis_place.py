# Generated by Django 4.0.8 on 2023-03-01 15:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0059_dgisplace_subregion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dgisrecord',
            name='dgis_place',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='data.dgisplace'),
        ),
    ]
