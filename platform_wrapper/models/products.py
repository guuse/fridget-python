import json

from .product import Product


class Products(object):

    products = []

    def add_product(self, product: Product):
        self.products.append(product)

    def to_json(self):
        serialized_dict = {
            "box": 411
        }

        products_serialized_array = []

        for product in self.products:
            products_serialized_array.append(product.to_json())

        serialized_dict["products"] = products_serialized_array

        return serialized_dict

    def products_length(self):
        return len(self.products)

    def filter_category(self, category: str):

        filtered_products = []

        for product in self.products:

            if product.product_category == category:
                filtered_products.append(product)

        return filtered_products

