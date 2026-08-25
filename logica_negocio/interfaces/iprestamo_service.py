from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime, timedelta
from logica_negocio.estructuras import DoublyLinkedList
from acceso_datos import Usuario, Libro, Prestamo, EstadoPrestamo


class IPrestamoService(ABC):
    """Interfaz de las capacidades que puede ejecutar el service de Préstamos."""

    @abstractmethod
    async def registrar_prestamo(self, usuario: Usuario, libro: Libro) -> Prestamo: pass

    @abstractmethod
    async def devolver_prestamo(self, id: int) -> None: pass

    @abstractmethod
    async def consultar_prestamo_por_ID(self, id: int) -> Optional[Prestamo]: pass

    @abstractmethod
    async def consultar_prestamos_por_usuario(self, id_usuario: int) -> DoublyLinkedList[Prestamo]: pass

    @abstractmethod
    async def consultar_prestamos_por_libro(self, isbn_libro: str) -> DoublyLinkedList[Prestamo]: pass

    @abstractmethod
    async def consultar_prestamos_activos(self) -> DoublyLinkedList[Prestamo]: pass

    @abstractmethod
    async def consultar_prestamos_vencidos(self) -> DoublyLinkedList[Prestamo]: pass

    @abstractmethod
    async def consultar_prestamos_activos_por_usuario(self, id_usuario: int) -> DoublyLinkedList[Prestamo]: pass

    @abstractmethod
    async def consultar_prestamos_vencidos_por_usuario(self, id_usuario: int) -> DoublyLinkedList[Prestamo]: pass

    @abstractmethod
    async def consultar_prestamos_activos_por_libro(self, isbn_libro: str) -> DoublyLinkedList[Prestamo]: pass

    @abstractmethod
    async def consultar_prestamos_vencidos_por_libro(self, isbn_libro: str) -> DoublyLinkedList[Prestamo]: pass

    @abstractmethod
    async def consultar_prestamo_activo_por_libro_y_usuario(self, id_usuario: int, isbn_libro: str) -> Optional[Prestamo]: pass

    @abstractmethod
    async def consultar_prestamo_activo_por_ejemplar(self, id_ejemplar: int) -> Optional[Prestamo]: pass

    @abstractmethod
    def consultar_prestamos(self) -> DoublyLinkedList[Prestamo]: pass

    @abstractmethod
    async def modificar_fecha_vencimiento_prestamo(self, id: int, fecha: datetime) -> int: pass

    @abstractmethod
    async def actualizar_estado_prestamo(self, id: int, estado: EstadoPrestamo) -> int: pass

    @abstractmethod
    async def existen_prestamos_vencidos_para_usuario(self, id_usuario: int) -> bool: pass

    @abstractmethod
    async def validar_elegibilidad_usuario(self, id_usuario: int) -> bool: pass

    @abstractmethod
    async def validar_disponibilidad_libro(self, isbn_libro: str) -> bool: pass

    @abstractmethod
    async def obtener_plazo_actual_prestamo(self, id: int, id_usuario: int) -> timedelta: pass

    @abstractmethod
    async def _cargar_prestamos(self) -> None: pass
