from ovp.apps.donations.backends.zoop import ZoopBackend
from django.core.management.base import BaseCommand
import json


class Command(BaseCommand):
    def handle(self, *args, **options):
        backend = ZoopBackend()
        print(json.dumps(backend.list_sellers()[1].json()))
