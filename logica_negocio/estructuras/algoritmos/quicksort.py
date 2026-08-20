from typing import List, Any, Callable, TypeVar

T = TypeVar('T')


def quicksort(lista: List[T], key: Callable[[T], Any] = lambda x: x) -> List[T]:
    """
    Ordena una lista utilizando el algoritmo Quicksort.\n
    :param lista: La lista de elementos a ordenar.\n
    :param key: Una función que extrae la propiedad de comparación (ej: lambda x: x.id_usuario).\n
    :return: Una nueva lista ordenada.
    """

    # Representa el caso base cuando ya la lista pasada como argumento posee 1 o no posee elementos.
    if len(lista) <= 1:
        return lista
    
    # Se elige el elemento central como pivote y se referencia según función la llave o key, el valor de ese pivote.
    pivote = lista[len(lista) // 2]
    valor_pivote = key(pivote)
    
    # Se particiona la lista en sublistas basándose en la función llave.
    izquierdos = [x for x in lista if key(x) < valor_pivote]
    centrales = [x for x in lista if key(x) == valor_pivote]
    derechos = [x for x in lista if key(x) > valor_pivote]
    
    # Se aplica recursión sobre las listas hasta que se llegue a listas con 1 o ningún elemento y se concatena los resultados.
    return quicksort(izquierdos, key) + centrales + quicksort(derechos, key)
