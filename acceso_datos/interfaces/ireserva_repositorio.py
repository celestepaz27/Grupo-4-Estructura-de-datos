from abc import ABC, abstractmethod
from typing import List, Optional
from acceso_datos.modelos import Reserva, EstadoReserva


class IReservaRepositorio(ABC):
    """Interfaz de las capacidades que puede ejecutar el repositorio de las reservas."""

    @abstractmethod
    async def registrar(self, reserva: Reserva) -> int:
        pass

    @abstractmethod
    async def consultar_por_ID(self, id: int) -> Optional[Reserva]:
        pass

    @abstractmethod
    async def consultar_todas(self) -> List[Reserva]:
        pass

    @abstractmethod
    async def consultar_pendientes(self) -> List[Reserva]:
        pass

    @abstractmethod
    async def consultar_primera_pendiente(self) -> Optional[Reserva]:
        pass

    @abstractmethod
    async def consultar_pendiente_por_libro_y_usuario(self, id_usuario: int, isbn_libro: str) -> Optional[Reserva]:
        pass

    @abstractmethod
    async def consultar_pendientes_por_libro(self, isbn_libro: str) -> List[Reserva]:
        pass

    @abstractmethod
    async def consultar_pendientes_por_usuario(self, id_usuario: int) -> List[Reserva]:
        pass

    @abstractmethod
    async def actualizar_estado(self, id: int, estado: EstadoReserva) -> int:
        pass
