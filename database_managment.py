from sqlite_handler import *

def add_columns(table:SQLHTable, columns:list):
  for column in columns:
    table.add_column(column)

def set_tables(database_instance:SQLHDatabase, tables:list):
    for table in tables:
        database_instance.add_table(table)


products_table = SQLHTable(name="products", row_id=True, row_id_name="product_id")
product_name_column = SQLHColumn(name="name", type="TEXT", constraint="NOT NULL")
product_description_column = SQLHColumn(name="description", type="TEXT", constraint="NOT NULL")
product_quantity_column = SQLHColumn(name="quantity", type="INTEGER", constraint="NOT NULL")
product_price_column = SQLHColumn(name="price", type="INTEGER", constraint="")
product_src_column = SQLHColumn(name="image", type="TEXT", constraint="")
product_table_columns = [product_name_column, product_description_column, product_quantity_column, product_price_column, product_src_column]
add_columns(products_table, product_table_columns)

users_table = SQLHTable(name="users", row_id=True, row_id_name="user_id")
users_first_name_column = SQLHColumn(name="first_name", type="TEXT", constraint="")
users_last_name_column = SQLHColumn(name="last_name", type="TEXT", constraint="")
users_email_column = SQLHColumn(name="email", type="TEXT", constraint="NOT NULL")
users_password_column = SQLHColumn(name = "password", type="TEXT", constraint="NOT NULL")
users_phone_column = SQLHColumn(name="phone_number", type="TEXT", constraint="")
users_table_columns = [users_first_name_column, users_last_name_column, users_email_column, users_password_column, users_phone_column]
add_columns(users_table, users_table_columns)

orders_table = SQLHTable(name="orders", row_id=True, row_id_name="order_id")
orders_user_id_column = SQLHColumn(name="user_id", type="INTEGER", constraint="NOT NULL", foreign_key=users_table)
orders_product_id_column = SQLHColumn(name="product_id", type="INTEGER", constraint="NOT NULL", foreign_key=products_table)
orders_product_quantity_column = SQLHColumn(name="quantity", type="TEXT", constraint="NOT NULL")
orders_table_columns = [orders_user_id_column, orders_product_id_column, orders_product_quantity_column]
add_columns(orders_table, orders_table_columns)

status_table = SQLHTable(name="status", row_id=True, row_id_name="status_id")
status_name_column = SQLHColumn(name="name", type="TEXT", constraint="")
status_table_columns = [status_name_column]
add_columns(status_table, status_table_columns)
main_dtbs_tables = [products_table, users_table, orders_table, status_table]
set_tables(main_dtbs, main_dtbs_tables)

if __name__ == "__main__":
  # products_table.add_record(["Jordans", "sneekers", 25, 109, "./items/jordans.png"])
  # products_table.add_record(["Shirt", "just a random shirt", 2, 14, "./items/temp_image.png"])


  # users_table.add_record(["John", "Doe", "john.doe@gmail.com", "johndoe1", "+520991"])
  # users_table.add_record(["Jane", "Doe", "jane.doe@gmail.com", "janedoe1", "+672114"])

  # status_table.add_record(["paid"])
  # status_table.add_record(["sent"])
  # status_table.add_record(["delivered"])

  # for table in main_dtbs_tables:
  #   print("+--------------------------+")
  #   print(f"name: {table.name}\n")
  #   print(f"columns: {",".join([column.name for column in table.get_columns()])}\n")
  #   print("records: ")
  #   for records in table.get_records(rows=True):
  #     for record in records:
  #       print(f"{record[1]} ")
  #   print("+--------------------------+")

  products = products_table.get_records(rows = True)
  for product in products:
    print(product)
  pass