# Generated by Django 4.1.2 on 2022-10-21 18:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0007_alter_dgisrecord_phone_area_code_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dgisrecord',
            name='categories',
            field=models.CharField(max_length=1024, verbose_name='Рубрики'),
        ),
        migrations.AlterField(
            model_name='dgisrecord',
            name='emails',
            field=models.CharField(max_length=1024, verbose_name='Адреса электронной почты'),
        ),
        migrations.AlterField(
            model_name='dgisrecord',
            name='inn_ogrn',
            field=models.CharField(max_length=1024, verbose_name='ИНН/ОГРН'),
        ),
        migrations.AlterField(
            model_name='dgisrecord',
            name='soc_facebook',
            field=models.CharField(max_length=1024, verbose_name='Facebook'),
        ),
        migrations.AlterField(
            model_name='dgisrecord',
            name='soc_google_plus',
            field=models.CharField(max_length=1024, verbose_name='GooglePlus'),
        ),
        migrations.AlterField(
            model_name='dgisrecord',
            name='soc_icq',
            field=models.CharField(max_length=1024, verbose_name='Icq'),
        ),
        migrations.AlterField(
            model_name='dgisrecord',
            name='soc_instagram',
            field=models.CharField(max_length=1024, verbose_name='Instagram'),
        ),
        migrations.AlterField(
            model_name='dgisrecord',
            name='soc_linkedin',
            field=models.CharField(max_length=1024, verbose_name='LinkedIn'),
        ),
        migrations.AlterField(
            model_name='dgisrecord',
            name='soc_odnoklassniki',
            field=models.CharField(max_length=1024, verbose_name='Одноклассники'),
        ),
        migrations.AlterField(
            model_name='dgisrecord',
            name='soc_pinterest',
            field=models.CharField(max_length=1024, verbose_name='Pinterest'),
        ),
        migrations.AlterField(
            model_name='dgisrecord',
            name='soc_skype',
            field=models.CharField(max_length=1024, verbose_name='Skype'),
        ),
        migrations.AlterField(
            model_name='dgisrecord',
            name='soc_telegram',
            field=models.CharField(max_length=1024, verbose_name='Telegram'),
        ),
        migrations.AlterField(
            model_name='dgisrecord',
            name='soc_twitter',
            field=models.CharField(max_length=1024, verbose_name='Twitter'),
        ),
        migrations.AlterField(
            model_name='dgisrecord',
            name='soc_viber',
            field=models.CharField(max_length=1024, verbose_name='Viber'),
        ),
        migrations.AlterField(
            model_name='dgisrecord',
            name='soc_vk',
            field=models.CharField(max_length=1024, verbose_name='ВКонтакте'),
        ),
        migrations.AlterField(
            model_name='dgisrecord',
            name='soc_whatsapp',
            field=models.CharField(max_length=1024, verbose_name='WhatsApp'),
        ),
        migrations.AlterField(
            model_name='dgisrecord',
            name='soc_work_time',
            field=models.CharField(max_length=1024, verbose_name='Графики работы'),
        ),
        migrations.AlterField(
            model_name='dgisrecord',
            name='soc_youtube',
            field=models.CharField(max_length=1024, verbose_name='YouTube'),
        ),
        migrations.AlterField(
            model_name='dgisrecord',
            name='web_alias',
            field=models.CharField(max_length=1024, verbose_name='Web-Алиас'),
        ),
        migrations.AlterField(
            model_name='dgisrecord',
            name='web_sites',
            field=models.CharField(max_length=1024, verbose_name='Веб сайты'),
        ),
    ]
