from abc import ABC, abstractmethod
from typing import Optional
from acceso_datos import Usuario
from logica_negocio.estructuras import DoublyLinkedList


class IUsuarioService(ABC):
    """Interfaz de las capacidades que puede ejecutar el service de Usuarios."""

    @abstractmethod
    async def registrar_usuario(self, usuario: Usuario) -> int:
        pass

    @abstractmethod
    async def eliminar_usuario(self, id: int) -> int:
        pass

    @abstractmethod
    async def consultar_usuario(self, id: int) -> Optional[Usuario]:
        pass

    @abstractmethod
    async def modificar_usuario(self, id: int, usuario_modificado: Usuario) -> int:
        pass

    @abstractmethod
    async def buscar_usuario_por_correo(self, correo: str) -> Optional[Usuario]:
        pass

    @abstractmethod
    async def existe_correo(self, correo: str) -> bool:
        pass

    @abstractmethod
    async def obtener_usuarios(self) -> DoublyLinkedList[Usuario]:
        pass

    @abstractmethod
    async def _cargar_usuarios_diccionario(self) -> None:
        pass
