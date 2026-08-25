from abc import ABC, abstractmethod
from acceso_datos import Libro
from logica_negocio.estructuras import DoublyLinkedList


class IOrdenadorLibros(ABC):
    """
    Interfaz de las capacidades para ordenar una colección de libros en base a ciertos criterios.\n
    Aplica el algoritmo de quicksort en sus métodos.
    """

    @abstractmethod
    def ordenar_por_titulo(self) -> DoublyLinkedList[Libro]: pass

    @abstractmethod
    def ordenar_por_autor(self) -> DoublyLinkedList[Libro]: pass

    @abstractmethod
    def ordenar_por_ISBN(self) -> DoublyLinkedList[Libro]: pass

    @abstractmethod
    def ordenar_por_anio(self) -> DoublyLinkedList[Libro]: pass
