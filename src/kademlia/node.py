
import logging

log = logging.getLogger(__name__)  # pylint: disable=invalid-name


class Node:
    """
    Simple object to encapsulate the concept of a Node (minimally an ID, but
    also possibly an IP and port if this represents a node on the network).
    This class should generally not be instantiated directly, as it is a low
    level construct mostly used by the router.
    """

    def __init__(self, node_id, ip=None, port=None):
       raise NotImplementedError

    def same_home_as(self, node):
        raise NotImplementedError

    def distance_to(self, node):
        raise NotImplementedError

    def __iter__(self):
       raise NotImplementedError
    def __repr__(self):
        raise NotImplementedError
    def __str__(self):
        raise NotImplementedError


class NodeHeap:
    """
    A heap of nodes ordered by distance to a given node.
    """

    def __init__(self, node, maxsize):
        raise NotImplementedError

    def remove(self, peers):
        raise NotImplementedError

    def get_node(self, node_id):
        raise NotImplementedError

    def have_contacted_all(self):
        raise NotImplementedError

    def get_ids(self):
        raise NotImplementedError

    def mark_contacted(self, node):
        raise NotImplementedError

    def popleft(self):
       raise NotImplementedError

    def push(self, nodes):
       raise NotImplementedError

    def __len__(self):
        return min(len(self.heap), self.maxsize)

    def __iter__(self):
       raise NotImplementedError

    def __contains__(self, node):
       raise NotImplementedError

    def get_uncontacted(self):
        raise NotImplementedError
