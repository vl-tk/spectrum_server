# Generated by Django 4.0.8 on 2023-02-28 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0051_abcgtinrecord'),
    ]

    operations = [
        migrations.AddField(
            model_name='abcgtinrecord',
            name='acc_retail_sales_share',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='abcgtinrecord',
            name='retail_sales_share',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='abcgtinrecord',
            name='retail_sales',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
    ]
