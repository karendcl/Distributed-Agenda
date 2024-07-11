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
    Local storage for this node.
    Storage implementations of get must return the same type as put in by set
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
        Set a key to the given value.
        """
        if value == None:
            pass
        else:
            with DDB.at(f"{self.file_name}").session() as (session, file):
                file[f"{key}"] = (time.monotonic(), value)
                session.write()

    def cull(self):
        with DDB.at(f"{self.file_name}").session() as (session, data):
            print(self.iter_older_than(self.ttl))
            for id, _ in self.iter_older_than(self.ttl):
                del data[id]
            session.write()

    def __getitem__(self, key):
        """
        Get the given key.  If item doesn't exist, raises C{KeyError}
        """
        if DDB.at(f"{self.file_name}", key=f"{key}").exists():
            return DDB.at(f"{self.file_name}", key=f"{key}").read()[1]

    def set(self, key, value):
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
        Get given key.  If not found, return default.
        """

        if DDB.at(f"{self.file_name}", key=key).exists():
            log.debug("DDB EXISTS!!!!!!!!!!!!!!!!")
            return DDB.at(f"{self.file_name}", key=f"{key}").read()
        log.debug("DDB DOES NOT EXISTS!!!!!!!!!!!!!!!!")
        return default
    
    def iter_older_than(self, seconds_old):
        min_birthday = time.monotonic() - seconds_old
        zipped = self._triple_iter()
        matches = takewhile(lambda r: min_birthday >= r[1], zipped)
        return list(map(operator.itemgetter(0, 2), matches))

    def _triple_iter(self):
        data = DDB.at(f"{self.file_name}").read()
        keys = data.keys()
        birthday = map(operator.itemgetter(0), data.values())
        values = map(operator.itemgetter(1), data.values())
        return zip(keys, birthday, values)

    def __iter__(self):
        data = DDB.at(f"{self.file_name}").read()
        keys = data.keys()
        values = map(operator.itemgetter(1), data.values())
        return zip(keys, values)

    def __repr__(self):
        return repr(DDB.at(f"{self.file_name}").read())
    
    def __len__(self):
        data = DDB.at(f"{self.file_name}").read()
        return len(data)

class ForgetfulStorage(Storage):
    def __init__(self, ttl=604800):
        """
        By default, max age is a week.
        """
        self.data = OrderedDict()
        self.ttl = ttl

    def __setitem__(self, key, value):
        if key in self.data:
            del self.data[key]
        self.data[key] = (time.monotonic(), value)
        self.cull()

    def cull(self):
        for _, _ in self.iter_older_than(self.ttl):
            self.data.popitem(last=False)

    def get(self, key, default=None):
        self.cull()
        if key in self.data:
            return self[key]
        return default

    def __getitem__(self, key):
        self.cull()
        return self.data[key][1]

    def __repr__(self):
        self.cull()
        return repr(self.data)

    def iter_older_than(self, seconds_old):
        min_birthday = time.monotonic() - seconds_old
        zipped = self._triple_iter()
        matches = takewhile(lambda r: min_birthday >= r[1], zipped)
        return list(map(operator.itemgetter(0, 2), matches))

    def _triple_iter(self):
        ikeys = self.data.keys()
        ibirthday = map(operator.itemgetter(0), self.data.values())
        ivalues = map(operator.itemgetter(1), self.data.values())
        return zip(ikeys, ibirthday, ivalues)

    def __iter__(self):
        self.cull()
        ikeys = self.data.keys()
        ivalues = map(operator.itemgetter(1), self.data.values())
        return zip(ikeys, ivalues)


