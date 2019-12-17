from datetime import datetime, timedelta

import requests

from utils.products_factory import create_products_from_json
from . import platform_paths
from .models.product import Product
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

        print(response.status_code)

        if response.status_code == 200:
            if object is Products:
                return create_products_from_json(response.json())
            if object is Product:
                product_data = response.json()
                return Product(
                    product_name=product_data['name'],
                    product_category=product_data['category'],
                    product_exp=(datetime.now() + timedelta(product_data['expiresIn'])).date(),
                    product_amount_unit=product_data['unit'],
                    product_desc=product_data['description']
                )

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

    def get_boxes(self, user_id: str):
        raise NotImplementedError()

    def get_products(self, box_id: int) -> Products:
        """Retrieves products from the fridge box

        :param box_id: The id of the box (int)

        :returns: List of all products inside the box
        """
        products_get_path = platform_paths.PRODUCTS_GET_PATH.format(box_id)
        url = self.host + products_get_path


        response = requests.get(
            url=url,
            headers=self.default_headers
        )

        # Raise Exceptions if they occur
        response.raise_for_status()

        return self.parse_object_response(response, Products)

    def get_product_from_ean(self, ean: str) -> Product:
        """Retrieves products from the GS1

        :param ean: ean of a product

        :returns: Returns the GS1 info about a product
        """
        get_product_from_ean_path = platform_paths.EAN_GET.format(ean)
        url = self.host + get_product_from_ean_path

        response = requests.get(
            url=url,
            headers=self.default_headers
        )

        print(response.content)

        # Raise Exceptions if they occur
        response.raise_for_status()

        return self.parse_object_response(response, Product)

    def get_user_boxes(self, box_id: int) -> Products:
        """Retrieves products from the fridge box

        :param box_id: The id of the box (int)

        :returns: List of all products inside the box
        """
        products_get_path = platform_paths.PRODUCTS_GET_PATH.format(box_id)
        url = self.host + products_get_path


        response = requests.get(
            url=url,
            headers=self.default_headers
        )

        # Raise Exceptions if they occur
        response.raise_for_status()

        return self.parse_object_response(response, Products)