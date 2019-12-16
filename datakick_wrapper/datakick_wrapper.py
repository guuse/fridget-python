import requests

from .models.product import Product
from . import datakick_paths


class DatakickWrapper(object):

    host = datakick_paths.BASE_PATH
    api_key = None

    default_headers = {
        'cache-control': "no-cache",
        'Content-Type': "application/json",
    }

    def __init__(self, api_key: str = None):
        self.api_key = api_key

    def get_api_key(self) -> str:
        return self.api_key

    def parse_response_to_object(self, response, object):
        if response.status_code != 200:
            # TODO: Implement what will happen if the API fails/does not find the product
            ...
        else:
            return object(json_object=response.json())

    def get_product(self, ean13_code: str) -> Product:
        product_path = datakick_paths.PRODUCT_PATH.format(ean13_code)
        url = self.host + product_path
        response = requests.get(url)

        # Raise exception if one occurs
        response.raise_for_status()

        print(response.json())

        return self.parse_response_to_object(response, Product)

