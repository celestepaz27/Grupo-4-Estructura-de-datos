from enum import Enum
from .libro import Libro


class EstadoEjemplar(Enum):
    DISPONIBLE = "DISPONIBLE"
    PRESTADO = "PRESTADO"
    DAÑADO = "DAÑADO"

class Ejemplar:
    """Clase que representa los ejemplares asociados a un libro."""

    def __init__(self, libro_asociado: Libro, estado: EstadoEjemplar, id_ejemplar: int = -1):
        self.__id_ejemplar = id_ejemplar
        self.__libro_asociado = libro_asociado
        self.estado = estado

    @property
    def id_ejemplar(self) -> int:
        return self.__id_ejemplar

    @property
    def libro_asociado(self) -> Libro:
        return self.__libro_asociado

    @property
    def estado(self) -> EstadoEjemplar:
        return self.__estado

    @estado.setter
    def estado(self, valor: EstadoEjemplar) -> None:
        if not isinstance(valor, EstadoEjemplar):
            raise TypeError("El estado debe ser una instancia de EstadoEjemplar (DISPONIBLE, PRESTADO, DAÑADO).")
        self.__estado = valor
