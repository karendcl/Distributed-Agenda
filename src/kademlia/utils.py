"""
General catchall for functions that don't make sense as methods.
"""
import hashlib
import operator
import asyncio


async def gather_dict(dic):
    """
    Combina los resultados de varias tareas asíncronas en un diccionario.

    Args:
        dic: Un diccionario donde las claves son las llaves del diccionario resultante y los valores son las tareas asíncronas.

    Returns:
        Un diccionario donde las claves son las mismas que las claves de `dic` y los valores son los resultados de las tareas asíncronas.
    """
    cors = list(dic.values())
    results = await asyncio.gather(*cors)
    return dict(zip(dic.keys(), results))


def digest(string):
    """
    Calcula el hash SHA1 de una cadena o bytes.

    Args:
        string: La cadena o bytes para los que se calculará el hash.

    Returns:
        La huella digital SHA1 de la cadena o bytes como una cadena hexadecimal.
    """
    if not isinstance(string, bytes):
        string = str(string).encode('utf8')
    return hashlib.sha1(string).hexdigest()


def digest_lid(string):
    """
    Calcula la huella digital SHA1 de una cadena o bytes.

    Args:
        string: La cadena o bytes para los que se calculará la huella digital.

    Returns:
        La huella digital SHA1 de la cadena o bytes como bytes.
    """
    if not isinstance(string, bytes):
        string = str(string).encode('utf8')
    return hashlib.sha1(string).digest()


def shared_prefix(args):
    """
    Encuentra el prefijo común entre las cadenas dadas.

    Por ejemplo:

        shared_prefix(['blahblah', 'blahwhat'])

    Devuelve 'blah'.
    """
    i = 0
    while i < min(map(len, args)):
        if len(set(map(operator.itemgetter(i), args))) != 1:
            break
        i += 1
    return args[0][:i]


def bytes_to_bit_string(bites):
    """
    Convierte una secuencia de bytes a una cadena de bits.

    Args:
        bites: La secuencia de bytes para convertir.

    Returns:
        Una cadena que representa la secuencia de bytes como bits.
    """
    bits = [bin(bite)[2:].rjust(8, '0') for bite in bites]
    return "".join(bits)



