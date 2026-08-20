from typing import Optional, TypeVar, Generic
from .lista_enlazada_doble import DoublyLinkedList

T = TypeVar('T')


class NodoCola(Generic[T]):
    """
    Clase que representa a cada nodo que formara parte de una cola (Cola[T]). 
    Cada nodo es representado por NodoCola[T].
    """

    def __init__(self, dato: T):
        self.dato: T = dato
        self.siguiente: Optional['NodoCola[T]'] = None

    @property
    def dato(self) -> T:
        return self.__dato

    @dato.setter
    def dato(self, valor: T) -> None:
        self.__dato = valor

    @property
    def siguiente(self) -> Optional['NodoCola[T]']:
        return self.__siguiente

    @siguiente.setter
    def siguiente(self, nodo: Optional['NodoCola[T]']) -> None:
        self.__siguiente = nodo


class Cola(Generic[T]):
    """
    Clase que representa una cola la cual recibe en su estructura varios objetos de tipo NodoCola[T]. 
    Cada cola es representada por Cola[T].
    """

    def __init__(self):
        self.__frente: Optional[NodoCola[T]] = None
        self.__final: Optional[NodoCola[T]] = None
        self.__tamanio: int = 0

    def esta_vacia(self) -> bool:
        """Método que retorna si la cola esta vacía o no."""
        return self.__tamanio == 0

    def obtener_tamanio(self) -> int:
        """Método que retorna el tamaño actual de la cola."""
        return self.__tamanio

    def obtener_frente(self) -> T:
        """
        Método que retorna el actual elemento que está en primer fila de espera.
        """
                
        if self.esta_vacia():
            raise IndexError("La cola está vacía.")
        return self.__frente.dato

    def encolar(self, valor: T) -> None:
        """
        Método que agrega o encola un elemento al final de la colección.
        """
                
        nuevo_nodo = NodoCola(valor)
        if self.esta_vacia():
            self.__frente = nuevo_nodo
            self.__final = nuevo_nodo
        else:
            if self.__final:
                self.__final.siguiente = nuevo_nodo
            self.__final = nuevo_nodo
        self.__tamanio += 1

    def desencolar(self) -> T:
        """
        Método que elimina o extrae el elemento que está al frente en la colección. 
        En otras palabras, el primer elemento actual en espera es borrado, el cual este será retornado.
        """

        if self.esta_vacia():
            raise IndexError("No se puede desencolar de una estructura vacía.")
        
        valor = self.__frente.dato
        self.__frente = self.__frente.siguiente
        
        if self.__frente is None:
            self.__final = None
            
        self.__tamanio -= 1
        return valor

    def obtener_todos(self) -> DoublyLinkedList[T]:
        """
        Método que exporta los elementos actuales de la cola (Cola[T]) a una lista enlazada doble (DoublyLinkedList[T]).
        Se devuelve una DoublyLinkedList[T] con todos los elementos de cola.
        """

        lista_doble = DoublyLinkedList[T]()
        actual = self.__frente
        while actual:
            lista_doble.insertar_al_final(actual.dato)
            actual = actual.siguiente
        return lista_doble
