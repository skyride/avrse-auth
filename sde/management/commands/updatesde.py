from django.core.management.base import BaseCommand

from django.db import connections

from sde.models import *
from sde.model_updater import ModelUpdater


class Command(BaseCommand):
    help = "Imports the SDE from fuzzworks sqlite database to our main database"

    def handle(self, *args, **options):
        # Get cursor for sde db
        with connections['sde'].cursor() as cursor:
            updater = ModelUpdater(cursor)
            updater.update_model(MarketGroup, "invMarketGroups")
            updater.update_model(Category, "invCategories")
            updater.update_model(Group, "invGroups")
            updater.update_model(Type, "invTypes")
            updater.update_model(AttributeCategory, "dgmAttributeCategories")
            updater.update_model(AttributeType, "dgmAttributeTypes")
            updater.update_model(TypeAttribute, "dgmTypeAttributes", no_key=True)
            updater.update_model(Region, "mapRegions")
            updater.update_model(Constellation, "mapConstellations")
            updater.update_model(System, "mapSolarSystems")
            updater.update_model(Station, "staStations")
