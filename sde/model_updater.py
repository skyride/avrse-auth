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
    def update_model(self, Model, table_name):
        print("Updating %s...   " % Model.__name__, end="")
        sys.stdout.flush()

        table_map = getattr(maps, Model.__name__)

        # Get query
        query = self.query_from_map(table_name, table_map)

        # Iterate query results
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        for result in results:
            # Get the database object
            try:
                obj = Model.objects.get(pk=result[0])
            except Model.DoesNotExist:
                obj = Model()

            # Iterate table map, setting attributes
            for i, attr in enumerate(map(lambda x: x[0], table_map)):
                setattr(obj, attr, result[i])

            obj.save()

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
