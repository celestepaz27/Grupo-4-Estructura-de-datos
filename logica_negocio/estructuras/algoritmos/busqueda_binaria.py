from typing import List, Any, Callable, TypeVar, Optional

T = TypeVar('T')


def busqueda_binaria(lista_ordenada: List[T], objetivo: Any, key: Callable[[T], Any] = lambda x: x) -> Optional[T]:
    """
    Busca un elemento en una lista PREVIAMENTE ORDENADA por Quicksort siguiendo el principio de "Divide y Vencerás".\n
    :param lista_ordenada: Lista donde se realizará la búsqueda.\n
    :param objetivo: El valor exacto que se busca en base a la propiedad que se quiere comparar (ej: un ID específico).\n
    :param key: Una función que extrae la propiedad de comparación de los objetos.\n
    :return: El objeto encontrado o None si no existe en la lista.\n
    """

    inicio = 0
    fin = len(lista_ordenada) - 1
    
    while inicio <= fin:
        medio = (inicio + fin) // 2
        valor_medio = key(lista_ordenada[medio])
        
        if valor_medio == objetivo:
            return lista_ordenada[medio]
        elif valor_medio < objetivo:
            inicio = medio + 1
        else:
            fin = medio - 1
            
    return None
