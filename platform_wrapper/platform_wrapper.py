import requests

from . import platform_paths
from .models.products import Products


class PlatformWrapper(object):

    host = "https://fridget.chprojecten.nl/api"
    api_key = None

    default_headers = {
        'cache-control': "no-cache",
        'content-type': "application/json"
    }

    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_api_key(self) -> str:
        return self.api_key

    def parse_object_response(self, response, object):
        """"
        Function handles a response which returns an object
        """
        raise NotImplementedError()

    def parse_response(self, response) -> bool:
        """"
        Function handles a response which doesn't return a body
        """
        if response.status_code != 200 or response.status_code != 201:
            # TODO 3: Implement what will happen if the API fails/did not add
            ...
        else:
            print("added")
            return True

    def add_products(self, products: Products) -> bool:
        products_add_path = platform_paths.PRODUCTS_ADD_PATH
        url = self.host + products_add_path
        json_body = products.to_json()
        print(json_body)
        response = requests.post(url, json=json_body)
        print(response.content)

        return self.parse_response(response)

