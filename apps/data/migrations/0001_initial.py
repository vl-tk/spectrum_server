# Generated by Django 4.1.2 on 2022-10-21 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CHZRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('inn', models.CharField(max_length=50, verbose_name='ИНН')),
                ('owner_name', models.CharField(max_length=255)),
                ('prid', models.PositiveIntegerField()),
                ('gt', models.PositiveIntegerField()),
                ('pg_name', models.CharField(max_length=255)),
                ('product_name', models.CharField(max_length=255)),
                ('producer_name', models.CharField(max_length=255)),
                ('mrp', models.PositiveIntegerField()),
                ('in_russia', models.PositiveIntegerField()),
                ('out_total', models.PositiveIntegerField()),
                ('out_whosale', models.PositiveIntegerField()),
                ('out_retail', models.PositiveIntegerField()),
                ('out_recycle', models.PositiveIntegerField()),
            ],
            options={
                'verbose_name': 'Запись ЧЗ',
                'verbose_name_plural': 'Записи ЧЗ',
            },
        ),
    ]
