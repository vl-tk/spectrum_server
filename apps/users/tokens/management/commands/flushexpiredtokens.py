from apps.users.tokens.models import OutstandingToken
from django.core.management.base import BaseCommand
from rest_framework_simplejwt.utils import aware_utcnow


class Command(BaseCommand):
    help = 'Flushes any expired tokens in the outstanding token list'

    def handle(self, *args, **kwargs):
        OutstandingToken.objects.filter(expires_at__lte=aware_utcnow()).delete()
