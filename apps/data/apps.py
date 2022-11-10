from django.apps import AppConfig


class DataConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.data'
    verbose_name = 'Данные импортируемых баз'

    def ready(self):
        import apps.data.signals
