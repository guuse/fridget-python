from .product import Product


class Products:

    def __init__(self):
        self.products = []

    def add_product(self, product: Product):
        self.products.append(product)

    def to_json(self):
        # TODO: Box ID
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

        for product in self.items:

            if product.product_category == category:
                filtered_products.append(product)

        return filtered_products

    def delete_item(self, id: int):
        for item in self.products:
            if id == item.product_id:
                self.products.pop(self.products.index(item))