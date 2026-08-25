from abc import ABC, abstractmethod
from typing import Optional, List
from acceso_datos import Ejemplar, EstadoEjemplar


class IEjemplarService(ABC):
    """Interfaz de las capacidades que puede ejecutar el service de Ejemplares para las copias físicas de los libros."""

    @abstractmethod
    async def registrar_ejemplar(self, ejemplar: Ejemplar) -> int:
        pass

    @abstractmethod
    async def modificar_estado_ejemplar(self, id: int, estado: EstadoEjemplar) -> int:
        pass

    @abstractmethod
    async def eliminar_ejemplar(self, id: int) -> int:
        pass

    @abstractmethod
    async def consultar_ejemplar(self, id: int) -> Optional[Ejemplar]:
        pass

    @abstractmethod
    async def consultar_ejemplares_por_libro(self, isbn: str) -> List[Ejemplar]:
        pass

    @abstractmethod
    async def consultar_ejemplares_disponibles_por_libro(self, isbn: str) -> List[Ejemplar]:
        pass

    @abstractmethod
    async def obtener_primer_ejemplar_disponible(self, isbn: str) -> Optional[Ejemplar]:
        pass

    @abstractmethod
    async def existen_ejemplares_disponibles(self, isbn: str) -> bool:
        pass
