# by Copper(Milishenko) <3


from __future__ import annotations
from sqlite3 import *
from sqlite3 import Error, Connection
from os import *
count = 0

def object_check(func):
  def wrapper(*args, **kwargs):
    result = func(*args, **kwargs)
    return result
  return wrapper

class SQLHandler(object):
  def __init__(self, file_name:str = 'data.db'):
    self.connection = self.create_connection(file_name)

  def create_connection(self, file_name:str):
    connection = None
    try:
        connection = connect(file_name)
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        return connection
    except Error as e:
        print(f"Error: {e}")

  def execute_query(self, query):
    global count
    count += 1
    print()
    print('query number', count)
    print(query)
    print()
    cursor = self.connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        self.connection.commit()
        return result
    except Error as e:
        print(f"Error: {e}")
  
class SQLHDatabase(SQLHandler):
  def __init__(self, name:str = 'data.db'):
    super().__init__(name)
    self.tables = list()
    self.tables_dict = list()
    self.file_tables = super().execute_query("SELECT name FROM sqlite_master WHERE type='table';")
        
  def delete_record_table(self, table, id):
    if self.find_table(table):
      query_template = f"DELETE FROM {table.name} WHERE {table.primary_key.name} like {id};"
      super().execute_query(query_template)

  def add_table(self, table:SQLHTable):
    self.tables.append(table)
    table.set_database(self)
    
    if not (f'{table.name}',) in self.file_tables:
      query_template = f"CREATE TABLE IF NOT EXISTS {table.name}("
      columns = table.get_columns()
      columns_template_strings = list()
      temp_str = list()
      foreign_keys_list = list()
      for column in columns:
        temp_str.append(f"{column.name} {column.type}{(' PRIMARY KEY' if column.primary_key else '')} {column.constraint}")
        if isinstance(column.foreign_key, SQLHTable) :
          foreign_keys_list.append(f'FOREIGN KEY({column.name}) REFERENCES {column.table.name}({column.table.primary_key.name})')
      temp_str.extend(foreign_keys_list)
      columns_template_strings = ",".join(temp_str)
      query_template += columns_template_strings
      query_template += ");"

      super().execute_query(query_template)

      primary_key = table.primary_key
      primary_key_records = primary_key.get_records()
      if table.get_records_count():
        for i in range(1, table.get_records_count() + 1):
          tmp_list = list()
          for column_dict in table.columns:
            tmp_list.append(column_dict['records'][i - 1])
          self.insert_table(table = table, records = tmp_list)
      
  def insert_table(self, table:SQLHTable, records):
    records = records
    tmp_records = list()
    for record in records:
      tmp_records.append(f"'{str(record)}'" if not str(record).isdigit() and record != 'NULL' else f"{record}")
    records = tmp_records
    if table in self.tables:
      columns = table.get_columns()
      columns_names = [column.name for column in columns]
      query_template = f"INSERT INTO {table.name}({','.join(columns_names)}) VALUES({','.join(records)});"
      super().execute_query(query=query_template)

  def alter_table(self, table:SQLHTable, column:SQLHColumn, method:str = 'ADD'):
    if table in self.tables:
      if method.upper() == 'ADD':
        query_template = f"ALTER TABLE {table.name} ADD {column.name} {column.type} {column.constraint}"
        super().execute_query(query_template)

  def change_record_table(self, table, condition:list):
    """condition = [set_column, set_value, where_column, where_value]"""
    query_template = f"UPDATE {table} SET {condition[0]} = {condition[1]} WHERE {condition[2]} like {condition[3]}"
    super().execute_query(query_template)

  def column_append(self, table, column):
    if table in self.tables and column in table.get_columns():
      table_primary_key = table.primary_key()
      primary_key_records = table.get_records_by_column(table_primary_key)
      column_records = table.get_records_by_column(column)
      self.alter_table(table = table, column = column, method = "add")
      if column_records is not None:
        for index, column_record in enumerate(column_records):
          condition = [column.name, column_record, table_primary_key, primary_key_records[index]]
          self.change_record_table(table=table, condition=condition)

  def find_table(self, table:str|SQLHTable):
    if self.tables is not None:
      for l_table in self.tables:
        if isinstance(table, str):
          if l_table.name == table:
            return l_table
        elif isinstance(table, SQLHTable):
          if l_table is table:
            return l_table
      return None

  def get_records(self, table):
    return super().execute_query(f"SELECT * FROM {table.name}")

  def table_in_file(self, table_name):
    if (f'{table_name}',) in self.file_tables:
      return True
    return False

class SQLHTable(object):
  def __init__(self, name:str, row_id:bool = False, row_id_name:str = "id"):
    self.name = name
    self.columns = []
    self.primary_key = None
    self.live = False
    self.database_object:SQLHDatabase = None
    self.row_id = SQLHColumn(name=row_id_name, type="INTEGER", constraint="NOT NULL", primary_key=True, foreign_key=None) if row_id else None
    if row_id:
      self.primary_key = self.row_id
      self.add_column(self.row_id) 

  def add_column(self, column:SQLHColumn):
    support_column_records = []
    if len(self.columns):
      support_column_records = self.columns[0]["records"]

    if column.primary_key and self.primary_key is not None:
      self.primary_key = column
    self.columns.append({"column_object":column, "records":['NULL' for _ in support_column_records]})

    column.set_table(self)

    if self.live and self.database_object:
      self.database_object.alter_table(table=self, column=column, method='ADD')

  def add_column_records(self, column:SQLHColumn, records:list):
    if len(self.get_records()[0]):
      records = records
      support_column = None
      support_column_records = None
      if self.primary_key:
        support_column = self.primary_key
        support_column_records = self.get_column_dict(support_column)["records"]
      else:
        support_column = self.columns[0]["column_object"]
        support_column_records = self.columns[0]["records"]
      if len(records) < len(support_column_records):
        for _ in range(len(support_column_records) - len(records)):
          records.append("NULL")

      column_dict = self.get_column_dict(column=column)

      for index, record in enumerate(column_dict["records"]):
        column_dict["records"][index] = records[index]

      if self.live and self.database_object:
        for index, record in enumerate(column_dict["records"]):
          self.database_object.change_record_table(table = self.name, condition=[column.name, record, support_column.name, support_column_records[index]])
      
      return True
    else:
      return False

  def add_special_record(self, column, record, index:int = None, condition:list = None):
    """condition = [by_column, by_value]"""
    if self.get_column_dict(column) is not None and len(self.get_records()):
      
      column_dict = self.get_column_dict(column)
      column_records = column_dict["records"]
      support_index = index
      support_column = None
      support_value = None
      if support_index is None:
        support_column = condition[0]
        support_value = condition[1]
        support_column_dict = self.get_column_dict(support_column)
        try:
          support_index = support_column_dict["records"].index(support_value)
        except:
          print("Value was not found")
          return False
      column_records[support_index] = record
      if self.live and self.database_object:
        self.database_object.change_record_table(table = self, condition = [column.name, record, support_column, support_value])
    else:
      return False

  def __null_row_add(self,  records_exec, row_id = True):

    last_id = records_exec[-1][0] if records_exec != [] else 0
    for column_dict in self.columns:
      records = column_dict["records"]
      if row_id:
        records.append([(None if self.row_id is not column_dict["column_object"] else last_id +1) ,("NULL" if self.row_id is not column_dict["column_object"] else last_id + 1)])
      else:
        records.append([None , "NULL"])

  def find_record_by_id(self, id):
    pass

  def change_record(self, column: SQLHColumn|str, record, id, live = False):
    column_dict_index = self.get_column_dict(column=column, index_return=True)
    record = record
    for index, trecord in enumerate(self.columns[column_dict_index]["records"]):
      trecord = trecord if not isinstance(trecord, list) else trecord[0]
      if trecord == id[0]:
        self.columns[column_dict_index]["records"][index][1] = record
    if live:
      self.database_object.change_record_table(self.name, condition=[(column.name if isinstance(column, SQLHColumn) else column), record, self.primary_key.name, id[0]])

  def get_row_by_id(self, id):
    for record in self.get_records(rows=True):
      if record[0] == id:
        return record
    return None

  def delete_record(self, id, live = False):
    for column_dict in self.columns:
      for index, record in enumerate(column_dict["records"]):
        if record[0] == id[0]:
          column_dict["records"].pop(index)
    if live:
      self.database_object.delete_record_table(self, id[0])

  def add_record(self, records:list, live_mode:bool = True, set_row_id = True):
    records_exec = self.database_object.execute_query(f"SELECT * FROM {self.name}")
    primary_key_records = self.get_column_dict(self.primary_key)["records"] 
    self.__null_row_add(row_id=set_row_id, records_exec=records_exec)
    records = records
    if self.row_id and set_row_id:
      records.insert(0, 'none')
    for index, column_dict in enumerate(self.columns):
      last_record = column_dict['records'][-1][1]
      if last_record == 'NULL' and len(records):
        column_dict['records'][-1][1] = records[index]
        column_dict['records'][-1][0] = self.columns[0]['records'][-1][1]
    if self.live and live_mode:
      arg_records = list()                                                                           
      for column_dict in self.columns:
        arg_records.append(column_dict["records"][-1][1])
      self.database_object.insert_table(table = self, records = arg_records)
      # self.database_object.add_record(self, arg_records)

  def set_database(self, database_object:SQLHDatabase):
    if isinstance(database_object, SQLHDatabase):
      self.database_object = database_object
      self.live = True

      if self.database_object.table_in_file(self.name):
        records = self.database_object.get_records(self)
        for record in records:
          correct_record = list(record)
          self.add_record(records=correct_record, live_mode=False, set_row_id=False)
        return True
    return False

  @staticmethod
  def __get_something(arg_list:list, key:str):
    return_list:list = []
    for item in arg_list:
      return_list.append(item[key])
    return return_list

  def get_records(self, rows = False):
    if not rows:
      return self.__get_something(arg_list=self.columns, key="records")
    else:
      return_list = list()
      for i in range(0, len(self.get_column_dict(self.primary_key)['records']) if self.primary_key is not None else len(self.columns[0]['records'])):
        tmp_list = list()
        for column_dict in self.columns:
          tmp_list.append(column_dict['records'][i])
        return_list.append(tmp_list)
      return return_list
  def get_columns(self):
    return self.__get_something(arg_list=self.columns, key="column_object")

  def get_column_dict(self, column:SQLHColumn|str, index_return:bool = False):
    if len(self.get_columns()):
      for index, column_dict in enumerate(self.columns):
        if isinstance(column, SQLHColumn):
          if column_dict["column_object"] is column:
            return (column_dict if not index_return else index)
        elif isinstance(column, str):
          if column_dict["column_object"].name == column:
            return (column_dict if not index_return else index)
    return None
    

  def get_records_count(self):
    if self.primary_key and len(self.get_column_dict(self.primary_key)["records"]):
      primary_key_records = self.get_column_dict(self.primary_key)["records"]
      return len(primary_key_records)
    elif len(self.get_records()) and len(self.get_records()[0]):
      return len(self.get_records()[0])
    return 0

class SQLHColumn(object):
  def __init__(self, name:str, type:str, constraint:str, primary_key:bool = False, foreign_key:SQLHTable = False):
    self.name = name
    self.type = type
    self.constraint = constraint
    self.primary_key = primary_key
    self.foreign_key = foreign_key
    self.table = None
  
  def set_table(self, table:SQLHTable):
    self.table = table

  def get_table(self):
    return self.table

  def get_records(self):
    if self.table:
      return self.table.get_column_dict(self)['records']

main_dtbs = SQLHDatabase(name="data.db")
