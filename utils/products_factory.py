from platform_wrapper.models.product import Product
from platform_wrapper.models.products import Products


def create_products_from_json(json):

    products = Products()

    json_objects = json.load(json)

    for product_json_object in json_objects:

        product_object = Product(
            product_name=product_json_object['name'],
            product_desc=product_json_object['description'],
            product_exp=product_json_object['expiresIn'],
            product_amount=product_json_object['amount'],
            product_amount_unit=product_json_object['unit']
        )

        products.add_product(product_object)

    return products