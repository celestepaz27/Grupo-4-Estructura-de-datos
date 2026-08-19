from abc import ABC
from acceso_datos.conexion_db import Database


class Repositorio(ABC):
    """Clase abstracta base para todos los repositorios del sistema"""

    def __init__(self, database: Database):
        self._database = database
