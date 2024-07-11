"""
Package for interacting on the network via a Async Protocol
"""
import asyncio
import logging

LOG = logging.getLogger(__name__)


class MalformedMessage(Exception):
    """
    Message does not contain what is expected.
    """


class RPCProtocol(asyncio.DatagramProtocol):
    """
    Protocol implementation using msgpack to encode messages and asyncio
    to handle async sending / recieving.
    """

    def __init__(self, wait_timeout=5):
        raise NotImplementedError

    def connection_made(self, transport):
        raise NotImplementedError

    def datagram_received(self, data, addr):
        raise NotImplementedError
    async def _solve_datagram(self, datagram, address):
        raise NotImplementedError

    def _accept_response(self, msg_id, data, address):
        raise NotImplementedError

    async def _accept_request(self, msg_id, data, address):
        raise NotImplementedError

    def _timeout(self, msg_id):
        raise NotImplementedError
    def __getattr__(self, name):
        raise NotImplementedError
