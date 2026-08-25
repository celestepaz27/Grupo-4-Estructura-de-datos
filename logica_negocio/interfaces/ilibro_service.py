from abc import ABC, abstractmethod
from typing import Optional
from acceso_datos import Libro, Categoria
from logica_negocio.estructuras import DoublyLinkedList, ArbolAVL


class ILibroService(ABC):
    """Interfaz de las capacidades que puede ejecutar el service de Libros."""

    @abstractmethod
    async def registrar_libro(self, libro: Libro) -> int: pass

    @abstractmethod
    async def modificar_libro(self, isbn: str, libro_modificado: Libro) -> int: pass

    @abstractmethod
    async def eliminar_libro(self, isbn: str) -> int: pass

    @abstractmethod
    async def consultar_libro(self, isbn: str) -> Optional[Libro]: pass

    @abstractmethod
    def buscar_libros(self, criterio: str) -> DoublyLinkedList[Libro]: pass

    @abstractmethod
    async def filtrar_libros_por_categoria(self, categoria: Categoria) -> DoublyLinkedList[Libro]: pass

    @abstractmethod
    async def existe_libro(self, isbn: str) -> bool: pass

    @abstractmethod
    async def obtener_catalogo_libros(self) -> ArbolAVL[Libro]: pass

    @abstractmethod
    async def esta_disponible(self, isbn: str) -> bool: pass

    @abstractmethod
    async def _cargar_catalogo_libros(self) -> None: pass

    @abstractmethod
    def _cargar_indices_ISBN(self) -> None: pass
