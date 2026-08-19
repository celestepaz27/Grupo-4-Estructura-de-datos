from typing import List, Optional
from datetime import datetime
from .repositorio_generico import Repositorio
from acceso_datos.interfaces import IDevolucionRepositorio
from acceso_datos.modelos import Devolucion, Prestamo, EstadoPrestamo, Lector, Ejemplar, EstadoEjemplar, Libro, Categoria
from acceso_datos.conexion_db import Database


class DevolucionRepositorio(Repositorio, IDevolucionRepositorio):
    """
    Implementación concreta del repositorio de devoluciones utilizando como estado interno 
    cualquier objeto que sea de la abstracción Database.
    """

    def __init__(self, database: Database):
        super().__init__(database)
        self.__TABLA = "Devolucion"

    async def registrar(self, devolucion: Devolucion) -> int:
        """
        Método que registra una devolución en el caso de que un usuario solicite la devolución de un préstamo de un libro 
        en la base de datos. Retorna un número que no sea 0 si el registro se realizo.
        """

        if hasattr(self._database, "formatear_fecha_para_db"):
            fecha_devolucion_real_convertida = self._database.formatear_fecha_para_db(devolucion.fecha_devolucion_real)
        else:
            fecha_devolucion_real_convertida = devolucion.fecha_devolucion_real.strftime('%Y-%m-%d %H:%M:%S')
        
        datos = {
            "id_prestamo": devolucion.prestamo_asociado.id_prestamo,
            "fecha_devolucion_real": fecha_devolucion_real_convertida,
            "descripcion": devolucion.descripcion
        }
        
        return await self._database.crear(self.__TABLA, datos) 

    async def consultar_por_ID(self, id: int) -> Optional[Devolucion]:
        """Método que busca una devolución por su ID y retorna una posible si existe."""

        consulta = """
        SELECT 
            D.id_devolucion, D.fecha_devolucion_real, D.descripcion,
            P.id_prestamo, P.fecha_prestamo, P.fecha_vencimiento, P.estado AS estado_prestamo,
            U.id_usuario, U.nombre AS nombre_usuario, U.apellido AS apellido_usuario, U.correo AS correo_usuario,
            E.id_ejemplar, E.estado AS estado_ejemplar,
            L.isbn AS isbn_libro, C.id_categoria AS id_categoria_libro, C.nombre AS nombre_categoria, 
            L.titulo AS titulo_libro, L.autor AS autor_libro, L.anio_publicacion AS anio_publicacion_libro
        FROM Devolucion D
        INNER JOIN Prestamo P ON D.id_prestamo = P.id_prestamo
        INNER JOIN Usuario U ON P.id_usuario = U.id_usuario
        INNER JOIN Ejemplar E ON P.id_ejemplar = E.id_ejemplar
        INNER JOIN Libro L ON E.isbn_libro = L.isbn
        INNER JOIN Categoria C ON L.id_categoria = C.id_categoria
        WHERE D.id_devolucion = %s
        """
        
        resultados = await self._database.ejecutar_consulta(consulta, (id, ))

        if not resultados:
            return None
            
        return self.__mapear_a_objeto(resultados[0])

    async def consultar_por_prestamo(self, id_prestamo: int) -> Optional[Devolucion]:
        """Método que busca una devolución en base al préstamo asociado por su ID y la retorna si existe."""

        consulta = """
        SELECT 
            D.id_devolucion, D.fecha_devolucion_real, D.descripcion
            P.id_prestamo, P.fecha_prestamo, P.fecha_vencimiento, P.estado AS estado_prestamo,
            U.id_usuario, U.nombre AS nombre_usuario, U.apellido AS apellido_usuario, U.correo AS correo_usuario,
            E.id_ejemplar, E.estado AS estado_ejemplar,
            L.isbn AS isbn_libro, C.id_categoria AS id_categoria_libro, C.nombre AS nombre_categoria, 
            L.titulo AS titulo_libro, L.autor AS autor_libro, L.anio_publicacion AS anio_publicacion_libro
        FROM Devolucion D
        INNER JOIN Prestamo P ON D.id_prestamo = P.id_prestamo
        INNER JOIN Usuario U ON P.id_usuario = U.id_usuario
        INNER JOIN Ejemplar E ON P.id_ejemplar = E.id_ejemplar
        INNER JOIN Libro L ON E.isbn_libro = L.isbn
        INNER JOIN Categoria C ON L.id_categoria = C.id_categoria
        WHERE P.id_prestamo = %s
        """
        
        resultados = await self._database.ejecutar_consulta(consulta, (id_prestamo, ))

        if not resultados:
            return None
            
        return self.__mapear_a_objeto(resultados[0])

    async def consultar_todas(self) -> List[Devolucion]:
        """Método que busca todas las devoluciones registradas y las retorna."""

        consulta = """
        SELECT 
            D.id_devolucion, D.fecha_devolucion_real, D.descripcion
            P.id_prestamo, P.fecha_prestamo, P.fecha_vencimiento, P.estado AS estado_prestamo,
            U.id_usuario, U.nombre AS nombre_usuario, U.apellido AS apellido_usuario, U.correo AS correo_usuario,
            E.id_ejemplar, E.estado AS estado_ejemplar,
            L.isbn AS isbn_libro, C.id_categoria AS id_categoria_libro, C.nombre AS nombre_categoria, 
            L.titulo AS titulo_libro, L.autor AS autor_libro, L.anio_publicacion AS anio_publicacion_libro
        FROM Devolucion D
        INNER JOIN Prestamo P ON D.id_prestamo = P.id_prestamo
        INNER JOIN Usuario U ON P.id_usuario = U.id_usuario
        INNER JOIN Ejemplar E ON P.id_ejemplar = E.id_ejemplar
        INNER JOIN Libro L ON E.isbn_libro = L.isbn
        INNER JOIN Categoria C ON L.id_categoria = C.id_categoria
        """
        
        resultados = await self._database.ejecutar_consulta(consulta,)

        return [self.__mapear_a_objeto(fila) for fila in resultados]

    def __mapear_a_objeto(self, fila: dict) -> Devolucion:
        """Método privado que convierte cada fila de los resultados de la DB a un objeto Devolucion real."""

        if hasattr(self._database, "convertir_string_a_datetime"):
            fecha_prestamo_convertida = self._database.convertir_string_a_datetime(fila["fecha_prestamo"])
            fecha_vencimiento_convertida = self._database.convertir_string_a_datetime(fila["fecha_vencimiento"])
            fecha_devolucion_real_convertida = self._database.convertir_string_a_datetime(fila["fecha_devolucion_real"])
        else:
            fecha_prestamo_convertida = (
                fila["fecha_prestamo"] if isinstance(fila["fecha_prestamo"], datetime)
                else datetime.fromisoformat(str(fila["fecha_prestamo"])))
        
            fecha_vencimiento_convertida = (
                fila["fecha_vencimiento"] if isinstance(fila["fecha_vencimiento"], datetime) 
                else datetime.fromisoformat(str(fila["fecha_vencimiento"]))
            ) 

            fecha_devolucion_real_convertida = (
                fila["fecha_devolucion_real"] if isinstance(fila["fecha_devolucion_real"], datetime)
                else datetime.fromisoformat(str(fila["fecha_devolucion_real"]))
            )

        devolucion = Devolucion(
            id_devolucion=int(fila["id_devolucion"]),
            prestamo_asociado=Prestamo(
                id_prestamo=int(fila["id_prestamo"]),
                usuario_asociado=Lector(
                    id_usuario=int(fila["id_usuario"]),
                    nombre=fila["nombre_usuario"],
                    apellido=fila["apellido_usuario"],
                    clave="",
                    correo=fila["correo_usuario"]
                ),
                ejemplar_asociado=Ejemplar(
                    id_ejemplar=int(fila["id_ejemplar"]),
                    libro_asociado=Libro(
                        isbn=fila["isbn_libro"],
                        categoria_libro=Categoria(id_categoria=int(fila["id_categoria_libro"]), nombre=fila["nombre_categoria"]),
                        titulo=fila["titulo_libro"],
                        autor=fila["autor_libro"],
                        anio_publicacion=int(fila["anio_publicacion_libro"])
                    ),
                    estado=EstadoEjemplar(fila["estado_ejemplar"])                    
                ),
                fecha_prestamo=fecha_prestamo_convertida,
                fecha_vencimiento=fecha_vencimiento_convertida,
                estado=EstadoPrestamo(fila["estado_prestamo"])
            ),
            fecha_devolucion_real=fecha_devolucion_real_convertida,
            descripcion=fila["descripcion"]
        )

        devolucion.prestamo_asociado.fecha_devolucion = fecha_devolucion_real_convertida

        return devolucion
