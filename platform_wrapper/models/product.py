class Product(object):
    def __init__(self, product_name: str,
                 product_exp,
                 product_amount: int,
                 product_desc: str = None,
                 product_amount_unit: str = None):

        self.product_name = product_name
        self.product_desc = product_desc
        self.product_exp = product_exp
        self.product_amount = product_amount
        self.product_amount_unit = product_amount_unit

    def to_json(self):
        """"
        Function to convert a Product object to a dict which can be used as json payload

        returns Dict
        """
        serialized_dict = {'name': self.product_name,
                           'desc': self.product_desc,
                           'amount': self.product_amount,
                           'expires': self.product_exp.__str__(),
                           'unit': self.product_amount_unit
                           }

        return serialized_dict
