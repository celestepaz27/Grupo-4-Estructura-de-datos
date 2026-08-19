from abc import ABC, abstractmethod
from typing import List, Optional
from acceso_datos.modelos import Usuario


class IUsuarioRepositorio(ABC):
    """Interfaz de las capacidades que puede ejecutar el repositorio de usuarios."""

    @abstractmethod
    async def registrar(self, usuario: Usuario) -> int:
        pass

    @abstractmethod
    async def consultar_por_ID(self, id: int) -> Optional[Usuario]:
        pass

    @abstractmethod
    async def consultar_por_correo(self, correo: str) -> Optional[Usuario]:
        pass

    @abstractmethod
    async def consultar_todos(self) -> List[Usuario]:
        pass

    @abstractmethod
    async def actualizar(self, id: int, usuario: Usuario) -> int:
        pass

    @abstractmethod
    async def eliminar(self, id: int) -> int:
        pass
