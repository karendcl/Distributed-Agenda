from collections import Counter
import logging

from kademlia.node import Node, NodeHeap
from kademlia.utils import gather_dict


log = logging.getLogger(__name__)  


class SpiderCrawl:
    """
    Rastrea la red Kademlia en busca de claves de 160 bits.
    """

    def __init__(self, protocol, node, peers, ksize, alpha):
        """
        Crea un nuevo objeto SpiderCrawl para rastrear la red Kademlia.

        Args:
            protocol: Una instancia del protocolo Kademlia.
            node: Un nodo que representa la clave que se está buscando.
            peers: Una lista de nodos que se utilizan como punto de entrada a la red.
            ksize: El valor de k para el conjunto de nodos más cercanos.
            alpha: El valor de alpha para el número de nodos contactados por iteración.
        """

        self.protocol = protocol
        self.ksize = ksize
        self.alpha = alpha
        self.node = node
        self.nearest = NodeHeap(self.node, self.ksize)
        self.last_ids_crawled = []
        log.info("creating spider with peers: %s", peers)
        self.nearest.push(peers)

    async def _find(self, rpcmethod):
        """
        Busca un valor o una lista de nodos.

        Args:
            rpcmethod: El método RPC a utilizar (por ejemplo, call_find_value o call_find_node).

        El proceso de búsqueda:
          1. Llama a find_* para los ALPHA nodos más cercanos que aún no han sido interrogados,
             agregando los resultados al conjunto actual de nodos más cercanos.
          2. El conjunto de nodos más cercanos debe llevar un registro de quién ha sido interrogado,
             ordenado por cercanía y manteniendo solo KSIZE nodos.
          3. Si el conjunto es el mismo que en la última iteración, la próxima llamada debe ser a todos los nodos que aún no han sido interrogados.
          4. Repite el proceso hasta que todos los nodos del conjunto más cercano hayan sido interrogados.
        """
        log.info("crawling network with nearest: %s", str(tuple(self.nearest)))
        count = self.alpha
        if self.nearest.get_ids() == self.last_ids_crawled:
            count = len(self.nearest)
        self.last_ids_crawled = self.nearest.get_ids()

        dicts = {}
        for peer in self.nearest.get_uncontacted()[:count]:
            dicts[peer.id] = rpcmethod(peer, self.node)
            self.nearest.mark_contacted(peer)
        found = await gather_dict(dicts)
        return await self._nodes_found(found)

    async def _nodes_found(self, responses):
        raise NotImplementedError


class ValueSpiderCrawl(SpiderCrawl):
    def __init__(self, protocol, node, peers, ksize, alpha):
        SpiderCrawl.__init__(self, protocol, node, peers, ksize, alpha)
        self.nearest_without_value = NodeHeap(self.node, 1)

    async def find(self):
        """
        Encuentra el valor solicitado o los nodos más cercanos.
        """
        return await self._find(self.protocol.call_find_value)

    async def _nodes_found(self, responses):
        """
        Maneja el resultado de una iteración de la búsqueda.
        """
        toremove = []
        found_values = []
        for peerid, response in responses.items():
            response = RPCFindResponse(response)
            if not response.happened():
                toremove.append(peerid)
            elif response.has_value():
                found_values.append(response.get_value())
            else:
                peer = self.nearest.get_node(peerid)
                self.nearest_without_value.push(peer)
                self.nearest.push(response.get_node_list())
        self.nearest.remove(toremove)

        if found_values:
            return await self._handle_found_values(found_values)
        if self.nearest.have_contacted_all():
            return None
        return await self.find()

    async def _handle_found_values(self, values):
        """
        Le informamos al nodo más cercano que *no* tenía
        el valor para almacenarlo.
        """
        log.debug(f'!!!!!!!!! VALUES !!!!!!!!!!!! {values}')
        value = max(values, key=lambda x: x[0])
            
        peer = self.nearest_without_value.popleft()
        if peer:
            await self.protocol.call_store(peer, self.node.id, value[1])
        return value


class NodeSpiderCrawl(SpiderCrawl):
    async def find(self):
        """
        Encuentra los nodos más cercanos.
        """
        return await self._find(self.protocol.call_find_node)

    async def _nodes_found(self, responses):
        """
        Maneja el resultado de una iteración de la búsqueda.
        """
        toremove = []
        for peerid, response in responses.items():
            response = RPCFindResponse(response)
            if not response.happened():
                toremove.append(peerid)
            else:
                self.nearest.push(response.get_node_list())
        self.nearest.remove(toremove)

        if self.nearest.have_contacted_all():
            return list(self.nearest)
        return await self.find()


class RPCFindResponse:
    def __init__(self, response):
        """
        Un wrapper para el resultado de una búsqueda RPC.

        Args:
            response: Tupla de (<respuesta recibida>, <valor>)
                      donde <valor> es una lista de tuplas si no se encontró o
                      un diccionario de {'valor': v} donde v es el valor deseado
        """
        self.response = response

    def happened(self):
        """
        ¿El otro host realmente respondió?
        """
        return self.response[0]

    def has_value(self):
        return isinstance(self.response[1], dict)

    def get_value(self):
        return self.response[1]['value']

    def get_node_list(self):
        """
        Obtener la lista de nodos en la respuesta.  Si no hay valor, se establece.
        """
        nodelist = self.response[1] or []
        return [Node(*nodeple) for nodeple in nodelist]
