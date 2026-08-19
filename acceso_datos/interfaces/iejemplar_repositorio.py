from abc import ABC, abstractmethod
from typing import List, Optional
from acceso_datos.modelos import Ejemplar, EstadoEjemplar


class IEjemplarRepositorio(ABC):
    """Interfaz de las capacidades que puede ejecutar el repositorio de ejemplares."""

    @abstractmethod
    async def registrar(self, ejemplar: Ejemplar) -> int:
        pass

    @abstractmethod
    async def consultar_por_ID(self, id: int) -> Optional[Ejemplar]:
        pass

    @abstractmethod
    async def consultar_por_libro(self, isbn_libro: str) -> List[Ejemplar]:
        pass

    @abstractmethod
    async def consultar_disponibles_por_libro(self, isbn_libro: str) -> List[Ejemplar]:
        pass

    @abstractmethod
    async def actualizar_estado(self, id: int, estado: EstadoEjemplar) -> int:
        pass

    @abstractmethod
    async def eliminar(self, id: int) -> int:
        pass
