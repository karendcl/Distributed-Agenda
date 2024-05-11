from back.DB.DB_Utils import DB_Utils

class Database:
    def __init__(self, name):
        self.name = name
        self.tables = []

    def create(self):
        DB_Utils.create_database(self.name)

    def create_table(self, table_name, schema, auto_increment=False):
        table = Table(self.name, table_name, schema, auto_increment)
        return table
    
    def drop_table(self, table_name):
        DB_Utils.delete_table(self.name, table_name)
    
    def drop(self):
        DB_Utils.delete_database(self.name)

    def __str__(self) -> str:
        tables_str = '\n '.join([table.name for table in self.tables])
        return f"Database: {self.name}\n--------------------------\nTables: {tables_str}"

class Table:
    def __init__(self, DB_Name, name, schema, auto_increment=False):
        self.name = name
        self.schema = schema
        self.auto_increment = auto_increment
        self.DB_Name = DB_Name

        self._create(self, DB_Name)

    def _create(self, DB_Name):
        DB_Utils.create_table(DB_Name, self.name, self.schema, self.auto_increment)

    def insert(self, DB_Name, data):
        DB_Utils.insert_data(DB_Name, self.name, data)

    def get(self, DB_Name, criteria=None):
        return DB_Utils.get_data(DB_Name, self.name, criteria)

    def update(self, DB_Name, id_registro, new_data):
        DB_Utils.update_data(DB_Name, self.name, id_registro, new_data)

    def delete(self, DB_Name, id_registro):
        DB_Utils.delete_data(DB_Name, self.name, id_registro)

    def __str__(self) -> str:
        return f"Table: {self.name}\n--------------------------\nSchema: {self.schema}\nAuto Increment: {self.auto_increment}"


