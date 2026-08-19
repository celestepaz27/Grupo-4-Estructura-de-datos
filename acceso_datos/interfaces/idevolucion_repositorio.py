from abc import ABC, abstractmethod
from typing import List, Optional
from acceso_datos.modelos import Devolucion


class IDevolucionRepositorio(ABC):
    """Interfaz de las capacidades que puede ejecutar el repositorio de las devoluciones."""

    @abstractmethod
    async def registrar(self, devolucion: Devolucion) -> int:
        pass

    @abstractmethod
    async def consultar_por_ID(self, id: int) -> Optional[Devolucion]:
        pass

    @abstractmethod
    async def consultar_por_prestamo(self, id_prestamo: int) -> Optional[Devolucion]:
        pass

    @abstractmethod
    async def consultar_todas(self) -> List[Devolucion]:
        pass
