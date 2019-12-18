from platform_wrapper.models.product import Product
from platform_wrapper.models.products import Products


def create_products_from_json(json_array):
    """Converts a json response of Products to a Python object of Products

    :param json_array: a json array of products

    :returns: Products object
    """

    products = Products()

    for product_json_object in json_array:

        product_object = Product(
            product_name=product_json_object['name'],
            product_desc=product_json_object['description'],
            product_exp=product_json_object['expiresIn'],
            product_amount=product_json_object['amount'],
            product_amount_unit=product_json_object['unit'],
            product_category=product_json_object['category'],
            product_id=product_json_object['id']
        )

        products.add_product(product_object)

    return products
