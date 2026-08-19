from enum import Enum
from datetime import datetime
from typing import Optional
from .usuarios import Usuario
from .ejemplar import Ejemplar


class EstadoPrestamo(Enum):
    ACTIVO = "ACTIVO"
    VENCIDO = "VENCIDO"
    FINALIZADO = "FINALIZADO"


class Prestamo:
    """Clase que representa a los préstamos solicitados por los usuarios."""

    def __init__(self, usuario_asociado: Usuario, ejemplar_asociado: Ejemplar, fecha_prestamo: datetime, 
                 fecha_vencimiento: datetime, estado: EstadoPrestamo, id_prestamo: int = -1):
        
        self.__id_prestamo = id_prestamo
        self.__usuario_asociado = usuario_asociado
        self.__ejemplar_asociado = ejemplar_asociado
        self.__fecha_prestamo = fecha_prestamo
        self.fecha_vencimiento = fecha_vencimiento    
        self.__fecha_devolucion = None
        self.estado = estado

    @property
    def id_prestamo(self) -> int:
        return self.__id_prestamo

    @property
    def usuario_asociado(self) -> Usuario:
        return self.__usuario_asociado

    @property
    def ejemplar_asociado(self) -> Ejemplar:
        return self.__ejemplar_asociado

    @property
    def fecha_prestamo(self) -> datetime:
        return self.__fecha_prestamo

    @property
    def fecha_vencimiento(self) -> datetime:
        return self.__fecha_vencimiento

    @fecha_vencimiento.setter
    def fecha_vencimiento(self, valor: datetime) -> None:
        if self.__fecha_prestamo >= valor:
            raise ValueError("La fecha de vencimiento debe ser posterior a la del inicio del préstamo.")
        self.__fecha_vencimiento = valor

    @property
    def fecha_devolucion(self) -> Optional[datetime]:
        return self.__fecha_devolucion

    @fecha_devolucion.setter
    def fecha_devolucion(self, valor: datetime) -> None:
        if self.__fecha_prestamo >= valor:
            raise ValueError("La fecha de devolución debe ser posterior a la del inicio del préstamo.")
        self.__fecha_devolucion = valor

    @property
    def estado(self) -> EstadoPrestamo:
        return self.__estado

    @estado.setter
    def estado(self, valor: EstadoPrestamo) -> None:
        if not isinstance(valor, EstadoPrestamo):
            raise TypeError("El estado debe ser una instancia de EstadoPrestamo (ACTIVO, VENCIDO, FINALIZADO).")
        self.__estado = valor
