from abc import ABC, abstractmethod
from typing import List, Optional
from acceso_datos.modelos import Libro, Categoria


class ILibroRepositorio(ABC):
    """Interfaz de las capacidades que puede ejecutar el repositorio de libros."""

    @abstractmethod
    async def registrar(self, libro: Libro) -> int:
        pass

    @abstractmethod
    async def consultar_por_isbn(self, isbn: str) -> Optional[Libro]:
        pass

    @abstractmethod
    async def consultar_todos_por_categoria(self, categoria: Categoria) -> List[Libro]:
        pass

    @abstractmethod
    async def consultar_todos(self) -> List[Libro]:
        pass

    @abstractmethod
    async def actualizar(self, isbn: str, libro: Libro) -> int:
        pass

    @abstractmethod
    async def eliminar(self, isbn: str) -> int:
        pass
