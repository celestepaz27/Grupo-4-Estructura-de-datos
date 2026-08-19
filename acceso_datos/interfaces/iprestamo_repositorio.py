from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from acceso_datos.modelos import Prestamo, EstadoPrestamo


class IPrestamoRepositorio(ABC):
    """Interfaz de las capacidades que puede ejecutar el repositorio de préstamos."""

    @abstractmethod
    async def registrar(self, prestamo: Prestamo) -> int:
        pass

    @abstractmethod
    async def consultar_por_ID(self, id: int) -> Optional[Prestamo]:
        pass

    @abstractmethod
    async def consultar_todos_por_usuario(self, id_usuario: int) -> List[Prestamo]:
        pass

    @abstractmethod
    async def consultar_todos_por_libro(self, isbn_libro: str) -> List[Prestamo]:
        pass

    @abstractmethod
    async def consultar_activos(self) -> List[Prestamo]:
        pass

    @abstractmethod
    async def consultar_vencidos(self) -> List[Prestamo]:
        pass

    @abstractmethod
    async def consultar_activos_por_usuario(self, id_usuario: int) -> List[Prestamo]:
        pass

    @abstractmethod
    async def consultar_vencidos_por_usuario(self, id_usuario: int) -> List[Prestamo]:
        pass

    @abstractmethod
    async def consultar_activos_por_libro(self, isbn_libro: str) -> List[Prestamo]:
        pass

    @abstractmethod
    async def consultar_vencidos_por_libro(self, isbn_libro: str) -> List[Prestamo]:
        pass

    @abstractmethod
    async def consultar_activo_por_usuario_y_id_libro(self, id_usuario: int, isbn_libro: str) -> Optional[Prestamo]:
        pass

    @abstractmethod
    async def consultar_activo_por_ejemplar(self, id_ejemplar: int) -> Optional[Prestamo]:
        pass

    @abstractmethod
    async def asignar_fecha_devolucion(self, id: int, fecha: datetime) -> int:
        pass

    @abstractmethod
    async def actualizar_fecha_vencimiento(self, id: int, fecha: datetime) -> int:
        pass

    @abstractmethod
    async def actualizar_estado(self, id: int, estado: EstadoPrestamo) -> int:
        pass
    