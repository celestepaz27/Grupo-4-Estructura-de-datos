from abc import ABC, abstractmethod
from typing import Optional
from logica_negocio.estructuras import DoublyLinkedList
from acceso_datos import Reserva, EstadoReserva


class IReservaService(ABC):
    """Interfaz de las capacidades que puede ejecutar el service de Reserva."""

    @abstractmethod
    async def registrar_reserva(self, reserva: Reserva) -> int: pass

    @abstractmethod
    async def cancelar_reserva(self, id: int) -> int: pass

    @abstractmethod
    async def procesar_siguiente_reserva_pendiente(self, isbn_libro: str) -> Optional[Reserva]: pass

    @abstractmethod
    async def consultar_reserva_por_ID(self, id: int) -> Optional[Reserva]: pass

    @abstractmethod
    async def consultar_reservas(self) -> DoublyLinkedList[Reserva]: pass

    @abstractmethod
    async def consultar_reservas_pendientes(self) -> DoublyLinkedList[Reserva]: pass

    @abstractmethod
    async def consultar_primera_reserva_pendiente(self) -> Optional[Reserva]: pass

    @abstractmethod
    async def consultar_reserva_pendiente_por_libro_y_usuario(self, id_usuario: int, isbn_libro: str) -> Optional[Reserva]: pass

    @abstractmethod
    async def consultar_reservas_pendientes_por_libro(self, isbn_libro: str) -> DoublyLinkedList[Reserva]: pass

    @abstractmethod
    async def consultar_reservas_pendientes_por_usuario(self, id_usuario: int) -> DoublyLinkedList[Reserva]: pass

    @abstractmethod
    async def actualizar_estado_reserva(self, id, estado: EstadoReserva) -> int: pass

    @abstractmethod
    async def existen_reservas_pendientes_para_libro(self, isbn_libro: str) -> bool: pass

    @abstractmethod
    async def existen_reservas_pendientes_para_usuario(self, id_usuario: int) -> bool: pass

    @abstractmethod
    async def _cargar_cola_reservas(self) -> None: pass
