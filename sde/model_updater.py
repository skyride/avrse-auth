from __future__ import print_function
import sys

from django.db import transaction

from sde import maps

# Defines some functions for importing


# Updates a model from the SDE
class ModelUpdater:
    def __init__(self, cursor):
        self.cursor = cursor

    @transaction.atomic
    def update_model(self, Model, table_name, no_key=False):
        print("Updating %s...   " % Model.__name__, end="")
        sys.stdout.flush()

        table_map = getattr(maps, Model.__name__)

        # Get query
        query = self.query_from_map(table_name, table_map)

        # Delete all existing results if we have no key
        if no_key:
            Model.objects.all().delete()

        # Iterate query results
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        bulk = []
        for result in results:
            # Get the database object if it's not a keyless table
            if no_key:
                obj = Model()
                create = True
            else:
                try:
                    obj = Model.objects.get(pk=result[0])
                    create = False
                except Model.DoesNotExist:
                    obj = Model()
                    create = True

            # Iterate table map, setting attributes
            for i, attr in enumerate(map(lambda x: x[0], table_map)):
                setattr(obj, attr, result[i])

            if create:
                bulk.append(obj)
            else:
                obj.save()

        if len(bulk) > 0:
            Model.objects.bulk_create(bulk)

        print("%s objects" % len(results))


    # Generates SQL select query from a map
    def query_from_map(self, table_name, table_map):
        cols = ", ".join(
            map(
                lambda x: "`" + x[1] + "`",
                table_map
            )
        )

        sql = "SELECT %s FROM %s" % (
            cols,
            table_name
        )

        return sql
