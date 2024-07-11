"""
Package for interacting on the network at a high level.
"""

import logging

from kademlia.protocol import KademliaProtocol


log = logging.getLogger(__name__)  # pylint: disable=invalid-name


# pylint: disable=too-many-instance-attributes
class Server:
    """
    High level view of a node instance.  This is the object that should be
    created to start listening as an active node on the network.
    """

    protocol_class = KademliaProtocol

    def __init__(self, ip, ksize=3, alpha=2, node_id=None, storage=None):
        raise NotImplementedError


    def stop(self):
        raise NotImplementedError


    def _create_protocol(self):
        raise NotImplementedError


    async def listen(self, port, interface='0.0.0.0'):
        raise NotImplementedError


    def refresh_table(self):
        raise NotImplementedError

    async def _refresh_table(self):
        raise NotImplementedError


    def bootstrappable_neighbors(self):
        raise NotImplementedError


    async def bootstrap(self, addrs):
        raise NotImplementedError


    async def bootstrap_node(self, addr):
        raise NotImplementedError


    async def get(self, key, refresh=False):
       raise NotImplementedError


    async def set(self, key, value):
       raise NotImplementedError


    async def set_digest(self, dkey, value):
       raise NotImplementedError


    async def set_refresh(self, dkey, value):
        raise NotImplementedError


    def save_state(self, fname):
        raise NotImplementedError


    @classmethod
    async def load_state(cls, fname, port, interface='0.0.0.0'):
       raise NotImplementedError


    def save_state_regularly(self, fname, frequency=600):
        raise NotImplementedError


def check_dht_value_type(value):
   raise NotImplementedError
