import logging


log = logging.getLogger(__name__) 

class KBucket:
    def __init__(self, rangeLower, rangeUpper, ksize, replacementNodeFactor=5):
        raise NotImplementedError


    def touch_last_updated(self):
        raise NotImplementedError


    def get_nodes(self):
        raise NotImplementedError


    def split(self):
        raise NotImplementedError


    def remove_node(self, node):
        raise NotImplementedError


    def has_in_range(self, node):
        raise NotImplementedError


    def is_new_node(self, node):
        raise NotImplementedError

    def add_node(self, node):
        raise NotImplementedError


    def depth(self):
        raise NotImplementedError


    def head(self):
        raise NotImplementedError


    def __getitem__(self, node_id):
        raise NotImplementedError


    def __len__(self):
        raise NotImplementedError



class TableTraverser:
    def __init__(self, table, startNode):
        raise NotImplementedError


    def __iter__(self):
        raise NotImplementedError


    def __next__(self):
        raise NotImplementedError



class RoutingTable:
    def __init__(self, protocol, ksize, node):
        raise NotImplementedError


    def flush(self):
        raise NotImplementedError


    def split_bucket(self, index):
        raise NotImplementedError


    def lonely_buckets(self):
        raise NotImplementedError


    def remove_contact(self, node):
        raise NotImplementedError


    def is_new_node(self, node):
        raise NotImplementedError

    def add_contact(self, node):
        raise NotImplementedError

    def get_bucket_for(self, node):
        raise NotImplementedError

    def find_neighbors(self, node, k=None, exclude=None):
        raise NotImplementedError
