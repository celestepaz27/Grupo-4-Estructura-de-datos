from typing import Optional, List
from logica_negocio.interfaces import ICategoriaService
from acceso_datos import ICategoriaRepositorio, Categoria


class CategoriaService(ICategoriaService):
    """Implementación concreta del servicio de categorias."""

    def __init__(self, categoria_repositorio: ICategoriaRepositorio):
        self.__categoria_repositorio = categoria_repositorio

    async def consultar_categoria(self, id: int) -> Optional[Categoria]:
        """
        Método que consulta en el repositorio de categorias sobre la existencia de una categoría por su ID.\n
        Si existe devuelve ese registro en un objeto de tipo Categoria, si no es así, se devuelve None.
        """

        return await self.__categoria_repositorio.consultar_por_ID(id)
    
    async def obtener_categorias(self) -> List[Categoria]:
        """Método que retorna todas los categorias registradas en el sistema."""

        return await self.__categoria_repositorio.consultar_todas()
