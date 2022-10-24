from django.apps import AppConfig


class DataConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.data'

    def ready(self):
        import apps.data.signals
