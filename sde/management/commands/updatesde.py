from django.core.management.base import BaseCommand

from django.db import connections

from sde import maps
from sde.models import *
from sde.model_updater import ModelUpdater


class Command(BaseCommand):
    help = "Imports the SDE from fuzzworks sqlite database to our main database"

    def handle(self, *args, **options):
        # Get cursor for sde db
        with connections['sde'].cursor() as cursor:
            updater = ModelUpdater(cursor)
            updater.update_model(Region, "mapRegions", maps.Region)
