import logging



log = logging.getLogger(__name__) 

class Storage:
    """
    Local storage for this node.
    Storage implementations of get must return the same type as put in by set
    """

    def __init__(self, file_name, ttl=604800):
        raise NotImplementedError

    def __setitem__(self, key, value):
        raise NotImplementedError

    def cull(self):
        raise NotImplementedError

    def __getitem__(self, key):
        raise NotImplementedError

    def set(self, key, value):
        raise NotImplementedError

    def get(self, key: str, default=None):
        raise NotImplementedError
    
    def iter_older_than(self, seconds_old):
        raise NotImplementedError

    def _triple_iter(self):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def __repr__(self):
        raise NotImplementedError
    
    def __len__(self):
        raise NotImplementedError

class ForgetfulStorage(Storage):
    def __init__(self, ttl=604800):
        raise NotImplementedError

    def __setitem__(self, key, value):
        raise NotImplementedError
    
    def cull(self):
        raise NotImplementedError

    def get(self, key, default=None):
        raise NotImplementedError

    def __getitem__(self, key):
        raise NotImplementedError

    def __repr__(self):
        raise NotImplementedError

    def iter_older_than(self, seconds_old):
        raise NotImplementedError

    def _triple_iter(self):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError


