""""
Product object from UPC Database.

Properties:
product_name : name of the product (string)
expiration_time : the amount of days a product remains good after purchase (int)

"""


class Product(object):
    def __init__(self, importing=True, **kwargs):
        if importing:
            json_object = kwargs.get('json_object')

            # TODO 1: Implement some way to handle objects which are not in the database?
            self.product_name = json_object["title"]
            self.expiration_time = json_object["description"]["expiration_time"]
        else:
            self.product_name = kwargs.get('product_name', "")
            self.expiration_time = kwargs.get('expiration_time', 0)
