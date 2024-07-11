import heapq
import time
import operator
import asyncio
import logging

from itertools import chain
from collections import OrderedDict
from kademlia.utils import shared_prefix, bytes_to_bit_string

log = logging.getLogger(__name__)

class KBucket:
    """
    Representa un bucket en la tabla de enrutamiento.
    """

    def __init__(self, rangeLower, rangeUpper, ksize, replacementNodeFactor=5):
        """
        Crea una nueva instancia de `KBucket`.

        Args:
            rangeLower: El límite inferior del rango del bucket.
            rangeUpper: El límite superior del rango del bucket.
            ksize: El valor de k para el número máximo de nodos en el bucket.
            replacementNodeFactor: El factor de multiplicación para el número máximo de nodos de reemplazo.
        """
        self.range = (rangeLower, rangeUpper)
        self.nodes = OrderedDict()
        self.replacement_nodes = OrderedDict()
        self.touch_last_updated()
        self.ksize = ksize
        self.max_replacement_nodes = self.ksize * replacementNodeFactor

    def touch_last_updated(self):
        """
        Actualiza la marca de tiempo de la última actualización del bucket.
        """
        self.last_updated = time.monotonic()

    def get_nodes(self):
        """
        Obtiene una lista de los nodos en el bucket.
        """
        return list(self.nodes.values())

    def split(self):
        """
        Divide el bucket en dos buckets más pequeños.
        """
        midpoint = (self.range[0] + self.range[1]) // 2
        one = KBucket(self.range[0], midpoint, self.ksize)
        two = KBucket(midpoint + 1, self.range[1], self.ksize)
        nodes = chain(self.nodes.values(), self.replacement_nodes.values())
        
        for node in nodes:
            bucket = one if node.long_id <= midpoint else two
            bucket.add_node(node)

        return (one, two)

    def remove_node(self, node):
        """
        Elimina un nodo del bucket.
        """
        if node.id in self.replacement_nodes:
            del self.replacement_nodes[node.id]

        if node.id in self.nodes:
            del self.nodes[node.id]

            if self.replacement_nodes:
                newnode_id, newnode = self.replacement_nodes.popitem()
                self.nodes[newnode_id] = newnode

    def has_in_range(self, node):
        """
        Verifica si un nodo está dentro del rango del bucket.
        """
        return self.range[0] <= node.long_id <= self.range[1]

    def is_new_node(self, node):
        """
        Verifica si un nodo es nuevo en el bucket.
        """
        for n in self.get_nodes():
            if node.id == n.id and n.port == node.port:
                return False
        return True

    def add_node(self, node):
        """
        Agrega un nodo al bucket. Devuelve True si la operación fue exitosa,
        False si el bucket está lleno.

        Si el bucket está lleno, se mantiene un registro del nodo en una lista de reemplazo (segun el 
        paper de Kademlia).
        """
        
        if node.id in self.nodes:
            log.debug("NODE %s ALREADY IN BUCKET", node)
            del self.nodes[node.id]
            self.nodes[node.id] = node
        elif len(self) < self.ksize:
            self.nodes[node.id] = node
        else:
            if node.id in self.replacement_nodes:
                del self.replacement_nodes[node.id]
            self.replacement_nodes[node.id] = node
            while len(self.replacement_nodes) > self.max_replacement_nodes:
                self.replacement_nodes.popitem(last=False)
            return False
        return True

    def depth(self):
        """
        Calcula la profundidad del bucket, es decir, la cantidad de prefijos compartidos
        entre los IDs de los nodos.
        """
        vals = self.nodes.values()
        log.debug("vals in depth function KBUCKET: %s", vals)
        sprefix = shared_prefix([bytes_to_bit_string(n.id) for n in vals])
        return len(sprefix)

    def head(self):
        """
        Obtiene el nodo más cercano al inicio del rango del bucket.
        """
        return list(self.nodes.values())[0]

    def __getitem__(self, node_id):
        """
        Obtiene un nodo del bucket por su ID.
        """
        return self.nodes.get(node_id, None)

    def __len__(self):
        """
        Devuelve el número de nodos en el bucket.
        """
        return len(self.nodes)



class RoutingTable:
    """
    Gestiona la tabla de enrutamiento de un nodo Kademlia.
    """
    def __init__(self, protocol, ksize, node):
        """
        Inicializa la tabla de enrutamiento.

        Args:
            protocol: Una instancia del protocolo Kademlia.
            ksize: El valor de k para cada bucket.
            node: El nodo actual.
        """
        self.node = node
        self.protocol = protocol
        self.ksize = ksize
        self.flush()

    def flush(self):
        """
        Limpia la tabla de enrutamiento.
        """
        self.buckets = [KBucket(0, 2 ** 160, self.ksize)]

    def split_bucket(self, index):
        """
        Divide un bucket en dos buckets más pequeños.
        """
        one, two = self.buckets[index].split()
        self.buckets[index] = one
        self.buckets.insert(index + 1, two)

    def lonely_buckets(self):
        """
        Obtiene todos los buckets que no se han actualizado en más de una hora.
        """
        hrago = time.monotonic() - 10
        return [b for b in self.buckets if b.last_updated < hrago]

    def remove_contact(self, node):
        """
        Elimina un nodo de la tabla de enrutamiento.
        """
        index = self.get_bucket_for(node)
        self.buckets[index].remove_node(node)

    def is_new_node(self, node):
        """
        Verifica si un nodo es nuevo en la tabla de enrutamiento.
        """
        index = self.get_bucket_for(node)
        return self.buckets[index].is_new_node(node)

    def add_contact(self, node):
        """
        Agrega un nodo a la tabla de enrutamiento.
        """
        index = self.get_bucket_for(node)
        bucket = self.buckets[index]

        if bucket.add_node(node):
            return
        
        if bucket.has_in_range(self.node) or bucket.depth() % 5 != 0:
            self.split_bucket(index)
            self.add_contact(node)
        else:
            asyncio.ensure_future(self.protocol.call_ping(bucket.head()))

    def get_bucket_for(self, node):
        """
        Obtiene el índice del bucket al que pertenece un nodo dado.
        """
        for index, bucket in enumerate(self.buckets):
            if node.long_id < bucket.range[1]:
                return index
        return None

    def find_neighbors(self, node, k=None, exclude=None):
        """
        Encuentra los k nodos más cercanos a un nodo dado.
        """
        k = k or self.ksize
        nodes = []
        for neighbor in TableTraverser(self, node):
            notexcluded = exclude is None or not neighbor.same_home_as(exclude)
            if neighbor.id != node.id and notexcluded:
                heapq.heappush(nodes, (node.distance_to(neighbor), neighbor))
            if len(nodes) == k:
                break

        return list(map(operator.itemgetter(1), heapq.nsmallest(k, nodes)))
    
    
class TableTraverser:
    """
    Iterador para recorrer la tabla de enrutamiento.
    """
    def __init__(self, table : RoutingTable, startNode):
        """
        Inicializa el iterador.

        Args:
            table: La tabla de enrutamiento.
            startNode: El nodo de inicio para la búsqueda.
        """ 
        index = table.get_bucket_for(startNode)
        table.buckets[index].touch_last_updated()
        self.current_nodes = table.buckets[index].get_nodes()
        self.left_buckets = table.buckets[:index]
        self.right_buckets = table.buckets[(index + 1):]
        self.left = True

    def __iter__(self):
        return self

    def __next__(self):
        """
        Devuelve el siguiente nodo de la tabla de enrutamiento.
        """
        if self.current_nodes:
            return self.current_nodes.pop()

        if self.left and self.left_buckets:
            self.current_nodes = self.left_buckets.pop().get_nodes()
            self.left = False
            return next(self)

        if self.right_buckets:
            self.current_nodes = self.right_buckets.pop(0).get_nodes()
            self.left = True
            return next(self)

        raise StopIteration

