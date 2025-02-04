# Generated by Django 4.1.2 on 2022-10-21 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0004_alter_chzrecord_gt'),
    ]

    operations = [
        migrations.CreateModel(
            name='DGisRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Наименование организации')),
                ('brand', models.CharField(max_length=255, verbose_name='Бренд')),
                ('legal_name', models.CharField(max_length=255, verbose_name='Юридическое название')),
                ('org_form', models.CharField(max_length=255, verbose_name='Организационно-правовая форма')),
                ('branch_legal_name', models.CharField(max_length=255, verbose_name='Юридическое название филиала')),
                ('branch_org_name', models.CharField(max_length=255, verbose_name='Организационно-правовая форма филиала')),
                ('extension', models.CharField(max_length=255, verbose_name='Расширение')),
                ('extension_addition', models.CharField(max_length=255, verbose_name='Дополнение к расширению')),
                ('division', models.CharField(max_length=255, verbose_name='Подразделение')),
                ('division_extension', models.CharField(max_length=255, verbose_name='Расширение подразделения')),
                ('project', models.CharField(max_length=255, verbose_name='Проект')),
                ('publications', models.CharField(max_length=255, verbose_name='Публикации')),
                ('unit', models.CharField(max_length=255, verbose_name='Единица территориального деления')),
                ('street', models.CharField(max_length=255, verbose_name='Улица')),
                ('address', models.CharField(max_length=255, verbose_name='Адрес')),
                ('number_of_floors', models.CharField(max_length=255, verbose_name='Этажность')),
                ('building_purpose', models.CharField(max_length=255, verbose_name='Назначение здания')),
                ('phone_area_code', models.CharField(max_length=255, verbose_name='Код телефонной зоны')),
                ('phones', models.CharField(max_length=255, verbose_name='Телефоны')),
                ('emails', models.CharField(max_length=255, verbose_name='Адреса электронной почты')),
                ('web_alias', models.CharField(max_length=255, verbose_name='Web-Алиас')),
                ('web_sites', models.CharField(max_length=255, verbose_name='Веб сайты')),
                ('soc_skype', models.CharField(max_length=255, verbose_name='Skype')),
                ('soc_icq', models.CharField(max_length=255, verbose_name='Icq')),
                ('soc_vk', models.CharField(max_length=255, verbose_name='ВКонтакте')),
                ('soc_twitter', models.CharField(max_length=255, verbose_name='Twitter')),
                ('soc_facebook', models.CharField(max_length=255, verbose_name='Facebook')),
                ('soc_instagram', models.CharField(max_length=255, verbose_name='Instagram')),
                ('soc_linkedin', models.CharField(max_length=255, verbose_name='LinkedIn')),
                ('soc_pinterest', models.CharField(max_length=255, verbose_name='Pinterest')),
                ('soc_youtube', models.CharField(max_length=255, verbose_name='YouTube')),
                ('soc_google_plus', models.CharField(max_length=255, verbose_name='GooglePlus')),
                ('soc_odnoklassniki', models.CharField(max_length=255, verbose_name='Одноклассники')),
                ('soc_whatsapp', models.CharField(max_length=255, verbose_name='WhatsApp')),
                ('soc_viber', models.CharField(max_length=255, verbose_name='Viber')),
                ('soc_telegram', models.CharField(max_length=255, verbose_name='Telegram')),
                ('soc_work_time', models.CharField(max_length=255, verbose_name='Графики работы')),
                ('categories', models.CharField(max_length=255, verbose_name='Рубрики')),
                ('inn_ogrn', models.CharField(max_length=255, verbose_name='ИНН/ОГРН')),
                ('inn', models.CharField(max_length=255, verbose_name='ИНН')),
            ],
            options={
                'verbose_name': 'Запись 2Гис',
                'verbose_name_plural': 'Записи 2Гис',
            },
        ),
    ]
