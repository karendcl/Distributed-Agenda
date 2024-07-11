import logging

from kademlia.rpcudp import RPCProtocol

log = logging.getLogger(__name__)  # pylint: disable=invalid-name


class KademliaProtocol(RPCProtocol):
    def __init__(self, source_node, storage, ksize):
               raise NotImplementedError


    def get_refresh_ids(self):
               raise NotImplementedError


    def rpc_stun(self, sender):  # pylint: disable=no-self-use
               raise NotImplementedError

    def rpc_ping(self, sender, nodeid):
              raise NotImplementedError

    def rpc_refresh(self, sender, nodeid, key, value):
               raise NotImplementedError


    def rpc_store(self, sender, nodeid, key, value):
               raise NotImplementedError


    def rpc_find_node(self, sender, nodeid, key):
               raise NotImplementedError


    def rpc_find_value(self, sender, nodeid, key):
               raise NotImplementedError


    async def call_find_node(self, node_to_ask, node_to_find):
               raise NotImplementedError

    async def call_find_value(self, node_to_ask, node_to_find):
               raise NotImplementedError


    async def call_ping(self, node_to_ask):
               raise NotImplementedError

    async def call_store(self, node_to_ask, key, value):
               raise NotImplementedError

    async def call_refresh(self, node_to_ask, key, value):
               raise NotImplementedError


    def welcome_if_new(self, node):
               raise NotImplementedError

    def handle_call_response(self, result, node):
               raise NotImplementedError

