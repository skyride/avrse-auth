from bravado.client import SwaggerClient
from bravado.swagger_model import load_file
from bravado.requests_client import RequestsClient

from esi import swagger_json_file


def get_client(token=None):
    if token == None:
        return SwaggerClient.from_spec(
            load_file(swagger_json_file)
        )

    # Set up client
    http_client = RequestsClient()


    return SwaggerClient.from_spec(
        load_file(swagger_json_file),
        http_client=http_client
    )
