from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


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

    name = models.CharField('Наименование организации', max_length=2048)

    brand = models.CharField('Бренд', max_length=2048)

    legal_name = models.CharField('Юридическое название', max_length=2048)

    org_form = models.CharField('Организационно-правовая форма', max_length=2048)

    branch_legal_name = models.CharField('Юридическое название филиала', max_length=2048)

    branch_org_name = models.CharField('Организационно-правовая форма филиала', max_length=2048)

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

    phone_area_code = models.CharField('Код телефонной зоны', max_length=2048)
    phones = models.CharField('Телефоны', max_length=2048)
    emails = models.CharField('Адреса электронной почты', max_length=2048)

    web_alias = models.CharField('Web-Алиас', max_length=2048)
    web_sites = models.CharField('Веб сайты', max_length=2048)

    soc_skype = models.CharField('Skype', max_length=2048)
    soc_icq = models.CharField('Icq', max_length=2048)
    soc_vk = models.CharField('ВКонтакте', max_length=2048)
    soc_twitter = models.CharField('Twitter', max_length=2048)
    soc_facebook = models.CharField('Facebook', max_length=2048)
    soc_instagram = models.CharField('Instagram', max_length=2048)
    soc_linkedin = models.CharField('LinkedIn', max_length=2048)
    soc_pinterest = models.CharField('Pinterest', max_length=2048)
    soc_youtube = models.CharField('YouTube', max_length=2048)
    soc_google_plus = models.CharField('GooglePlus', max_length=2048)
    soc_odnoklassniki = models.CharField('Одноклассники', max_length=2048)
    soc_whatsapp = models.CharField('WhatsApp', max_length=2048)
    soc_viber = models.CharField('Viber', max_length=2048)
    soc_telegram = models.CharField('Telegram', max_length=2048)
    soc_work_time = models.CharField('Графики работы', max_length=2048)

    categories = models.CharField('Рубрики', max_length=2048)

    inn_ogrn = models.CharField('ИНН/ОГРН', max_length=2048)

    # not in table
    inn = models.CharField('ИНН', max_length=255)

    class Meta:
        verbose_name = 'Запись 2Гис'
        verbose_name_plural = 'Записи 2Гис'

    def __str__(self):
        return f'#{self.pk} - "{self.name}"'
