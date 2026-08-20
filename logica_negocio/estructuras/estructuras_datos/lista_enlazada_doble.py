from typing import List, Optional, TypeVar, Generic

T = TypeVar('T')


class NodoDoble(Generic[T]):
    """
    Clase que representa a cada nodo que formara parte de una lista enlazada doble (DoublyLinkedList[T]). 
    Cada nodo es representado por NodoDoble[T].
    """

    def __init__(self, dato: T):
        self.dato: T = dato
        self.anterior: Optional['NodoDoble[T]'] = None
        self.siguiente: Optional['NodoDoble[T]'] = None

    @property
    def dato(self) -> T:
        return self.__dato

    @dato.setter
    def dato(self, valor: T) -> None:
        self.__dato = valor

    @property
    def anterior(self) -> Optional['NodoDoble[T]']:
        return self.__anterior

    @anterior.setter
    def anterior(self, nodo: Optional['NodoDoble[T]']) -> None:
        self.__anterior = nodo

    @property
    def siguiente(self) -> Optional['NodoDoble[T]']:
        return self.__siguiente

    @siguiente.setter
    def siguiente(self, nodo: Optional['NodoDoble[T]']) -> None:
        self.__siguiente = nodo


class DoublyLinkedList(Generic[T]):
    """
    Clase que representa una lista enlazada doble la cual recibe en su estructura varios objetos de tipo NodoDoble[T]. 
    Cada lista enlazada doble es representada por DoublyLinkedList[T].
    """

    def __init__(self):
        self.__cabeza: Optional[NodoDoble[T]] = None
        self.__cola: Optional[NodoDoble[T]] = None
        self.__tamanio: int = 0

    def esta_vacia(self) -> bool:
        """Método que retorna si la lista enlazada doble esta vacía o no."""
        return self.__tamanio == 0

    def obtener_tamanio(self) -> int:
        """Método que retorna el tamaño actual de la lista enlazada doble."""
        return self.__tamanio

    def insertar_al_inicio(self, valor: T) -> NodoDoble[T]:
        """
        Método que agrega un elemento al inicio de la lista enlazada doble.
        Retorna el nodo creado si fue agregado a la colección con éxito.
        """

        nuevo_nodo = NodoDoble(valor)
        if self.esta_vacia():
            self.__cabeza = nuevo_nodo
            self.__cola = nuevo_nodo
        else:
            self.__conectar(nuevo_nodo, self.__cabeza)
            self.__cabeza = nuevo_nodo
        self.__tamanio += 1
        return nuevo_nodo

    def insertar_al_final(self, valor: T) -> NodoDoble[T]:
        """
        Método que agrega un elemento al final de la lista enlazada doble.
        Retorna el nodo creado si fue agregado a la colección con éxito.
        """
                
        nuevo_nodo = NodoDoble(valor)
        if self.esta_vacia():
            self.__cabeza = nuevo_nodo
            self.__cola = nuevo_nodo
        else:
            self.__conectar(self.__cola, nuevo_nodo)
            self.__cola = nuevo_nodo
        self.__tamanio += 1
        return nuevo_nodo

    def eliminar(self, valor: T) -> bool:
        """
        Método que elimina un elemento de la lista enlazada doble. 
        Devuelve true si fue eliminado o false si no fue así.
        """

        nodo = self.__buscar_nodo(valor)

        if not nodo:
            return False
        
        self.__desconectar(nodo)
        self.__tamanio -= 1
        return True

    def buscar(self, valor: T) -> Optional[NodoDoble[T]]:
        """
        Método que busca un elemento dentro de la lista enlazada doble. 
        Devuelve el nodo especifico con su valor si fue encontrado, si no devuelve None.
        """

        return self.__buscar_nodo(valor)

    def recorrer_adelante(self) -> List[T]:
        """
        Método que recorre todos los elementos desde la cabeza para adelante dentro de la lista enlazada doble. 
        Devuelve una lista normal con todos los elementos conectados.
        """

        elementos = []
        actual = self.__cabeza
        while actual:
            elementos.append(actual.dato)
            actual = actual.siguiente
        return elementos

    def recorrer_atras(self) -> List[T]:
        """
        Método que recorre todos los elementos desde la cola para atrás dentro de la lista enlazada doble. 
        Devuelve una lista normal con todos los elementos conectados.
        """

        elementos = []
        actual = self.__cola
        while actual:
            elementos.append(actual.dato)
            actual = actual.anterior
        return elementos

    def __buscar_nodo(self, valor: T) -> Optional[NodoDoble[T]]:
        """
        Método privado que consulta entre todos los elementos de la lista enlazada doble 
        si un nodo con el respectivo elemento existe. Devuelve un nodo especifico si existe, si no devuelve None.
        """

        actual = self.__cabeza
        while actual:
            if actual.dato == valor:
                return actual
            actual = actual.siguiente
        return None

    def __conectar(self, anterior: NodoDoble[T], siguiente: NodoDoble[T]) -> None:
        """
        Método privado que conecta dos nodos entre si en la lista enlazada doble.
        El nodo anterior adjuntado tendrá como su siguiente el nodo siguiente adjuntado.
        El nodo siguiente adjuntado tendrá como su anterior el nodo anterior adjuntado.
        """

        if anterior:
            anterior.siguiente = siguiente
        if siguiente:
            siguiente.anterior = anterior

    def __desconectar(self, nodo: NodoDoble[T]) -> None:
        """
        Método privado que elimina un nodo especifico de la lista enlazada doble y lo desconecta del flujo.
        """

        if nodo == self.__cabeza and nodo == self.__cola:
            self.__cabeza = None
            self.__cola = None
        elif nodo == self.__cabeza:
            self.__cabeza = nodo.siguiente
            if self.__cabeza:
                self.__cabeza.anterior = None
        elif nodo == self.__cola:
            self.__cola = nodo.anterior
            if self.__cola:
                self.__cola.siguiente = None
        else:
            anterior_nodo = nodo.anterior
            siguiente_nodo = nodo.siguiente
            if anterior_nodo:
                anterior_nodo.siguiente = siguiente_nodo
            if siguiente_nodo:
                siguiente_nodo.anterior = anterior_nodo
        
        nodo.anterior = None
        nodo.siguiente = None
