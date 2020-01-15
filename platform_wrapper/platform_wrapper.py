from datetime import datetime, timedelta

import requests

from platform_wrapper.factories.products_factory import create_products_from_json
from . import platform_paths
from .factories.boxes_factory import create_boxes_from_json
from .models.boxes import Boxes
from .models.product import Product
from .models.products import Products


class PlatformWrapper(object):

    host = "https://fridget.chprojecten.nl/api"
    default_headers = {
        'cache-control': "no-cache",
        'content-type': "application/json"
    }

    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_api_key(self) -> str:
        return self.api_key

    @staticmethod
    def parse_object_response(response, object):

        if response.status_code == 200 or response.status_code == 201:
            if object is Products:
                return create_products_from_json(response.json())
            elif object is Product:
                product_data = response.json()

                return Product(
                    product_name=product_data['name'],
                    product_category=product_data['category'],
                    product_exp=product_data['expiresIn'],
                    product_amount_unit=product_data['unit'],
                    product_desc=product_data['description']
                )
            elif object is Boxes:
                return create_boxes_from_json(response.json())
            else:
                raise NotImplementedError()

        else:
            raise Exception(response.status_code)

    @staticmethod
    def parse_response(response) -> bool:
        """"
        Function handles a response which doesn't return a body
        """
        if response.status_code != 200 and response.status_code != 201 and response.status_code != 204:
            # TODO 3: Implement what will happen if the API fails/did not add
            raise NotImplementedError()
        else:
            return True

    def _get(self, url: str, object_type):
        response = requests.get(
            url=url,
            headers=self.default_headers
        )

        # Raise Exceptions if they occur
        response.raise_for_status()

        return self.parse_object_response(response, object_type)

    def _post(self, url: str, json_body, object_type=None):
        response = requests.post(
            url=url,
            headers=self.default_headers,
            json=json_body
        )

        response.raise_for_status()

        if object_type:
            return self.parse_object_response(response, object_type)
        return self.parse_response(response)

    def _put(self, url: str, json_body):
        response = requests.put(
            url=url,
            headers=self.default_headers,
            json=json_body
        )

        response.raise_for_status()

        return self.parse_response(response)

    def _delete(self, url: str):
        response = requests.delete(
            url=url,
            headers=self.default_headers
        )

        response.raise_for_status()

        return self.parse_response(response)

    def add_products(self, products: Products) -> Products:
        """Inserts a list of products into the database

        :param products: list of Products

        :returns: list of products currently in box
        """
        products_add_path = platform_paths.PRODUCTS_ADD_PATH
        url = self.host + products_add_path
        json_body = products.to_json()

        return self._post(url, json_body, Products)

    def get_products(self, box_id: int) -> Products:
        """Retrieves products from the fridge box

        :param box_id: The id of the box (int)

        :returns: List of all products inside the box
        """
        products_get_path = platform_paths.PRODUCTS_GET_PATH.format(box_id)
        url = self.host + products_get_path

        return self._get(url, Products)

    def get_product_from_ean(self, ean: str) -> Product:
        """Retrieves products from the GS1

        :param ean: ean of a product

        :returns: Returns the GS1 info about a product
        """
        get_product_from_ean_path = platform_paths.EAN_GET.format(ean)
        url = self.host + get_product_from_ean_path

        return self._get(url, Product)

    def get_user_boxes(self, user_id: str) -> Products:
        """Retrieves all boxes from a user

        :param user_id: The id of the user (str)

        :returns: List of all boxes an user has
        """
        products_get_path = platform_paths.BOXES_GET_PATH.format(user_id)
        url = self.host + products_get_path

        return self._get(url, Boxes)

    def delete_product(self, product_id: int):

        product_delete_path = platform_paths.PRODUCTS_DEL_PATH.format(product_id.__str__())
        url = self.host + product_delete_path

        return self._delete(url)

    def set_amount_product(self, product_id: int, amount: int):

        product_amount_put_path = platform_paths.PRODUCTS_PUT_PATH.format(product_id.__str__())
        url = self.host + product_amount_put_path

        return self._put(url, {"amount": amount})