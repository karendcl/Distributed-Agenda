import json
import os

from back.DB.Criteria import ICriteria

class DB_Utils:
    def create_database(DB_Name):
        """Crea el directorio principal (base de datos) si no existe."""
        try:
            os.makedirs(DB_Name)
            print(f"Base de datos '{DB_Name}' creada.")
        except FileExistsError:
            print(f"La base de datos '{DB_Name}' ya existe.")

    def delete_database(DB_Name):
        """Elimina el directorio principal (base de datos) y su contenido."""
        try:
            os.rmdir(DB_Name)
            print(f"Base de datos '{DB_Name}' eliminada.")
        except FileNotFoundError: 
            print(f"La base de datos '{DB_Name}' no existe.")

    def create_table(DB_Name, Table_Name, Schema, auto_increment=False):
        """Crea un archivo JSON vacío para la tabla y un archivo .meta para almacenar información adicional."""
        ruta_archivo = os.path.join(DB_Name, f"{Table_Name}.json")
        ruta_meta = os.path.join(DB_Name, f"{Table_Name}.meta")

        if not os.path.exists(ruta_archivo):
            with open(ruta_archivo, 'w') as archivo:
                json.dump([], archivo)  # Crea un arreglo JSON vacío para los datos
                print(f"Tabla '{Table_Name}' creada.")

            with open(ruta_meta, 'w') as archivo_meta:
                meta_info = {"auto_increment": auto_increment, "last_index": 0}
                json.dump(meta_info, archivo_meta, indent=4)  # Crea un archivo .meta con información adicional
                print(f"Archivo .meta para la tabla '{Table_Name}' creado.")
            
            ruta_esquema = os.path.join(DB_Name, f"{Table_Name}.schema.json")
            with open(ruta_esquema, 'w') as archivo_esquema:
                json.dump(Schema, archivo_esquema, indent=4)
                print(f"Esquema de la tabla '{Table_Name}' creado.")
        else:
            print(f"La tabla '{Table_Name}' ya existe.")

    def delete_table(DB_Name, Table_Name):
        """Elimina el archivo JSON de la tabla."""
        ruta_archivo = os.path.join(DB_Name, f"{Table_Name}.json")
        try:
            os.remove(ruta_archivo)
            print(f"Tabla '{Table_Name}' eliminada.")
        except FileNotFoundError:
            print(f"La tabla '{Table_Name}' no existe.")

    def insert_data(DB_Name, Table_Name, data):
        """Agrega un nuevo objeto JSON al archivo de la tabla."""
        ruta_archivo = os.path.join(DB_Name, f"{Table_Name}.json")
        ruta_esquema = os.path.join(DB_Name, f"{Table_Name}.schema.json")
        ruta_meta = os.path.join(DB_Name, f"{Table_Name}.meta")

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
            else:
                print("ADVERTENCIA: La tabla tiene autoincremento, se ignorará el campo 'id' proporcionado.")

        # Valida el tipo de dato usando el esquema
        with open(ruta_esquema, 'r') as archivo_esquema:
            esquema = json.load(archivo_esquema)
            for columna, tipo_dato in esquema["columnas"].items():
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

            registros.append(data)
            archivo.seek(0)
            json.dump(registros, archivo, indent=4)
            print(f"Datos insertados en la tabla '{Table_Name}'.")


    def get_data(DB_Name, Table_Name, criteria : ICriteria = None):
        """Lee y filtra los datos del archivo JSON según el criterio (opcional)."""
        ruta_archivo = os.path.join(DB_Name, f"{Table_Name}.json")
        with open(ruta_archivo, 'r') as archivo:
            registros = json.load(archivo)
            if criteria:
                # Filtra los registros según el criterio (implementa tu lógica aquí)
                registros_filtrados = [registro for registro in registros if criteria(registro)]
            else:
                registros_filtrados = registros
            return registros_filtrados

    def update_data(DB_Name, Table_Name, id_registro, new_data):
        """Actualiza un registro existente por su ID."""
        ruta_archivo = os.path.join(DB_Name, f"{Table_Name}.json")
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

    def delete_data(DB_Name, Table_Name, id_registro):
        """Elimina un registro existente por su ID."""
        ruta_archivo = os.path.join(DB_Name, f"{Table_Name}.json")
        with open(ruta_archivo, 'r+') as archivo:
            registros = json.load(archivo)
            registros = [registro for registro in registros if registro.get('id') != id_registro]
            archivo.seek(0)
            json.dump(registros, archivo, indent=4)
            print(f"Registro con ID {id_registro} eliminado.")

