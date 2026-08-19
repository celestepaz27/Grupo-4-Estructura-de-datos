from .prestamo import Prestamo
from datetime import datetime


class Devolucion:
    """Clase que representa a las devoluciones de los libros por medio de sus préstamos."""

    def __init__(self, prestamo_asociado: Prestamo, fecha_devolucion_real: datetime, descripcion: str, id_devolucion: int = -1):
        self.__id_devolucion = id_devolucion
        self.__prestamo_asociado = prestamo_asociado

        if prestamo_asociado.fecha_prestamo >= fecha_devolucion_real:
            raise ValueError("La fecha de devolución real debe ser posterior a la del inicio del préstamo.")

        self.__fecha_devolucion_real = fecha_devolucion_real
        self.descripcion = descripcion

    @property
    def id_devolucion(self) -> int:
        return self.__id_devolucion

    @property
    def prestamo_asociado(self) -> Prestamo:
        return self.__prestamo_asociado

    @property
    def fecha_devolucion_real(self) -> datetime:
        return self.__fecha_devolucion_real

    @property
    def descripcion(self) -> str:
        return self.__descripcion

    @descripcion.setter
    def descripcion(self, valor: str) -> None:
        if not valor.strip():
            raise ValueError("La descripción no puede estar vacia.")
        self.__descripcion = valor.strip()
