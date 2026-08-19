from typing import List, Optional
from .repositorio_generico import Repositorio
from acceso_datos.interfaces import ILibroRepositorio
from acceso_datos.modelos import Libro, Categoria
from acceso_datos.conexion_db import Database


class LibroRepositorio(Repositorio, ILibroRepositorio):
    """
    Implementación concreta del repositorio de libros utilizando como estado interno 
    cualquier objeto que sea de la abstracción Database.
    """

    def __init__(self, database: Database):
        super().__init__(database)
        self.__TABLA = "Libro"

    async def registrar(self, libro: Libro) -> int:
        """
        Método que inserta un libro en la base de datos.
        Retorna un número que no sea 0 si el registro se realizo.
        """
        
        datos = {
            "isbn": libro.isbn,
            "id_categoria": libro.categoria_libro.id_categoria,
            "titulo": libro.titulo,
            "autor": libro.autor,
            "anio_publicacion": libro.anio_publicacion
        }
        
        return await self._database.crear(self.__TABLA, datos)        

    async def consultar_por_isbn(self, isbn: str) -> Optional[Libro]:
        """Método que busca un libro por su ISBN y retorna un posible libro con ese código si existe."""

        consulta = """
            SELECT L.isbn, C.id_categoria, C.nombre AS nombre_categoria, L.titulo, L.autor, L.anio_publicacion 
            FROM Libro L INNER JOIN Categoria C ON L.id_categoria = C.id_categoria
            WHERE L.isbn = %s
        """

        resultados = await self._database.ejecutar_consulta(consulta, (isbn, ))

        if not resultados:
            return None
            
        return self.__mapear_a_objeto(resultados[0])

    async def consultar_todos_por_categoria(self, categoria: Categoria) -> List[Libro]:
        """Método que busca todos los libros correspondientes a una categoría y los retorna."""

        consulta = """
            SELECT L.isbn, C.id_categoria, C.nombre AS nombre_categoria, L.titulo, L.autor, L.anio_publicacion 
            FROM Libro L INNER JOIN Categoria C ON L.id_categoria = C.id_categoria
            WHERE C.id_categoria = %s
        """

        resultados = await self._database.ejecutar_consulta(consulta, (categoria.id_categoria, ))
            
        return [self.__mapear_a_objeto(fila) for fila in resultados]

    async def consultar_todos(self) -> List[Libro]:
        """Método que busca todos los libros y los retorna."""

        consulta = """
            SELECT L.isbn, C.id_categoria, C.nombre AS nombre_categoria, L.titulo, L.autor, L.anio_publicacion 
            FROM Libro L INNER JOIN Categoria C ON L.id_categoria = C.id_categoria
        """

        resultados = await self._database.ejecutar_consulta(consulta)
            
        return [self.__mapear_a_objeto(fila) for fila in resultados]

    async def actualizar(self, isbn: str, libro: Libro) -> int:
        """
        Método que actualiza los datos de un libro existente filtrado por su ISBN respectivo.
        Retorna un número que no sea 0 si el registro se actualizo.
        """

        filtros = {"isbn": isbn}
        
        datos = {
            "id_categoria": libro.categoria_libro.id_categoria,
            "titulo": libro.titulo,
            "autor": libro.autor,
            "anio_publicacion": libro.anio_publicacion
        }
        
        return await self._database.actualizar(self.__TABLA, filtros, datos)

    async def eliminar(self, isbn: str) -> int:
        """
        Método que elimina un libro de la base de datos por su ISBN.
        Retorna un número que no sea 0 si el registro se borro.
        """

        filtros = {"isbn": isbn}

        return await self._database.eliminar(self.__TABLA, filtros)

    def __mapear_a_objeto(self, fila: dict) -> Libro:
        """Método privado que convierte cada fila de los resultados de la DB a un objeto Libro real."""

        return Libro(
            isbn=fila["isbn"],
            categoria_libro=Categoria(id_categoria=int(fila["id_categoria"]), nombre=fila["nombre_categoria"]),
            titulo=fila["titulo"],
            autor=fila["autor"],
            anio_publicacion=int(fila["anio_publicacion"])
        )
