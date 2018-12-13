import os

from django.core.management.base import BaseCommand

from eveauth.tasks import update_kills


class Command(BaseCommand):
    help = "Update a characters kills"

    def add_arguments(self, parser):
        parser.add_argument('char_id', type=int)

    def handle(self, *args, **options):
        update_kills(options['char_id'])