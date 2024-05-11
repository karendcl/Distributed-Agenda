from typing import List
from DB_Utils import DB_Utils

class Database:

    path = "src\database"

    def __init__(self, name, path = None):
        self.name = name
        self.tables : List[Table] = []
        if path:
            self.path = path
        self.create()

    def create(self):
        try:
            DB_Utils.create_database(self.name, self.path)
        except FileExistsError:
            print(f"La base de datos '{self.name}' ya existe. Cargando la base de datos")
            self.load()
    
    def load(self):
        table_names = DB_Utils.get_tables(self.name, self.path)
        for table_name in table_names:
            schema = DB_Utils.get_schema(self.name, table_name, self.path)
            auto_increment = DB_Utils.get_auto_increment(self.name, table_name, self.path)
            table = Table(self.name, table_name, schema, self.path, auto_increment,  load=False)
            self.tables.append(table)
    
    def create_table(self, table_name, schema, auto_increment=False):
        table = Table(self.name, table_name, schema, self.path, auto_increment)
        return table
    
    def drop_table(self, table_name):
        DB_Utils.delete_table(self.name, table_name, self.path)
    
    def drop(self):
        table_names = [table.name for table in self.tables]
        for table_name in table_names:
            self.drop_table(table_name)
        DB_Utils.delete_database(self.name, self.path)

    def __str__(self) -> str:
        tables_str = '\n '.join([table.name for table in self.tables])
        return f"Database: {self.name}\n--------------------------\nTables: {tables_str}"

class Table:
    
    def __init__(self, DB_Name, name, schema, path, auto_increment=False, load=True):
        self.name = name
        self.schema = schema
        self.auto_increment = auto_increment
        self.DB_Name = DB_Name
        self.path = path

        if load:    
            self._create()

    def _create(self):
        DB_Utils.create_table(self.DB_Name, self.name, self.schema, self.path, self.auto_increment)

    def insert(self, data):
        DB_Utils.insert_data(self.DB_Name, self.name, data, self.path)

    def get(self, criteria=None):
        return DB_Utils.get_data(self.DB_Name, self.name, self.path, criteria)

    def update(self, id_registro, new_data):
        DB_Utils.update_data(self.DB_Name, self.name, id_registro, new_data, self.path)

    def delete(self, id_registro):
        DB_Utils.delete_data(self.DB_Name, self.name, id_registro, self.path)

    def __str__(self) -> str:
        return f"Table: {self.name}\n--------------------------\nSchema: {self.schema}\nAuto Increment: {self.auto_increment}"


