from typing import List, Optional
from datetime import datetime
from .repositorio_generico import Repositorio
from acceso_datos.interfaces import IPrestamoRepositorio
from acceso_datos.modelos import Prestamo, EstadoPrestamo, Lector, Ejemplar, EstadoEjemplar, Libro, Categoria
from acceso_datos.conexion_db import Database


class PrestamoRepositorio(Repositorio, IPrestamoRepositorio):
    """
    Implementación concreta del repositorio de préstamos utilizando como estado interno 
    cualquier objeto que sea de la abstracción Database.
    """

    def __init__(self, database: Database):
        super().__init__(database)
        self.__TABLA = "Prestamo"

    async def registrar(self, prestamo: Prestamo) -> int:
        """
        Método que registra un préstamo producto de la solicitud de un usuario sobre un libro en la base de datos.
        Retorna un número que no sea 0 si el registro se realizo.
        """

        if hasattr(self._database, "formatear_fecha_para_db"):
            fecha_prestamo_convertida = self._database.formatear_fecha_para_db(prestamo.fecha_prestamo)
            fecha_vencimiento_convertida = self._database.formatear_fecha_para_db(prestamo.fecha_vencimiento)
        else:
            fecha_prestamo_convertida = prestamo.fecha_prestamo.strftime('%Y-%m-%d %H:%M:%S')
            fecha_vencimiento_convertida = prestamo.fecha_vencimiento.strftime('%Y-%m-%d %H:%M:%S')
        
        datos = {
            "id_usuario": prestamo.usuario_asociado.id_usuario,
            "id_ejemplar": prestamo.ejemplar_asociado.id_ejemplar,
            "fecha_prestamo": fecha_prestamo_convertida,
            "fecha_vencimiento": fecha_vencimiento_convertida,
            "estado": prestamo.estado.value
        }
        
        return await self._database.crear(self.__TABLA, datos)    

    async def consultar_por_ID(self, id: int) -> Optional[Prestamo]:
        """Método que busca un préstamo por su ID y retorna un posible préstamo si existe."""

        consulta = """
        SELECT 
            P.id_prestamo, P.fecha_prestamo, P.fecha_vencimiento, P.fecha_devolucion, P.estado AS estado_prestamo,
            U.id_usuario, U.nombre AS nombre_usuario, U.apellido AS apellido_usuario, U.correo AS correo_usuario,
            E.id_ejemplar, E.estado AS estado_ejemplar,
            L.isbn AS isbn_libro, C.id_categoria AS id_categoria_libro, C.nombre AS nombre_categoria, 
            L.titulo AS titulo_libro, L.autor AS autor_libro, L.anio_publicacion AS anio_publicacion_libro
        FROM Prestamo P
        INNER JOIN Usuario U ON P.id_usuario = U.id_usuario
        INNER JOIN Ejemplar E ON P.id_ejemplar = E.id_ejemplar
        INNER JOIN Libro L ON E.isbn_libro = L.isbn
        INNER JOIN Categoria C ON L.id_categoria = C.id_categoria
        WHERE P.id_prestamo = %s
        """
        
        resultados = await self._database.ejecutar_consulta(consulta, (id, ))

        if not resultados:
            return None
            
        return self.__mapear_a_objeto(resultados[0])

    async def consultar_todos_por_usuario(self, id_usuario: int) -> List[Prestamo]:
        """Método que busca todos los préstamos relacionados a un usuario mediante su ID y los retorna."""

        consulta = """
        SELECT 
            P.id_prestamo, P.fecha_prestamo, P.fecha_vencimiento, P.fecha_devolucion, P.estado AS estado_prestamo,
            U.id_usuario, U.nombre AS nombre_usuario, U.apellido AS apellido_usuario, U.correo AS correo_usuario, 
            E.id_ejemplar, E.estado AS estado_ejemplar,
            L.isbn AS isbn_libro, C.id_categoria AS id_categoria_libro, C.nombre AS nombre_categoria, 
            L.titulo AS titulo_libro, L.autor AS autor_libro, L.anio_publicacion AS anio_publicacion_libro
        FROM Prestamo P
        INNER JOIN Usuario U ON P.id_usuario = U.id_usuario
        INNER JOIN Ejemplar E ON P.id_ejemplar = E.id_ejemplar
        INNER JOIN Libro L ON E.isbn_libro = L.isbn
        INNER JOIN Categoria C ON L.id_categoria = C.id_categoria
        WHERE U.id_usuario = %s
        """
        
        resultados = await self._database.ejecutar_consulta(consulta, (id_usuario, ))
            
        return [self.__mapear_a_objeto(fila) for fila in resultados]
    
    async def consultar_todos_por_libro(self, isbn_libro: str) -> List[Prestamo]:
        """Método que busca todos los préstamos relacionados a un libro mediante su ISBN y los retorna."""

        consulta = """
        SELECT 
            P.id_prestamo, P.fecha_prestamo, P.fecha_vencimiento, P.fecha_devolucion, P.estado AS estado_prestamo,
            U.id_usuario, U.nombre AS nombre_usuario, U.apellido AS apellido_usuario, U.correo AS correo_usuario,
            E.id_ejemplar, E.estado AS estado_ejemplar,
            L.isbn AS isbn_libro, C.id_categoria AS id_categoria_libro, C.nombre AS nombre_categoria, 
            L.titulo AS titulo_libro, L.autor AS autor_libro, L.anio_publicacion AS anio_publicacion_libro
        FROM Prestamo P
        INNER JOIN Usuario U ON P.id_usuario = U.id_usuario
        INNER JOIN Ejemplar E ON P.id_ejemplar = E.id_ejemplar
        INNER JOIN Libro L ON E.isbn_libro = L.isbn
        INNER JOIN Categoria C ON L.id_categoria = C.id_categoria
        WHERE L.isbn = %s
        """
        
        resultados = await self._database.ejecutar_consulta(consulta, (isbn_libro, ))
            
        return [self.__mapear_a_objeto(fila) for fila in resultados]

    async def consultar_activos(self) -> List[Prestamo]:
        """Método que busca todos los préstamos activos y los retorna."""

        consulta = """
        SELECT 
            P.id_prestamo, P.fecha_prestamo, P.fecha_vencimiento, P.fecha_devolucion, P.estado AS estado_prestamo,
            U.id_usuario, U.nombre AS nombre_usuario, U.apellido AS apellido_usuario, U.correo AS correo_usuario,
            E.id_ejemplar, E.estado AS estado_ejemplar,
            L.isbn AS isbn_libro, C.id_categoria AS id_categoria_libro, C.nombre AS nombre_categoria, 
            L.titulo AS titulo_libro, L.autor AS autor_libro, L.anio_publicacion AS anio_publicacion_libro
        FROM Prestamo P
        INNER JOIN Usuario U ON P.id_usuario = U.id_usuario
        INNER JOIN Ejemplar E ON P.id_ejemplar = E.id_ejemplar
        INNER JOIN Libro L ON E.isbn_libro = L.isbn
        INNER JOIN Categoria C ON L.id_categoria = C.id_categoria
        WHERE P.estado = %s
        """
        
        resultados = await self._database.ejecutar_consulta(consulta, (EstadoPrestamo.ACTIVO.value, ))
            
        return [self.__mapear_a_objeto(fila) for fila in resultados]

    async def consultar_vencidos(self) -> List[Prestamo]:
        """Método que busca todos los préstamos vencidos y los retorna."""

        consulta = """
        SELECT 
            P.id_prestamo, P.fecha_prestamo, P.fecha_vencimiento, P.fecha_devolucion, P.estado AS estado_prestamo,
            U.id_usuario, U.nombre AS nombre_usuario, U.apellido AS apellido_usuario, U.correo AS correo_usuario,
            E.id_ejemplar, E.estado AS estado_ejemplar,
            L.isbn AS isbn_libro, C.id_categoria AS id_categoria_libro, C.nombre AS nombre_categoria, 
            L.titulo AS titulo_libro, L.autor AS autor_libro, L.anio_publicacion AS anio_publicacion_libro
        FROM Prestamo P
        INNER JOIN Usuario U ON P.id_usuario = U.id_usuario
        INNER JOIN Ejemplar E ON P.id_ejemplar = E.id_ejemplar
        INNER JOIN Libro L ON E.isbn_libro = L.isbn
        INNER JOIN Categoria C ON L.id_categoria = C.id_categoria
        WHERE P.estado = %s
        """
        
        resultados = await self._database.ejecutar_consulta(consulta, (EstadoPrestamo.VENCIDO.value, ))
            
        return [self.__mapear_a_objeto(fila) for fila in resultados]

    async def consultar_activos_por_usuario(self, id_usuario: int) -> List[Prestamo]:
        """Método que busca todos los préstamos activos relacionados a un usuario mediante su ID y los retorna."""

        consulta = """
        SELECT 
            P.id_prestamo, P.fecha_prestamo, P.fecha_vencimiento, P.fecha_devolucion, P.estado AS estado_prestamo,
            U.id_usuario, U.nombre AS nombre_usuario, U.apellido AS apellido_usuario, U.correo AS correo_usuario,
            E.id_ejemplar, E.estado AS estado_ejemplar,
            L.isbn AS isbn_libro, C.id_categoria AS id_categoria_libro, C.nombre AS nombre_categoria, 
            L.titulo AS titulo_libro, L.autor AS autor_libro, L.anio_publicacion AS anio_publicacion_libro
        FROM Prestamo P
        INNER JOIN Usuario U ON P.id_usuario = U.id_usuario
        INNER JOIN Ejemplar E ON P.id_ejemplar = E.id_ejemplar
        INNER JOIN Libro L ON E.isbn_libro = L.isbn
        INNER JOIN Categoria C ON L.id_categoria = C.id_categoria
        WHERE U.id_usuario = %s AND P.estado = %s
        """
        
        resultados = await self._database.ejecutar_consulta(consulta, (id_usuario, EstadoPrestamo.ACTIVO.value))
            
        return [self.__mapear_a_objeto(fila) for fila in resultados]

    async def consultar_vencidos_por_usuario(self, id_usuario: int) -> List[Prestamo]:
        """Método que busca todos los préstamos vencidos relacionados a un usuario mediante su ID y los retorna."""

        consulta = """
        SELECT 
            P.id_prestamo, P.fecha_prestamo, P.fecha_vencimiento, P.fecha_devolucion, P.estado AS estado_prestamo,
            U.id_usuario, U.nombre AS nombre_usuario, U.apellido AS apellido_usuario, U.correo AS correo_usuario,
            E.id_ejemplar, E.estado AS estado_ejemplar,
            L.isbn AS isbn_libro, C.id_categoria AS id_categoria_libro, C.nombre AS nombre_categoria, 
            L.titulo AS titulo_libro, L.autor AS autor_libro, L.anio_publicacion AS anio_publicacion_libro
        FROM Prestamo P
        INNER JOIN Usuario U ON P.id_usuario = U.id_usuario
        INNER JOIN Ejemplar E ON P.id_ejemplar = E.id_ejemplar
        INNER JOIN Libro L ON E.isbn_libro = L.isbn
        INNER JOIN Categoria C ON L.id_categoria = C.id_categoria
        WHERE U.id_usuario = %s AND P.estado = %s
        """
        
        resultados = await self._database.ejecutar_consulta(consulta, (id_usuario, EstadoPrestamo.VENCIDO.value))
            
        return [self.__mapear_a_objeto(fila) for fila in resultados]

    async def consultar_activos_por_libro(self, isbn_libro: str) -> List[Prestamo]:
        """Método que busca todos los préstamos activos relacionados a un libro mediante su ISBN y los retorna."""

        consulta = """
        SELECT 
            P.id_prestamo, P.fecha_prestamo, P.fecha_vencimiento, P.fecha_devolucion, P.estado AS estado_prestamo,
            U.id_usuario, U.nombre AS nombre_usuario, U.apellido AS apellido_usuario, U.correo AS correo_usuario,
            E.id_ejemplar, E.estado AS estado_ejemplar,
            L.isbn AS isbn_libro, C.id_categoria AS id_categoria_libro, C.nombre AS nombre_categoria, 
            L.titulo AS titulo_libro, L.autor AS autor_libro, L.anio_publicacion AS anio_publicacion_libro
        FROM Prestamo P
        INNER JOIN Usuario U ON P.id_usuario = U.id_usuario
        INNER JOIN Ejemplar E ON P.id_ejemplar = E.id_ejemplar
        INNER JOIN Libro L ON E.isbn_libro = L.isbn
        INNER JOIN Categoria C ON L.id_categoria = C.id_categoria
        WHERE L.isbn = %s AND P.estado = %s
        """
        
        resultados = await self._database.ejecutar_consulta(consulta, (isbn_libro, EstadoPrestamo.ACTIVO.value))
            
        return [self.__mapear_a_objeto(fila) for fila in resultados]

    async def consultar_vencidos_por_libro(self, isbn_libro: str) -> List[Prestamo]:
        """Método que busca todos los préstamos vencidos relacionados a un libro mediante su ISBN y los retorna."""

        consulta = """
        SELECT 
            P.id_prestamo, P.fecha_prestamo, P.fecha_vencimiento, P.fecha_devolucion, P.estado AS estado_prestamo,
            U.id_usuario, U.nombre AS nombre_usuario, U.apellido AS apellido_usuario, U.correo AS correo_usuario,
            E.id_ejemplar, E.estado AS estado_ejemplar,
            L.isbn AS isbn_libro, C.id_categoria AS id_categoria_libro, C.nombre AS nombre_categoria, 
            L.titulo AS titulo_libro, L.autor AS autor_libro, L.anio_publicacion AS anio_publicacion_libro
        FROM Prestamo P
        INNER JOIN Usuario U ON P.id_usuario = U.id_usuario
        INNER JOIN Ejemplar E ON P.id_ejemplar = E.id_ejemplar
        INNER JOIN Libro L ON E.isbn_libro = L.isbn
        INNER JOIN Categoria C ON L.id_categoria = C.id_categoria
        WHERE L.isbn = %s AND P.estado = %s
        """
        
        resultados = await self._database.ejecutar_consulta(consulta, (isbn_libro, EstadoPrestamo.VENCIDO.value))
            
        return [self.__mapear_a_objeto(fila) for fila in resultados]

    async def consultar_activo_por_usuario_y_id_libro(self, id_usuario: int, isbn_libro: str) -> Optional[Prestamo]:
        """
        Método que busca un posible préstamo activo relacionado a un usuario y libro mediante su ID y ISBN respectivamente
        y lo retorna tal cual si existe.
        """

        consulta = """
        SELECT 
            P.id_prestamo, P.fecha_prestamo, P.fecha_vencimiento, P.fecha_devolucion, P.estado AS estado_prestamo,
            U.id_usuario, U.nombre AS nombre_usuario, U.apellido AS apellido_usuario, U.correo AS correo_usuario,
            E.id_ejemplar, E.estado AS estado_ejemplar,
            L.isbn AS isbn_libro, C.id_categoria AS id_categoria_libro, C.nombre AS nombre_categoria, 
            L.titulo AS titulo_libro, L.autor AS autor_libro, L.anio_publicacion AS anio_publicacion_libro
        FROM Prestamo P
        INNER JOIN Usuario U ON P.id_usuario = U.id_usuario
        INNER JOIN Ejemplar E ON P.id_ejemplar = E.id_ejemplar
        INNER JOIN Libro L ON E.isbn_libro = L.isbn
        INNER JOIN Categoria C ON L.id_categoria = C.id_categoria
        WHERE U.id_usuario = %s AND L.isbn = %s AND P.estado = %s
        """
        
        resultados = await self._database.ejecutar_consulta(consulta, (id_usuario, isbn_libro, EstadoPrestamo.ACTIVO.value))

        if not resultados:
            return None

        return self.__mapear_a_objeto(resultados[0])
    
    async def consultar_activo_por_ejemplar(self, id_ejemplar: int) -> Optional[Prestamo]:
        """
        Método que busca un posible préstamo activo relacionado a un ejemplar especifico de un libro por su ID 
        y lo retorna tal cual si existe.
        """

        consulta = """
        SELECT 
            P.id_prestamo, P.fecha_prestamo, P.fecha_vencimiento, P.fecha_devolucion, P.estado AS estado_prestamo,
            U.id_usuario, U.nombre AS nombre_usuario, U.apellido AS apellido_usuario, U.correo AS correo_usuario,
            E.id_ejemplar, E.estado AS estado_ejemplar,
            L.isbn AS isbn_libro, C.id_categoria AS id_categoria_libro, C.nombre AS nombre_categoria, 
            L.titulo AS titulo_libro, L.autor AS autor_libro, L.anio_publicacion AS anio_publicacion_libro
        FROM Prestamo P
        INNER JOIN Usuario U ON P.id_usuario = U.id_usuario
        INNER JOIN Ejemplar E ON P.id_ejemplar = E.id_ejemplar
        INNER JOIN Libro L ON E.isbn_libro = L.isbn
        INNER JOIN Categoria C ON L.id_categoria = C.id_categoria
        WHERE E.id_ejemplar = %s AND P.estado = %s
        """
        
        resultados = await self._database.ejecutar_consulta(consulta, (id_ejemplar, EstadoPrestamo.ACTIVO.value))

        if not resultados:
            return None

        return self.__mapear_a_objeto(resultados[0])

    async def asignar_fecha_devolucion(self, id: int, fecha: datetime) -> int:
        """
        Método que actualiza un préstamo por su ID asignando fecha de devolución a este cuando un usuario 
        solicite devolución de un libro. Retorna un número que no sea 0 si el registro se actualizo.
        """

        if hasattr(self._database, "formatear_fecha_para_db"):
            fecha_devolucion_convertida = self._database.formatear_fecha_para_db(fecha)
        else:
            fecha_devolucion_convertida = fecha.strftime('%Y-%m-%d %H:%M:%S')

        filtros = {"id_prestamo": id}
        datos = {"fecha_devolucion": fecha_devolucion_convertida}
        
        return await self._database.actualizar(self.__TABLA, filtros, datos)

    async def actualizar_fecha_vencimiento(self, id: int, fecha: datetime) -> int:
        """
        Método que actualiza un préstamo por su ID modificando la fecha de vencimiento de este. 
        Retorna un número que no sea 0 si el registro se actualizo.
        """

        if hasattr(self._database, "formatear_fecha_para_db"):
            fecha_vencimiento_convertida = self._database.formatear_fecha_para_db(fecha)
        else:
            fecha_vencimiento_convertida = fecha.strftime('%Y-%m-%d %H:%M:%S')

        filtros = {"id_prestamo": id}
        datos = {"fecha_vencimiento": fecha_vencimiento_convertida}
        
        return await self._database.actualizar(self.__TABLA, filtros, datos)

    async def actualizar_estado(self, id: int, estado: EstadoPrestamo) -> int:
        """
        Método que actualiza el estado de un préstamo especifíco por su ID dependiendo del caso. 
        Retorna un número que no sea 0 si el registro se actualizo.
        """

        filtros = {"id_prestamo": id}
        datos = {"estado": estado}
        
        return await self._database.actualizar(self.__TABLA, filtros, datos)

    def __mapear_a_objeto(self, fila: dict) -> Prestamo:
        """Método privado que convierte cada fila de los resultados de la DB a un objeto Prestamo real."""

        if hasattr(self._database, "convertir_string_a_datetime"):
            fecha_prestamo_convertida = self._database.convertir_string_a_datetime(fila["fecha_prestamo"])
            fecha_vencimiento_convertida = self._database.convertir_string_a_datetime(fila["fecha_vencimiento"])
            fecha_devolucion_convertida = (
                self._database.convertir_string_a_datetime(fila["fecha_devolucion"]) if fila["fecha_devolucion"] else None
            )

        else:
            fecha_prestamo_convertida = (
                fila["fecha_prestamo"] if isinstance(fila["fecha_prestamo"], datetime)
                else datetime.fromisoformat(str(fila["fecha_prestamo"])))
        
            fecha_vencimiento_convertida = (
                fila["fecha_vencimiento"] if isinstance(fila["fecha_vencimiento"], datetime) 
                else datetime.fromisoformat(str(fila["fecha_vencimiento"]))
            )

            fecha_devolucion_convertida = (
                (
                    fila["fecha_devolucion"] if isinstance(fila["fecha_devolucion"], datetime)
                    else datetime.fromisoformat(str(fila["fecha_devolucion"]))
                ) if fila["fecha_devolucion"] else None
            )

        prestamo = Prestamo(
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
        )             

        if fecha_devolucion_convertida:
            prestamo.fecha_devolucion = fecha_devolucion_convertida

        return prestamo
