class Product:
    def __init__(self,
                 product_name: str,
                 product_exp,
                 product_category: str = "Overig",
                 product_amount: int = 1,
                 product_desc: str = None,
                 product_amount_unit: str = None,
                 product_id: int = None):

        self.product_name = product_name
        self.product_desc = product_desc
        self.product_exp = product_exp
        self.product_category = product_category
        self.product_amount = product_amount
        self.product_amount_unit = product_amount_unit
        self.product_id = product_id

    def to_json(self):
        """"
        Function to convert a Product object to a dict which can be used as json payload

        returns Dict
        """
        #TODO: REMOVE DAYS
        serialized_dict = {
            'name': self.product_name,
            'desc': self.product_desc,
            'amount': self.product_amount,
            'expires': self.product_exp.__str__() + " days",
            'unit': self.product_amount_unit,
            'category': self.product_category
        }

        return serialized_dict
