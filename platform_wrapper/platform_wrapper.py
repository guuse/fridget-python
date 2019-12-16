import requests

from utils.products_factory import create_products_from_json
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

        if response.status_code != 200:
            if object is Products:

                return create_products_from_json(response.json())

        else:
            raise Exception(response.status_code)



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

    def get_products(self, box_id: int, category: str = None) -> Products:
        """Retrieves products from the fridge box

        :param box_id: The id of the box (int)
        :param category: A category (string, optional)

        :returns: List of all products inside the box
        """
        products_get_path = platform_paths.PRODUCTS_GET_PATH.format(box_id)
        url = self.host + products_get_path

        params = {
            'category': category
        }

        response = requests.get(
            url=url,
            params=params,
            headers=self.default_headers
        )

        # Raise Exceptions if they occur
        response.raise_for_status()

        return self.parse_object_response(response, Products)
