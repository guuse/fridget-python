import settings
from datakick_wrapper.datakick_wrapper import DatakickWrapper

wrapper = DatakickWrapper()
x = wrapper.get_product("5000112544602")
print(x.product_name)
print(x.category)
