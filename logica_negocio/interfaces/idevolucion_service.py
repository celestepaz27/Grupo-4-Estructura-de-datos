from abc import ABC, abstractmethod
from typing import Optional, List
from acceso_datos import Devolucion


class IDevolucionService(ABC):
    """Interfaz de las capacidades que puede ejecutar el service de Devolucion."""

    @abstractmethod
    async def registrar_devolucion(self, devolucion: Devolucion) -> int:
        pass

    @abstractmethod
    async def obtener_devolucion_por_ID(self, id: int) -> Optional[Devolucion]:
        pass

    @abstractmethod
    async def obtener_devolucion_por_prestamo(self, id_prestamo: int) -> Optional[Devolucion]:
        pass

    @abstractmethod
    async def listar_devoluciones(self) -> List[Devolucion]:
        pass
