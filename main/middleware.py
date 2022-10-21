import pytz
from django.utils import timezone
from django.utils.timezone import get_default_timezone


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
    #     # TODO для дальнейшего расширения, необходимо будет определять тайм зону пользователя
    #     tzname = get_default_timezone()
    #     if tzname:
    #         timezone.activate(pytz.timezone(tzname.zone))
    #     else:
    #         timezone.deactivate()
        return self.get_response(request)
