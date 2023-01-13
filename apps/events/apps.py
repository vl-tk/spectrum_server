from django.apps import AppConfig


class EventsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.events'
    verbose_name = 'Акции'

    def ready(self):
        import apps.events.signals
