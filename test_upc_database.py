import settings
from upc_database_wrapper.upc_database_wrapper import UpcDatabaseWrapper

wrapper = UpcDatabaseWrapper(api_key=settings.UPC_DATABASE_API_KEY)
x = wrapper.get_product("810012050821")
print(x.product_name)
