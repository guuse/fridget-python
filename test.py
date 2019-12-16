import datetime

import keyboard

from datakick_wrapper.datakick_wrapper import DatakickWrapper
from platform_wrapper.models.product import Product
from platform_wrapper.models.products import Products
from platform_wrapper.platform_wrapper import PlatformWrapper
from utils.utils import is_valid_ean

datakick_api = DatakickWrapper()
platform_api = PlatformWrapper(api_key="")

x = ""

while True:
    while True:
        if keyboard.is_pressed('enter'):
            break

        x += keyboard.read_key()

    print(x)

    y = 1
    z = ""

    for i in range(0, len(x)):
        if i % 2 == 0:
            if not x[i].isalpha():
                z += x[i]

    print(is_valid_ean(z))



    print(z)

    datakick_product = datakick_api.get_product(z)

    z = ""
    x = ""

    product = Product(product_name=datakick_product.product_name,
                      product_desc=datakick_product.desc,
                      product_amount=datakick_product.amount,
                      product_amount_unit=datakick_product.unit,
                      product_exp=(datetime.datetime.now() + datetime.timedelta(datakick_product.expiration_time)).date())

    products = Products()
    products.add_product(product)
    print(products.products_length())

    if (products.products_length() > 3):
        platform_api.add_products(products)
        break