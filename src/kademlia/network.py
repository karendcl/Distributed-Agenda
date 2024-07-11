"""
Package for interacting on the network at a high level.
"""
import random
import pickle
import asyncio
import logging
import uuid

from kademlia.protocol import KademliaProtocol
from kademlia.utils import digest
from kademlia.storage import Storage, ForgetfulStorage
from kademlia.node import Node
from kademlia.crawling import ValueSpiderCrawl
from kademlia.crawling import NodeSpiderCrawl

log = logging.getLogger(__name__)  


class Server:
    """
    Vista de alto nivel de una instancia de nodo. Este es el objeto que debe
    crearse para comenzar a escuchar como un nodo activo en la red.
    """

    protocol_class = KademliaProtocol

    def __init__(self, ip, ksize=3, alpha=2, node_id=None, storage=None):
        """
        Crea una instancia de server. Este comenzará a escuchar en el puerto dado.

        Args:
            ksize (int): El parámetro k del documento
            alpha (int): El parámetro alpha del documento
            node_id: El ID para este nodo en la red.
            storage: Una instancia que implementa la interfaz
                    :class:`~kademlia.storage.IStorage`
        """
        self.id = uuid.uuid4()
        self.ksize = ksize
        self.alpha = alpha
        self.storage = Storage(self.id)
        self.node = Node(node_id or digest(ip))
        self.transport = None
        self.protocol = None
        self.refresh_loop = None
        self.save_state_loop = None

    def stop(self):
        """
        Detiene el servidor.
        """
        if self.transport is not None:
            self.transport.close()

        if self.refresh_loop:
            self.refresh_loop.cancel()

        if self.save_state_loop:
            self.save_state_loop.cancel()

    def _create_protocol(self):
        """
        Crea una instancia del protocolo Kademlia.
        """
        return self.protocol_class(self.node, self.storage, self.ksize)

    async def listen(self, port, interface='0.0.0.0'):
        """
        Comienza a escuchar en el puerto dado.

        Proporciona interface="::" para aceptar direcciones IPv6
        """
        loop = asyncio.get_event_loop()
        listen = loop.create_datagram_endpoint(self._create_protocol,
                                               local_addr=(interface, port))
        log.info("Node %i listening on %s:%i",
                 self.node.long_id, interface, port)
        self.node.ip = interface
        self.node.port = port
        self.transport, self.protocol = await listen
        self.refresh_table()

    def refresh_table(self):
        """
        Actualiza la tabla de enrutamiento.
        """
        log.debug("Refreshing routing table")
        asyncio.ensure_future(self._refresh_table())
        loop = asyncio.get_event_loop()
        self.refresh_loop = loop.call_later(30, self.refresh_table)

    async def _refresh_table(self):
        """
        Actualiza los buckets que no han tenido ninguna búsqueda en la última hora
        """
        results = []
        for node_id in self.protocol.get_refresh_ids():
            node = Node(node_id)
            nearest = self.protocol.router.find_neighbors(node, self.alpha)
            log.debug('NEAREST IN REFRESH TABLE: %s', nearest)
            spider = NodeSpiderCrawl(self.protocol, node, nearest,
                                    self.ksize, self.alpha)
            results.append(spider.find())

        await asyncio.gather(*results)

        for dkey, value in self.storage:
            data = self.storage.get(dkey)
            await self.set_refresh(dkey, data)

    def bootstrappable_neighbors(self):
        """
        Obtiene una lista de pares (ip, port) aptos para
        usarse como argumento para el método bootstrap.

        El servidor debería haber sido iniciado
        ya - esta es solo una utilidad para obtener algunos vecinos y luego
        almacenarlos si este servidor se está apagando por un tiempo. Cuando vuelve
        a estar activo, la lista de nodos se puede usar para iniciar el servidor.
        """
        neighbors = self.protocol.router.find_neighbors(self.node)
        return [tuple(n)[-2:] for n in neighbors]

    async def bootstrap(self, addrs):
        """
        Inicia el servidor conectándose a otros nodos conocidos en la red.

        Args:
            addrs: Una lista de pares (ip, port). Ten en cuenta que solo las direcciones IP
                son aceptables - los nombres de host causarán un error.
        """
        log.debug("Attempting to bootstrap node with %i initial contacts",
                  len(addrs))
        cos = list(map(self.bootstrap_node, addrs))
        gathered = await asyncio.gather(*cos)
        nodes = [node for node in gathered if node is not None]
        spider = NodeSpiderCrawl(self.protocol, self.node, nodes,
                                 self.ksize, self.alpha)
        return await spider.find()

    async def bootstrap_node(self, addr):
        """
        Envía una solicitud de ping a un nodo dado para verificar su disponibilidad.
        """
        result = await self.protocol.ping(addr, self.node.id)
        return Node(result[1], addr[0], addr[1]) if result[0] else None

    async def get(self, key, refresh=False):
        """
        Obtiene una clave si la red la tiene.

        Returns:
            :class:`None` si no se encuentra, el valor en caso contrario.
        """
        log.info("Looking up key %s", key)
        dkey = key
        if not refresh:
            dkey = digest(key)
        res_self = self.storage.get(dkey)
        log.debug("RESULT GET SELF: %s", res_self)

        node = Node(dkey)
        nearest = self.protocol.router.find_neighbors(node)
        if not nearest:
            log.warning("There are no known neighbors to get key %s", key)
            return None
        spider = ValueSpiderCrawl(self.protocol, node, nearest,
                                  self.ksize, self.alpha)
        result = await spider.find()

        log.debug("RESULT GET: %s", result)

        if res_self is not None and result is not None:
            if res_self[0] > result[0]:
                return res_self[1] 
            else:
                self.storage[dkey] = result[1]
                return result[1]
        if res_self is not None:
            return res_self[1]
        if result is not None:
            return result[1]
        return None

    async def set(self, key, value):
        """
        Asigna la clave de cadena dada al valor dado en la red.
        """
        if not check_dht_value_type(value):
            raise TypeError(
                "Value must be of type int, float, bool, str, or bytes"
            )
        log.info("setting '%s' = '%s' on network", key, value)
        dkey = digest(key)
        return await self.set_digest(dkey, value)

    async def set_digest(self, dkey, value):
        """
        Asigna la clave SHA1 dada (bytes) al valor dado en la red.
        """
        node = Node(dkey)

        nearest = self.protocol.router.find_neighbors(node)

        if not nearest:
            log.warning("There are no known neighbors to set key %s",
                        dkey)
            return False

        spider = NodeSpiderCrawl(self.protocol, node, nearest,
                                    self.ksize, self.alpha)
        nodes = await spider.find()
        log.info("setting '%s' on %s", dkey, list(map(str, nodes)))
        log.debug("NODES SET DIGEST %s",nodes)

        biggest = max([n.distance_to(node) for n in nodes])
        if self.node.distance_to(node) < biggest:
            self.storage[dkey] = value
        results = [self.protocol.call_store(n, dkey, value) for n in nodes]
        return any(await asyncio.gather(*results))

    async def set_refresh(self, dkey, value):
        """
        Asigna la clave SHA1 dada (bytes) al valor dado en la red.
        """
        node = Node(dkey)

        nearest = self.protocol.router.find_neighbors(node)
        
        if not nearest:
            log.warning("There are no known neighbors to set key %s",
                        dkey)
            return False

        spider = NodeSpiderCrawl(self.protocol, node, nearest,
                                self.ksize, self.alpha)
        nodes = await spider.find()
        log.info("setting '%s' on %s", dkey, list(map(str, nodes)))
        log.debug("NODES SET DIGEST %s",nodes)

        results = [self.protocol.call_refresh(n, dkey, value) for n in nodes]
        return any(await asyncio.gather(*results))

    def save_state(self, fname):
        """
        Guarda el estado de este nodo (alfa/ksize/id/vecinos inmediatos)
        en un archivo de caché con el nombre dado fname.
        """
        log.info("Saving state to %s", fname)
        data = {
            'ksize': self.ksize,
            'alpha': self.alpha,
            'id': self.node.id,
            'neighbors': self.bootstrappable_neighbors()
        }
        if not data['neighbors']:
            log.warning("No known neighbors, so not writing to cache.")
            return
        with open(fname, 'wb') as file:
            pickle.dump(data, file)

    @classmethod
    async def load_state(cls, fname, port, interface='0.0.0.0'):
        """
        Carga el estado de este nodo (alfa/ksize/id/vecinos inmediatos)
        desde un archivo de caché con el nombre dado fname y luego inicia el nodo
        (usando el puerto/interfaz dado para comenzar a escuchar/iniciar).
        """
        log.info("Loading state from %s", fname)
        with open(fname, 'rb') as file:
            data = pickle.load(file)
        svr = cls(data['ksize'], data['alpha'], data['id'])
        await svr.listen(port, interface)
        if data['neighbors']:
            await svr.bootstrap(data['neighbors'])
        return svr

    def save_state_regularly(self, fname, frequency=600):
        """
        Guarda el estado del nodo con una regularidad dada en el archivo dado.

        Args:
            fname: Nombre de archivo para guardar regularmente
            frequency: Frecuencia en segundos con la que se debe guardar el estado.
                        De forma predeterminada, 10 minutos.
        """
        self.save_state(fname)
        loop = asyncio.get_event_loop()
        self.save_state_loop = loop.call_later(frequency,
                                                self.save_state_regularly,
                                                fname,
                                                frequency)


def check_dht_value_type(value):
    """
    Comprueba si el tipo del valor es un tipo válido para
    colocar en el DHT.
    """
    typeset = [
        int,
        float,
        bool,
        str,
        bytes,
        dict
    ]
    return type(value) in typeset 
