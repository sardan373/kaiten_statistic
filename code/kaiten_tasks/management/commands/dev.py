from django.core.management.base import BaseCommand

from kaiten_tasks.models import KaitenUser
from kaiten_tasks.workers.api import ApiClient

from requests.compat import json as complexjson


class Command(BaseCommand):
    def handle(self, *args, **options):
        client = ApiClient()
        print(client.users())
