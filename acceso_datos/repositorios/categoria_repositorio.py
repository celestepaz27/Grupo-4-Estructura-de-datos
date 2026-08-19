from typing import List, Optional
from .repositorio_generico import Repositorio
from acceso_datos.interfaces import ICategoriaRepositorio
from acceso_datos.modelos import Categoria
from acceso_datos.conexion_db import Database


class CategoriaRepositorio(Repositorio, ICategoriaRepositorio):
    """
    Implementación concreta del repositorio de categorias utilizando como estado interno 
    cualquier objeto que sea de la abstracción Database.
    """

    def __init__(self, database: Database):
        super().__init__(database)
        self.__TABLA = "Categoria"

    async def consultar_por_ID(self, id : int) -> Optional[Categoria]:
        """Método que busca una categoria por su ID y retorna una posible categoría si existe."""

        filtros = {"id_categoria": id}
        resultados = await self._database.leer(self.__TABLA, filtros)

        if not resultados:
            return None
            
        return self.__mapear_a_objeto(resultados[0])

    async def consultar_todas(self) -> List[Categoria]:
        """Método que busca todas las categorias existentes y las retorna."""

        resultados = await self._database.leer(self.__TABLA)

        return [self.__mapear_a_objeto(fila) for fila in resultados]

    def __mapear_a_objeto(self, fila: dict) -> Categoria:
        """Método privado que convierte cada fila de los resultados de la DB a un objeto Categoria real."""

        return Categoria(
            id_categoria=int(fila["id_categoria"]),
            nombre=fila["nombre"]
        )
