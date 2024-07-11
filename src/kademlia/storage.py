import logging
import time
from itertools import takewhile
import operator
from collections import OrderedDict
from abc import abstractmethod, ABC
import dictdatabase as DDB
import json
import pickle

log = logging.getLogger(__name__)  

class Storage:
    """
    Almacenamiento local para este nodo.
    Las implementaciones de almacenamiento de get deben devolver el mismo tipo que el que se puso en set
    """

    def __init__(self, file_name, ttl=604800):
        self.file_name = file_name
        self.ttl = ttl

        DDB.config.storage_directory = "database"

        database = DDB.at(f"{self.file_name}")
        if not database.exists():
            database.create({})
        else:
            #database already exist, do nothing
            pass

    def __setitem__(self, key, value):
        """
        Almacena un valor asociado con una clave en la base de datos.
        """
        if value == None:
            pass
        else:
            with DDB.at(f"{self.file_name}").session() as (session, file):
                file[f"{key}"] = (time.monotonic(), value)
                session.write()

    def cull(self):
        """
        Elimina las claves y valores que han caducado (más viejos que el TTL).
        """
        with DDB.at(f"{self.file_name}").session() as (session, data):
            print(self.iter_older_than(self.ttl))
            for id, _ in self.iter_older_than(self.ttl):
                del data[id]
            session.write()

    def __getitem__(self, key):
        """
        Obtiene el valor asociado con una clave. Lanza KeyError si la clave no existe.
        """
        if DDB.at(f"{self.file_name}", key=f"{key}").exists():
            return DDB.at(f"{self.file_name}", key=f"{key}").read()[1]

    def set(self, key, value):
        """
        Almacena un valor asociado con una clave, actualizando la marca de tiempo si la clave ya existe.
        """
        if value == None:
            pass
        else:
            data = value
            log.debug("New data %s", data)
            if DDB.at(f"{self.file_name}", key=key).exists():
                data_read = DDB.at(f"{self.file_name}", key=f"{key}").read()
                log.debug("Data %s", data_read)
                if value[0] < data_read[0]:
                    data =data_read                  

            with DDB.at(f"{self.file_name}").session() as (session, file):
                file[f"{key}"] = data
                session.write()

    def get(self, key: str, default=None):
        """
        Obtiene el valor asociado con una clave. Si la clave no existe, devuelve el valor predeterminado.
        """

        if DDB.at(f"{self.file_name}", key=key).exists():
            log.debug("DDB EXISTS!!!!!!!!!!!!!!!!")
            return DDB.at(f"{self.file_name}", key=f"{key}").read()
        log.debug("DDB DOES NOT EXISTS!!!!!!!!!!!!!!!!")
        return default
    
    def iter_older_than(self, seconds_old):
        """
        Itera sobre las claves y valores más antiguos que un tiempo dado.
        """
        min_birthday = time.monotonic() - seconds_old
        zipped = self._triple_iter()
        matches = takewhile(lambda r: min_birthday >= r[1], zipped)
        return list(map(operator.itemgetter(0, 2), matches))

    def _triple_iter(self):
        """
        Itera sobre las claves, las marcas de tiempo y los valores de la base de datos.
        """
        data = DDB.at(f"{self.file_name}").read()
        keys = data.keys()
        birthday = map(operator.itemgetter(0), data.values())
        values = map(operator.itemgetter(1), data.values())
        return zip(keys, birthday, values)

    def __iter__(self):
        """
        Itera sobre las claves y valores de la base de datos.
        """
        data = DDB.at(f"{self.file_name}").read()
        keys = data.keys()
        values = map(operator.itemgetter(1), data.values())
        return zip(keys, values)

    def __repr__(self):
        """
        Devuelve una representación de cadena de la base de datos.
        """
        return repr(DDB.at(f"{self.file_name}").read())
    
    def __len__(self):
        """
        Devuelve la cantidad de claves almacenadas en la base de datos.
        """
        data = DDB.at(f"{self.file_name}").read()
        return len(data)

class ForgetfulStorage(Storage):
    """
    Implementación de almacenamiento que no persiste datos.
    """
    def __init__(self, ttl=604800):
        """
        Inicializa el almacenamiento.
        """
        self.data = OrderedDict()
        self.ttl = ttl

    def __setitem__(self, key, value):
        """
        Almacena un valor asociado con una clave.
        """
        if key in self.data:
            del self.data[key]
        self.data[key] = (time.monotonic(), value)
        self.cull()

    def cull(self):
        """
        Elimina las claves y valores que han caducado (más viejos que el TTL).
        """
        for _, _ in self.iter_older_than(self.ttl):
            self.data.popitem(last=False)

    def get(self, key, default=None):
        """
        Obtiene un valor asociado con una clave. Si la clave no existe, devuelve el valor predeterminado.
        """
        self.cull()
        if key in self.data:
            return self[key]
        return default

    def __getitem__(self, key):
        """
        Obtiene el valor asociado con una clave.
        """
        self.cull()
        return self.data[key][1]

    def __repr__(self):
        """
        Devuelve una representación de cadena de los datos almacenados.
        """
        self.cull()
        return repr(self.data)

    def iter_older_than(self, seconds_old):
        """
        Itera sobre las claves y valores más antiguos que un tiempo dado.
        """
        min_birthday = time.monotonic() - seconds_old
        zipped = self._triple_iter()
        matches = takewhile(lambda r: min_birthday >= r[1], zipped)
        return list(map(operator.itemgetter(0, 2), matches))

    def _triple_iter(self):
        """
        Itera sobre las claves, las marcas de tiempo y los valores de los datos almacenados.
        """
        ikeys = self.data.keys()
        ibirthday = map(operator.itemgetter(0), self.data.values())
        ivalues = map(operator.itemgetter(1), self.data.values())
        return zip(ikeys, ibirthday, ivalues)

    def __iter__(self):
        """
        Itera sobre las claves y valores de los datos almacenados.
        """
        self.cull()
        ikeys = self.data.keys()
        ivalues = map(operator.itemgetter(1), self.data.values())
        return zip(ikeys, ivalues)


