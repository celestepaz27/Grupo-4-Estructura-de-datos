from abc import ABC, abstractmethod
from acceso_datos import Usuario, Sesion


class IAutenticacionService(ABC):
    """Interfaz de las capacidades que puede ejecutar el service de Autenticación."""

    @abstractmethod
    async def iniciar_sesion(self, correo: str, clave: str) -> Sesion:
        pass

    @abstractmethod
    def cerrar_sesion(self) -> None:
        pass

    @abstractmethod
    def obtener_sesion_actual(self) -> Sesion:
        pass

    @abstractmethod
    def obtener_usuario_autenticado(self) -> Usuario:
        pass

    @abstractmethod
    async def _validar_credenciales(self, correo: str, clave: str) -> bool:
        pass
