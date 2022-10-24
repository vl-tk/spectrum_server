from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords


class CHZRecord(models.Model):
    # 2022-05-15,3811470644,"ООО ""ААА""",7806292496,04660105982173,Альтернативная табачная продукция,"Табак для кальяна, DRUNK CHERRY, 40 гр, SPECTRUM TOBACCO","ООО ""СПЕКТРУМ ТБК""",0,0,7,7,0,0

    date = models.DateField()

    inn = models.CharField('ИНН', max_length=50)

    owner_name = models.CharField(max_length=255)

    prid = models.CharField(max_length=255)

    gt = models.CharField(max_length=255)

    pg_name = models.CharField(max_length=255)

    product_name = models.CharField(max_length=255)

    producer_name = models.CharField(max_length=255)

    mrp = models.PositiveIntegerField()

    in_russia = models.PositiveIntegerField()

    out_total = models.PositiveIntegerField()

    out_whosale = models.PositiveIntegerField()

    out_retail = models.PositiveIntegerField()

    out_recycle = models.PositiveIntegerField()

    is_edited_manually = models.BooleanField('Редактировано', default=False)

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Запись ЧЗ'
        verbose_name_plural = 'Записи ЧЗ'

    def __str__(self):
        return f'#{self.pk} - "{self.owner_name}" - {self.inn}'


class DGisRecord(models.Model):
    """
    Наименование организации    Бренд  Юридическое название Организационно-правовая форма      Юридическое название филиала       Организационно-правовая форма филиала     Расширение    Дополнение к расширению     Подразделение Расширение подразделения    Проект Публикации    Единица территориального деления   Улица  Адрес  Этажность     Назначение здания    Код телефонной зоны  Телефоны      Адреса электронной почты    Web-Алиас     Веб сайты     Skype  Icq    ВКонтакте     Twitter       Facebook      Instagram     LinkedIn      Pinterest     YouTube       GooglePlus    Одноклассники WhatsApp      Viber  Telegram      Графики работы       Рубрики       ИНН/ОГРН
    Бристоль, магазин у дома, ООО Альбион-2002       Бристоль      Альбион-2002  ООО                  магазин у дома                            Пенза  Пенза г. (Пенза городской округ, Пензенская обл., Россия)      Антонова      9      9      Жилой дом     (8412)Пенза г. (Пенза городской округ, Пензенская обл., Россия),Заречный г. (ЗАТО Заречный городской округ, Пензенская обл., Россия) 8007071555 [Обработан, Действующий, Контакт организации] 235645 [В архиве, Скрытый, Контакт не принадлежит организации]                     bristol.ru [Обработан, Действующий, Контакт организации]                     bristol_retail [Обработан, Действующий, Контакт организации]   magazinybristol [Обработан, Действующий, Контакт организации]  retail-1617203448558323 [Обработан, Действующий, Контакт организации] bristol_retail [Обработан, Действующий, Контакт организации] magaziny_bristol [В архиве, Скрытый, Контакт больше не функционирует, Контакт временно не функционирует, Контакт организации]                               group/54037646999782 [Обработан, Действующий, Контакт организации]    79108951221 [Обработан, Действующий, Контакт организации]      79108951221 [Обработан, Действующий, Контакт организации]             Пн-Вс 8:00-23:00     Алкогольные напитки Безалкогольные напитки Табачные изделия / Товары для курения Магазины разливного пива Снэковая продукция  5257056036/1025202393677
    """

    name = models.TextField('Наименование организации')

    brand = models.CharField('Бренд', max_length=2048)

    # not in table
    inn = ArrayField(
        models.PositiveBigIntegerField(),
        verbose_name='ИНН',
        null=True,
        blank=True
    )

    legal_name = models.CharField('Юр. название', max_length=2048)

    org_form = models.CharField('ОПФ', max_length=2048)

    branch_legal_name = models.CharField('Юр. название филиала', max_length=2048)

    branch_org_name = models.CharField('ОПФ филиала', max_length=2048)

    extension = models.CharField('Расширение', max_length=2048)

    extension_addition = models.CharField('Дополнение к расширению', max_length=2048)

    division = models.CharField('Подразделение', max_length=2048)

    division_extension = models.CharField('Расширение подразделения', max_length=2048)

    project_publications = models.CharField('Проект', max_length=2048)

    unit = models.CharField('Единица территориального деления', max_length=2048)
    street = models.CharField('Улица', max_length=2048)
    address = models.CharField('Адрес', max_length=2048)
    number_of_floors = models.CharField('Этажность', max_length=2048)
    building_purpose = models.CharField('Назначение здания', max_length=2048)

    phone_area_code = models.TextField('Код телефонной зоны')
    phones = models.TextField('Телефоны')
    emails = models.TextField('Адреса электронной почты')

    web_alias = models.TextField('Web-Алиас')
    web_sites = models.TextField('Веб сайты')

    soc_skype = models.CharField('Skype', max_length=2048)
    soc_icq = models.CharField('Icq', max_length=2048)
    soc_vk = models.TextField('ВКонтакте')
    soc_twitter = models.TextField('Twitter')
    soc_facebook = models.TextField('Facebook')
    soc_instagram = models.TextField('Instagram')
    soc_linkedin = models.TextField('LinkedIn')
    soc_pinterest = models.TextField('Pinterest')
    soc_youtube = models.TextField('YouTube')
    soc_google_plus = models.TextField('GooglePlus')
    soc_odnoklassniki = models.TextField('Одноклассники')
    soc_whatsapp = models.TextField('WhatsApp')
    soc_viber = models.TextField('Viber')
    soc_telegram = models.TextField('Telegram')
    soc_work_time = models.TextField('Графики работы')

    categories = models.TextField('Рубрики')

    inn_ogrn = models.TextField('ИНН/ОГРН')

    # not in table

    is_edited_manually = models.BooleanField('Редактировано', default=False)

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Запись 2Гис'
        verbose_name_plural = 'Записи 2Гис'

        # only 32 fields are suppported but we need all fields to 100% check if line is unique
        # constraints = [
        #     models.UniqueConstraint(fields=[
        #         'name',
        #         'brand',
        #         'legal_name',
        #         'org_form',
        #         'branch_legal_name',
        #         'branch_org_name',
        #         'extension',
        #         'extension_addition',
        #         'division',
        #         'division_extension',
        #         'project_publications',
        #         'unit',
        #         'street',
        #         'address',
        #         'number_of_floors',
        #         'building_purpose',
        #         'phone_area_code',
        #         'phones',
        #         'emails',
        #         'web_alias',
        #         'web_sites',
        #         'soc_skype',
        #         'soc_icq',
        #         'soc_vk',
        #         'soc_twitter',
        #         'soc_facebook',
        #         'soc_instagram',
        #         'soc_linkedin',
        #         'soc_pinterest',
        #         'soc_youtube',
        #         'soc_google_plus',
        #         'soc_odnoklassniki',
        #         'soc_whatsapp',
        #         'soc_viber',
        #         'soc_telegram',
        #         'soc_work_time',
        #         'categories',
        #         'inn_ogrn'
        #     ], name='unique_imported_fields')
        # ]

    def __str__(self):
        return f'#{self.pk} - "{self.name}"'
