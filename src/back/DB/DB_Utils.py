import json
import os

from Criteria import ICriteria

class DB_Utils:
    
    @staticmethod
    def create_database(DB_Name, address):
        """Crea el directorio principal (base de datos) si no existe."""
        db_path = os.path.join(address, DB_Name)
        try:
            os.mkdir(db_path)
            print(f"Base de datos '{DB_Name}' creada.")
        except FileExistsError:
            # print(f"La base de datos '{DB_Name}' ya existe.")
            raise FileExistsError
    
    @staticmethod
    def delete_database(DB_Name, address):
        """Elimina el directorio principal (base de datos) y su contenido."""
        db_path = os.path.join(address, DB_Name)
        try:
            os.rmdir(db_path)
            print(f"Base de datos '{DB_Name}' eliminada.")
        except FileNotFoundError: 
            print(f"La base de datos '{DB_Name}' no existe.")

    @staticmethod
    def create_table(DB_Name, Table_Name, Schema, address, auto_increment=False):
        """Crea un archivo JSON vacío para la tabla y un archivo .meta para almacenar información adicional."""
        ruta_archivo = os.path.join(address, DB_Name, f"{Table_Name}.json")
        ruta_meta = os.path.join(address, DB_Name, f"{Table_Name}.meta")

        if not os.path.exists(ruta_archivo):
            with open(ruta_archivo, 'w') as archivo:
                json.dump([], archivo)  # Crea un arreglo JSON vacío para los datos
                print(f"Tabla '{Table_Name}' creada.")

            with open(ruta_meta, 'w') as archivo_meta:
                meta_info = {"auto_increment": auto_increment, "last_index": 0}
                json.dump(meta_info, archivo_meta, indent=4)  # Crea un archivo .meta con información adicional
                print(f"Archivo .meta para la tabla '{Table_Name}' creado.")
            
            ruta_esquema = os.path.join(address, DB_Name, f"{Table_Name}.schema.json")
            with open(ruta_esquema, 'w') as archivo_esquema:
                json.dump(Schema, archivo_esquema, indent=4)
                print(f"Esquema de la tabla '{Table_Name}' creado.")
        else:
            print(f"La tabla '{Table_Name}' ya existe.")

    @staticmethod
    def delete_table(DB_Name, Table_Name, address):
        """Elimina el archivo JSON de la tabla."""
        ruta_archivo = os.path.join(address, DB_Name, f"{Table_Name}.json")
        ruta_meta = os.path.join(address, DB_Name, f"{Table_Name}.meta")
        ruta_esquema = os.path.join(address, DB_Name, f"{Table_Name}.schema.json")
        try:
            os.remove(ruta_archivo)
            os.remove(ruta_meta)
            os.remove(ruta_esquema)
            print(f"Tabla '{Table_Name}' eliminada.")
        except FileNotFoundError:
            print(f"La tabla '{Table_Name}' no existe.")
    
    @staticmethod
    def get_tables(DB_Name: str, address: str):
        """Devuelve una lista con los nombres de las tablas en la base de datos."""
        db_path = os.path.join(address, DB_Name)
        tables = [filename.split('.')[0] for filename in os.listdir(db_path) if filename.endswith('.json')]
        return tables

    @staticmethod
    def get_schema(DB_Name: str, table_name: str, address: str):
        """Retorna el esquema de la tabla especificada por 'table_name' en la base de datos especificada por 'DB_Name'."""
        schema_path = os.path.join(address, DB_Name, f"{table_name}.schema.json")
        with open(schema_path, 'r') as schema_file:
            schema = json.load(schema_file)
        return schema

    @staticmethod
    def get_auto_increment(DB_Name: str, table_name: str, address: str):
        """Retorna un booleano indicando si la tabla tiene autoincremento."""
        meta_path = os.path.join(address, DB_Name, f"{table_name}.meta")
        if os.path.exists(meta_path):
            with open(meta_path, 'r') as meta_file:
                meta_info = json.load(meta_file)
                return meta_info.get("auto_increment", False)
        return False

    @staticmethod
    def insert_data(DB_Name, Table_Name, data, address):
        """Agrega un nuevo objeto JSON al archivo de la tabla."""
        ruta_archivo = os.path.join(address, DB_Name, f"{Table_Name}.json")
        ruta_esquema = os.path.join(address, DB_Name, f"{Table_Name}.schema.json")
        ruta_meta = os.path.join(address, DB_Name, f"{Table_Name}.meta")

        # Verifica si la tabla tiene autoincremento
        if os.path.exists(ruta_meta):
            with open(ruta_meta, 'r') as archivo_meta:
                meta_info = json.load(archivo_meta)
                auto_increment = meta_info.get("auto_increment", False)
        else:
            auto_increment = False

        # Si la tabla tiene autoincremento, no es necesario añadir ID a los datos
        if auto_increment:
            if "id" in data:
                print("ADVERTENCIA: La tabla tiene autoincremento, no es necesario añadir el campo 'id' a los datos.")

        # Valida el tipo de dato usando el esquema
        with open(ruta_esquema, 'r') as archivo_esquema:
            esquema = json.load(archivo_esquema)
            for columna, tipo_dato in esquema.items():
                if columna in data:
                    # Convierte el string del tipo de dato a un tipo real usando eval()
                    if not isinstance(data[columna], eval(tipo_dato)):
                        raise TypeError(f"El valor de '{columna}' debe ser de tipo {tipo_dato}")

        # Si la validación es exitosa, guarda los datos en el archivo JSON
        with open(ruta_archivo, 'r+') as archivo:
            registros = json.load(archivo)

            # Si la tabla tiene autoincremento, se genera automáticamente el ID
            if auto_increment:
                last_index = meta_info.get("last_index", 0)
                data["id"] = last_index + 1
                meta_info["last_index"] = data["id"]

                with open(ruta_meta, 'r+') as archivo_meta:
                    archivo_meta.seek(0)
                    json.dump(meta_info, archivo_meta, indent=4)

            registros.append(data)
            archivo.seek(0)
            json.dump(registros, archivo, indent=4)
            print(f"Datos insertados en la tabla '{Table_Name}'.")


    @staticmethod
    def get_data(DB_Name, Table_Name, address, criteria : ICriteria):
        """Lee y filtra los datos del archivo JSON según el criterio (opcional)."""
        ruta_archivo = os.path.join(address, DB_Name, f"{Table_Name}.json")
        with open(ruta_archivo, 'r') as archivo:
            registros = json.load(archivo)
            if criteria:
                # Filtra los registros según el criterio (implementa tu lógica aquí)
                registros_filtrados = [registro for registro in registros if criteria(registro)]
            else:
                registros_filtrados = registros
            return registros_filtrados

    @staticmethod
    def update_data(DB_Name, Table_Name, id_registro, new_data, address):
        """Actualiza un registro existente por su ID."""
        ruta_archivo = os.path.join(address, DB_Name, f"{Table_Name}.json")
        with open(ruta_archivo, 'r+') as archivo:
            registros = json.load(archivo)
            indice_registro = None
            for i, registro in enumerate(registros):
                if registro.get('id') == id_registro:
                    indice_registro = i
                    break
            if indice_registro is not None:
                registros[indice_registro].update(new_data)  # Actualiza los datos
                archivo.seek(0)
                json.dump(registros, archivo, indent=4)
                print(f"Registro con ID {id_registro} actualizado.")
            else:
                print(f"Registro con ID {id_registro} no encontrado.")

    @staticmethod
    def delete_data(DB_Name, Table_Name, id_registro, address):
        """Elimina un registro existente por su ID."""
        ruta_archivo = os.path.join(address, DB_Name, f"{Table_Name}.json")
        with open(ruta_archivo, 'r+') as archivo:
            registros = json.load(archivo)
            registros = [registro for registro in registros if registro.get('id') != id_registro]
            archivo.seek(0)
            json.dump(registros, archivo, indent=4)
            print(f"Registro con ID {id_registro} eliminado.")

