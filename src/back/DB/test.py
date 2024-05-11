# Importa las clases necesarias
from DB import Database
from DB_Utils import DB_Utils

# Crear una instancia de la base de datos
my_database = Database("my_database")


# Crear una tabla en la base de datos
users_table = my_database.create_table("users", {"id": "int", "name": "str", "age": "int"}, auto_increment=True)

# Insertar datos en la tabla
users_table.insert({"name": "John", "age": 30})
users_table.insert({"name": "Alice", "age": 25})

# Obtener todos los registros de la tabla
all_users = users_table.get()
print("Todos los usuarios:", all_users)

# Obtener los usuarios mayores de 26 años
criteria = lambda x: x.get('age') > 26
users_above_26 = users_table.get(criteria)
print("Usuarios mayores de 26 años:", users_above_26)

# Actualizar el nombre del usuario con ID 1
users_table.update(1, {"name": "Johnny"})

# # Eliminar el usuario con ID 2
# users_table.delete(2)

# # Eliminar la tabla de la base de datos
# my_database.drop_table("users")

# # Eliminar la base de datos
# my_database.drop()
