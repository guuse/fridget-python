import json

import requests

from .models.product import Product
from . import upc_database_paths


class UpcDatabaseWrapper(object):

    host = "https://api.upcdatabase.org"
    api_key = None

    default_headers = {
        'cache-control': "no-cache",
    }

    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_api_key(self) -> str:
        return self.api_key

    def parse_response(self, response, object):
        if response.status_code != 200:
            # TODO 2: Implement what will happen if the API fails/does not find the product
            ...
        else:
            return object(json_object=response.json())

    def get_product(self, ean13_code: str) -> Product:
        product_path = upc_database_paths.PRODUCT_PATH.format(ean13_code, self.api_key)
        url = self.host + product_path
        response = requests.get(url)

        return self.parse_response(response, Product)

