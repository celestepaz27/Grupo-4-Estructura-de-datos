from abc import ABC, abstractmethod
from typing import Optional, List
from acceso_datos import Categoria


class ICategoriaService(ABC):
    """Interfaz de las capacidades que puede ejecutar el service de Categorias."""

    @abstractmethod
    async def consultar_categoria(self, id: int) -> Optional[Categoria]:
        pass

    @abstractmethod
    async def obtener_categorias(self) -> List[Categoria]:
        pass
