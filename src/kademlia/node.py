from operator import itemgetter
import heapq
import logging
from kademlia.utils import digest_lid

log = logging.getLogger(__name__)  


class Node:
    """
    Representa un nodo en la red Kademlia.
    """

    def __init__(self, node_id, ip=None, port=None):
        """
        Crea una instancia de Node.

        Args:
            node_id (int): El ID del nodo.
            ip (str): La dirección IP del nodo (opcional).
            port (int): El puerto del nodo (opcional).
        """
        self.id = node_id  
        log.debug("NODE CREATED WITH ID: %s", self.id)
        self.ip = ip  
        self.port = port
        self.long_id = int(digest_lid(node_id).hex(), 16)
        log.debug("NODE'S LONG ID: %s", self.long_id)

    def same_home_as(self, node):
        """
        Verifica si este nodo comparte la misma dirección IP y puerto que otro nodo.
        """ 
        return self.ip == node.ip and self.port == node.port

    def distance_to(self, node):
        """
        Calcula la distancia XOR entre este nodo y otro nodo.
        """
        return self.long_id ^ node.long_id

    def __iter__(self):
        """
        Permite iterar sobre el nodo como una tupla (ID, IP, puerto).
        """
        return iter([self.id, self.ip, self.port])

    def __repr__(self):
        """
        Devuelve una representación de cadena del nodo.
        """
        return repr([self.long_id, self.ip, self.port])

    def __str__(self):
        """
        Devuelve una representación de cadena del nodo en formato IP:puerto.
        """
        return "%s:%s" % (self.ip, str(self.port))


class NodeHeap:
    """
    Un heap de nodos ordenados por distancia a un nodo dado.
    """

    def __init__(self, node, maxsize):
        """
        Constructor.

        Args:
            node: El nodo desde el cual se mide la distancia.
            maxsize: El tamaño máximo del montón.
        """
        self.node = node
        self.heap = []
        self.contacted = set()
        self.maxsize = maxsize

    def remove(self, peers):
        """
        Elimina una lista de IDs de nodos del heap. 
        """
        peers = set(peers)
        if not peers:
            return
        nheap = []
        for distance, node in self.heap:
            if node.id not in peers:
                heapq.heappush(nheap, (distance, node))
        self.heap = nheap

    def get_node(self, node_id):
        """
        Obtiene un nodo del montón por su ID.
        """
        for _, node in self.heap:
            if node.id == node_id:
                return node
        return None

    def have_contacted_all(self):
        """
        Verifica si todos los nodos del montón han sido contactados.
        """
        return len(self.get_uncontacted()) == 0

    def get_ids(self):
        """
        Obtiene una lista de los IDs de los nodos en el montón.
        """
        return [n.id for n in self]

    def mark_contacted(self, node):
        """
        Marca un nodo como contactado.
        """
        self.contacted.add(node.id)

    def popleft(self):
        """
        Elimina y devuelve el nodo más cercano al nodo actual.
        """
        return heapq.heappop(self.heap)[1] if self else None

    def push(self, nodes):
        """
        Agrega nodos al heap.

        Args:
            nodes: Un nodo o una lista de nodos.
        """
        if not isinstance(nodes, list):
            nodes = [nodes]

        for node in nodes:
            if node not in self:
                distance = self.node.distance_to(node)
                heapq.heappush(self.heap, (distance, node))

    def __len__(self):
        """
        Devuelve el tamaño del heap.
        """
        return min(len(self.heap), self.maxsize)

    def __iter__(self):
        """
        Permite iterar sobre los nodos del heap.
        """
        nodes = heapq.nsmallest(self.maxsize, self.heap)
        return iter(map(itemgetter(1), nodes))

    def __contains__(self, node):
        """
        Verifica si un nodo está presente en el heap.
        """
        for _, other in self.heap:
            if node.id == other.id:
                return True
        return False

    def get_uncontacted(self):
        """
        Obtiene una lista de los nodos en el heap que aún no han sido contactados.
        """
        return [n for n in self if n.id not in self.contacted]
