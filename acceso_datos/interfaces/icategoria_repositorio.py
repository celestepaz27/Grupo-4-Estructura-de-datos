from abc import ABC, abstractmethod
from typing import List, Optional
from acceso_datos.modelos import Categoria


class ICategoriaRepositorio(ABC):
    """Interfaz de las capacidades que puede ejecutar el repositorio de categorias."""

    @abstractmethod
    async def consultar_por_ID(self, id : int) -> Optional[Categoria]:
        pass

    @abstractmethod
    async def consultar_todas(self) -> List[Categoria]:
        pass
