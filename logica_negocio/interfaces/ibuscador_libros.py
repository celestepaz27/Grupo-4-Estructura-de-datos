from abc import ABC, abstractmethod
from typing import Optional
from logica_negocio.estructuras import DoublyLinkedList
from acceso_datos import Libro


class IBuscadorLibros(ABC):
    """
    Interfaz de las capacidades para buscar en una colección de libros ORDENADA en base a ciertos criterios.\n
    Aplica el algoritmo de búsqueda binaria en sus métodos.
    """

    @abstractmethod
    def buscar_por_ISBN(self, isbn: str) -> Optional[Libro]: pass

    @abstractmethod
    def buscar_por_titulo(self, titulo: str) -> Optional[Libro]: pass

    @abstractmethod
    def buscar_por_autor(self, autor: str) -> DoublyLinkedList[Libro]: pass

    @abstractmethod
    def buscar_por_anio(self, anio: int) -> DoublyLinkedList[Libro]: pass
