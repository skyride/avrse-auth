import ujson

from django.core.management.base import BaseCommand

from esi import swagger_json_file
from esi.models import Scope


class Command(BaseCommand):
    help = "Imports scopes from the swagger.json file and adds them to the database"

    def handle(self, *args, **options):
        swagger = ujson.load(open(swagger_json_file))

        # Add or update scopes as required
        for name, description in swagger['securityDefinitions']['evesso']['scopes'].iteritems():
            try:
                db_scope = Scope.objects.get(name=name)
            except Scope.DoesNotExist:
                db_scope = Scope()

            db_scope.name = name
            db_scope.description = description
            db_scope.save()
