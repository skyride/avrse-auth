import os

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Downloads the SDE file from fuzzworks"

    def handle(self, *args, **options):
        # Fetch the SDE
        print "Clear existing SDE"
        os.system("rm sqlite-latest.sqlite*")

        print "Downloading SDE"
        os.system('wget https://www.fuzzwork.co.uk/dump/sqlite-latest.sqlite.bz2')

        print "Decompressing"
        os.system('bzip2 -d sqlite-latest.sqlite.bz2')
