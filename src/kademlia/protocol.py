import random
import asyncio
import logging

from kademlia.rpcudp import RPCProtocol

from kademlia.node import Node
from kademlia.routing import RoutingTable
from kademlia.utils import digest

log = logging.getLogger(__name__)  


class KademliaProtocol(RPCProtocol):
    """
    Implementa el protocolo Kademlia utilizando RPC UDP para la comunicación entre nodos.
    """
    def __init__(self, source_node, storage, ksize):
        """
        Inicializa el protocolo Kademlia.

        Args:
            source_node: El nodo actual.
            storage: El almacenamiento local del nodo.
            ksize: El tamaño de la tabla de enrutamiento.
        """
        RPCProtocol.__init__(self)
        self.router = RoutingTable(self, ksize, source_node)
        self.storage = storage
        self.source_node = source_node

    def get_refresh_ids(self):
        """
        Obtiene una lista de IDs de nodos para actualizar los buckets inactivos en la tabla de enrutamiento.
        """
        ids = []
        
        log.debug("LONELY BUCKETS: %s", self.router.lonely_buckets())
        log.debug("BUCKETS: %s", self.router.buckets)
        
        for bucket in self.router.lonely_buckets():
            rid = random.randint(*bucket.range).to_bytes(20, byteorder='big')
            ids.append(rid)
        
        log.debug('GET REFRESH IDS: %s', ids)
        
        return ids

    def rpc_stun(self, sender):
        """
        Método RPC para `stun`.  Devuelve la dirección del remitente.
        """  
        return sender

    def rpc_ping(self, sender, nodeid):
        """
        Método RPC para `ping`. Verifica si un nodo está activo.
        """
        source = Node(nodeid, sender[0], sender[1])
        self.welcome_if_new(source)
        
        return self.source_node.id

    def rpc_refresh(self, sender, nodeid, key, value):
        """
        Método RPC para `refresh`.  Actualiza el valor asociado con una clave en otro nodo.
        """
        source = Node(nodeid, sender[0], sender[1])
        self.welcome_if_new(source)

        log.debug("got a refresh store request from %s, storing '%s'='%s'",
                sender, key, value)
        self.storage.set(key, value)
        return True

    def rpc_store(self, sender, nodeid, key, value):
        """
        Método RPC para `store`. Almacena un valor en otro nodo.
        """
        source = Node(nodeid, sender[0], sender[1])
        self.welcome_if_new(source)

        log.debug("got a store request from %s, storing '%s'='%s'",
                sender, key, value)
        self.storage[key] = value
        
        return True

    def rpc_find_node(self, sender, nodeid, key):
        """
        Método RPC para `find_node`. Encuentra los vecinos más cercanos a una clave.
        """
        log.info("finding neighbors of %i in local table",
                int(nodeid, 16))
        source = Node(nodeid, sender[0], sender[1])
        self.welcome_if_new(source)
        node = Node(key)
        neighbors = self.router.find_neighbors(node, exclude=source)
    
        return list(map(tuple, neighbors))

    def rpc_find_value(self, sender, nodeid, key):
        """
        Método RPC para `find_value`. Encuentra el valor asociado con una clave.
        """
        source = Node(nodeid, sender[0], sender[1])
        self.welcome_if_new(source)
        value = self.storage.get(key, None)
        if value is None:
            return self.rpc_find_node(sender, nodeid, key)
        
        return {'value': value}

    #Metodos asincronos para llamar a otros metodos
    async def call_find_node(self, node_to_ask, node_to_find):
        
        address = (node_to_ask.ip, node_to_ask.port)
        result = await self.find_node(address, self.source_node.id,
                                    node_to_find.id)
        return self.handle_call_response(result, node_to_ask)

    async def call_find_value(self, node_to_ask, node_to_find):
        
        address = (node_to_ask.ip, node_to_ask.port)
        result = await self.find_value(address, self.source_node.id,
                                    node_to_find.id)
        
        return self.handle_call_response(result, node_to_ask)

    async def call_ping(self, node_to_ask):
        address = (node_to_ask.ip, node_to_ask.port)
        result = await self.ping(address, self.source_node.id)
        
        return self.handle_call_response(result, node_to_ask)

    async def call_store(self, node_to_ask, key, value):
        address = (node_to_ask.ip, node_to_ask.port)
        result = await self.store(address, self.source_node.id, key, value)
        
        return self.handle_call_response(result, node_to_ask)
    
    async def call_refresh(self, node_to_ask, key, value):
        address = (node_to_ask.ip, node_to_ask.port)
        result = await self.refresh(address, self.source_node.id, key, value)
        
        return self.handle_call_response(result, node_to_ask)

    def welcome_if_new(self, node):
        log.info("node %s", node)
        """
        Si un nodo es nuevo, se le envían todos los datos que debería almacenar
        y luego se agrega a la tabla de enrutamiento.

        Args:
            node: Un nuevo nodo que se acaba de unir (o del que acabamos de enterarnos).

        Proceso:
        Para cada clave en el almacenamiento, obtener k nodos más cercanos.  Si el nuevo nodo está más cerca
        que el más lejano en esa lista, y el nodo de este servidor
        está más cerca que el más cercano en esa lista, entonces almacenar la clave/valor
        en el nuevo nodo (Guiandome por el paper de Kademlia).
        """
        if not self.router.is_new_node(node):
            log.info("already in router")
            return

        log.info("never seen %s before, adding to router", node)
        log.debug("%s elements in storage of node %s", len(self.storage), self.source_node.long_id)
        for key, value in self.storage:
            
            log.info("Element in storage: %s %s", key, value)
            keynode = Node(digest(key))
            neighbors = self.router.find_neighbors(keynode)
            log.info("NEIGHBOURS %s", neighbors)
            
            if neighbors:
                last = neighbors[-1].distance_to(keynode)
                new_node_close = node.distance_to(keynode) < last
                log.info("NEW NODE CLOSE %s", new_node_close)
                first = neighbors[0].distance_to(keynode)
                this_closest = self.source_node.distance_to(keynode) < first
                log.info("THIS CLOSEST %s", this_closest)
            
            if not neighbors or (new_node_close and this_closest):
                asyncio.ensure_future(self.call_store(node, key, value))
        
        self.router.add_contact(node)

    def handle_call_response(self, result, node):
        """
        Si recibimos una respuesta, agregamos el nodo a la tabla de enrutamiento. Si
        no recibimos una respuesta, nos aseguramos de que se elimine de la tabla de enrutamiento.
        """
        if not result[0]:
            log.warning("no response from %s, removing from router", node)
            self.router.remove_contact(node)
            return result

        log.info("got successful response from %s", node)
        self.welcome_if_new(node)
        return result
