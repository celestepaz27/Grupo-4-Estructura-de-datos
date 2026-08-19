from abc import ABC
from datetime import datetime
from typing import Optional
import re


class Usuario(ABC):
    """Clase abstracta base para los usuarios del sistema"""

    def __init__(self, nombre: str, apellido: str, clave: str, correo: str, id_usuario: int = -1):
        self._id_usuario = id_usuario
        self.nombre = nombre
        self.apellido = apellido

        self._clave = clave.strip()

        if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", correo.strip()):
            raise ValueError("El correo es inválido. Debe contener @ y la extensión final del dominio del correo.")

        self._correo = correo.strip()

    @property
    def id_usuario(self) -> int:
        return self._id_usuario

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not valor.strip():
            raise ValueError("El nombre del usuario no puede estar vacío.")
        self._nombre = valor.strip()

    @property
    def apellido(self) -> str:
        return self._apellido

    @apellido.setter
    def apellido(self, valor: str) -> None:
        if not valor.strip():
            raise ValueError("El apellido del usuario no puede estar vacío.")
        self._apellido = valor.strip()

    @property
    def clave(self) -> str:
        return self._clave

    @property
    def correo(self) -> str:
        return self._correo


class Bibliotecario(Usuario):
    def __init__(self, nombre: str, apellido: str, clave: str, correo: str, id_usuario: int = -1):
        super().__init__(nombre, apellido, clave, correo, id_usuario=id_usuario)


class Lector(Usuario):
    def __init__(self, nombre: str, apellido: str, clave: str, correo: str, id_usuario: int = -1):
        super().__init__(nombre, apellido, clave, correo, id_usuario=id_usuario)


class Sesion:
    """Clase que representa a las sesiones dentro del sistema."""

    def __init__(self, usuario: Usuario):
        self.__usuario = usuario
        self.__fecha_inicio = None
        self.__activa = False

    @property
    def usuario(self) -> Usuario:
        return self.__usuario

    @property
    def fecha_inicio(self) -> Optional[datetime]:
        return self.__fecha_inicio

    @property
    def activa(self) -> bool:
        return self.__activa

    def iniciar_sesion(self) -> None:
        self.__activa = True
        self.__fecha_inicio = datetime.now()

    def cerrar_sesion(self) -> None:
        self.__activa = False

    def esta_activa(self) -> bool:
        return self.__activa
