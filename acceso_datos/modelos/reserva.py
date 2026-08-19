from enum import Enum
from datetime import datetime
from .usuarios import Usuario
from .libro import Libro


class EstadoReserva(Enum):
    PENDIENTE = "PENDIENTE"
    ASIGNADA = "ASIGNADA"
    CANCELADA = "CANCELADA"


class Reserva:
    """Clase que representa a las reservas realizadas dentro del sistema."""

    def __init__(self, usuario_asociado: Usuario, libro_asociado: Libro, fecha_reserva: datetime, 
                 estado: EstadoReserva, id_reserva: int = -1):
        self.__id_reserva = id_reserva
        self.__usuario_asociado = usuario_asociado
        self.__libro_asociado = libro_asociado
        self.__fecha_reserva = fecha_reserva
        self.estado = estado

    @property
    def id_reserva(self) -> int:
        return self.__id_reserva

    @property
    def usuario_asociado(self) -> Usuario:
        return self.__usuario_asociado

    @property
    def libro_asociado(self) -> Libro:
        return self.__libro_asociado

    @property
    def fecha_reserva(self) -> datetime:
        return self.__fecha_reserva

    @property
    def estado(self) -> EstadoReserva:
        return self.__estado

    @estado.setter
    def estado(self, valor: EstadoReserva) -> None:
        if not isinstance(valor, EstadoReserva):
            raise TypeError("El estado debe ser una instancia de EstadoReserva (PENDIENTE, ASIGNADA, CANCELADA).")
        self.__estado = valor
