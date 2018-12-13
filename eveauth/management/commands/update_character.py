import os

from django.core.management.base import BaseCommand

from eveauth.tasks import update_character


class Command(BaseCommand):
    help = "Update a characters details"

    def add_arguments(self, parser):
        parser.add_argument('char_id', type=int)

    def handle(self, *args, **options):
        update_character(options['char_id'])