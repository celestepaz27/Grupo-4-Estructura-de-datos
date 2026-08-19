from typing import List, Optional
from .repositorio_generico import Repositorio
from acceso_datos.interfaces import IEjemplarRepositorio
from acceso_datos.modelos import Ejemplar, EstadoEjemplar, Libro, Categoria
from acceso_datos.conexion_db import Database


class EjemplarRepositorio(Repositorio, IEjemplarRepositorio):
    """
    Implementación concreta del repositorio de ejemplares utilizando como estado interno 
    cualquier objeto que sea de la abstracción Database.
    """

    def __init__(self, database: Database):
        super().__init__(database)
        self.__TABLA = "Ejemplar"

    async def registrar(self, ejemplar: Ejemplar) -> int:
        """
        Método que inserta un ejemplar asociado a un libro en la base de datos.
        Retorna un número que no sea 0 si el registro se realizo.
        """
        
        datos = {
            "isbn_libro": ejemplar.libro_asociado.isbn,
            "estado": ejemplar.estado.value
        }
        
        return await self._database.crear(self.__TABLA, datos)    

    async def consultar_por_ID(self, id: int) -> Optional[Ejemplar]:
        """Método que busca un ejemplar por su ID y retorna un posible ejemplar si existe."""

        consulta = """
        SELECT 
            E.id_ejemplar, E.estado,
            L.isbn AS isbn_libro, C.id_categoria, C.nombre AS nombre_categoria,
            L.titulo, L.autor, L.anio_publicacion
        FROM Ejemplar E
        INNER JOIN Libro L ON E.isbn_libro = L.isbn
        INNER JOIN Categoria C ON C.id_categoria = L.id_categoria
        WHERE E.id_ejemplar = %s
        """
        
        resultados = await self._database.ejecutar_consulta(consulta, (id, ))

        if not resultados:
            return None
            
        return self.__mapear_a_objeto(resultados[0])

    async def consultar_por_libro(self, isbn_libro: str) -> List[Ejemplar]:
        """Método que busca todas los ejemplares asociados a un libro especifico por su ISBN y los retorna."""

        consulta = """
        SELECT 
            E.id_ejemplar, E.estado,
            L.isbn AS isbn_libro, C.id_categoria, C.nombre AS nombre_categoria,
            L.titulo, L.autor, L.anio_publicacion
        FROM Ejemplar E
        INNER JOIN Libro L ON E.isbn_libro = L.isbn
        INNER JOIN Categoria C ON C.id_categoria = L.id_categoria
        WHERE L.isbn = %s
        """
        
        resultados = await self._database.ejecutar_consulta(consulta, (isbn_libro, ))
            
        return [self.__mapear_a_objeto(fila) for fila in resultados]

    async def consultar_disponibles_por_libro(self, isbn_libro: str) -> List[Ejemplar]:
        """Método que busca todas los ejemplares DISPONIBLES asociados a un libro especifico por su ISBN y los retorna."""

        consulta = """
        SELECT 
            E.id_ejemplar, E.estado,
            L.isbn AS isbn_libro, C.id_categoria, C.nombre AS nombre_categoria,
            L.titulo, L.autor, L.anio_publicacion
        FROM Ejemplar E
        INNER JOIN Libro L ON E.isbn_libro = L.isbn
        INNER JOIN Categoria C ON C.id_categoria = L.id_categoria
        WHERE L.isbn = %s AND E.estado = %s
        """
        
        resultados = await self._database.ejecutar_consulta(consulta, (isbn_libro, EstadoEjemplar.DISPONIBLE.value))
            
        return [self.__mapear_a_objeto(fila) for fila in resultados]

    async def actualizar_estado(self, id: int, estado: EstadoEjemplar) -> int:
        """
        Método que actualiza el estado de un ejemplar especifíco por su ID.
        Retorna un número que no sea 0 si el registro se actualizo.
        """

        filtros = {"id_ejemplar": id}
        datos = {"estado": estado}
        
        return await self._database.actualizar(self.__TABLA, filtros, datos)

    async def eliminar(self, id: int) -> int:
        """
        Método que elimina un ejemplar de la base de datos por su ID.
        Retorna un número que no sea 0 si el registro se borro.
        """

        filtros = {"id_ejemplar": id}

        return await self._database.eliminar(self.__TABLA, filtros)

    def __mapear_a_objeto(self, fila: dict) -> Ejemplar:
        """Método privado que convierte cada fila de los resultados de la DB a un objeto Ejemplar real."""

        return Ejemplar(
            id_ejemplar=int(fila["id_ejemplar"]),
            libro_asociado=Libro(
                isbn=fila["isbn_libro"],
                categoria_libro=Categoria(id_categoria=int(fila["id_categoria"]), nombre=fila["nombre_categoria"]),
                titulo=fila["titulo"],
                autor=fila["autor"],
                anio_publicacion=int(fila["anio_publicacion"])
            ),
            estado=EstadoEjemplar(fila["estado"])
        )
