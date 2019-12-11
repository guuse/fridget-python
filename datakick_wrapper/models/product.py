""""
Product object from Datakick Database.

Properties:
product_name : name of the product (string)
expiration_time : the amount of days a product remains good after purchase (int)

"""
import json


class Product(object):
    def __init__(self, json_object):
        self.product_name = json_object["name"]
        ingredients_dict = json.loads(json_object["ingredients"])
        self.expiration_time = ingredients_dict["expiration_time"]
        self.category = ingredients_dict["category"]
        self.desc = ingredients_dict.get("description", None)
        self.amount = ingredients_dict["amount"]
        self.unit = ingredients_dict.get("unit", None)

