from typing import List, Optional
from datetime import datetime
from .repositorio_generico import Repositorio
from acceso_datos.interfaces import IReservaRepositorio
from acceso_datos.modelos import Reserva, EstadoReserva, Lector, Libro, Categoria
from acceso_datos.conexion_db import Database


class ReservaRepositorio(Repositorio, IReservaRepositorio):
    """
    Implementación concreta del repositorio de reservas utilizando como estado interno 
    cualquier objeto que sea de la abstracción Database.
    """

    def __init__(self, database: Database):
        super().__init__(database)
        self.__TABLA = "Reserva"

    async def registrar(self, reserva: Reserva) -> int:
        """
        Método que registra una reserva si no hay disponibilidad de ejemplares de un libro 
        en base a una solicitud de un usuario en la base de datos. Retorna un número que no sea 0 si el registro se realizo.
        """

        if hasattr(self._database, "formatear_fecha_para_db"):
            fecha_reserva_convertida = self._database.formatear_fecha_para_db(reserva.fecha_reserva)
        else:
            fecha_reserva_convertida = reserva.fecha_reserva.strftime('%Y-%m-%d %H:%M:%S')
        
        datos = {
            "id_usuario": reserva.usuario_asociado.id_usuario,
            "isbn_libro": reserva.libro_asociado.isbn,
            "fecha_reserva": fecha_reserva_convertida,
            "estado": reserva.estado.value
        }
        
        return await self._database.crear(self.__TABLA, datos) 
    
    async def consultar_por_ID(self, id: int) -> Optional[Reserva]:
        """Método que busca una reserva por su ID y retorna una posible si existe."""

        consulta = """
        SELECT 
            R.id_reserva, R.fecha_reserva, R.estado AS estado_reserva,
            U.id_usuario, U.nombre AS nombre_usuario, U.apellido AS apellido_usuario, U.correo AS correo_usuario,
            L.isbn AS isbn_libro, C.id_categoria AS id_categoria_libro, C.nombre AS nombre_categoria, 
            L.titulo AS titulo_libro, L.autor AS autor_libro, L.anio_publicacion AS anio_publicacion_libro
        FROM Reserva R
        INNER JOIN Usuario U ON R.id_usuario = U.id_usuario
        INNER JOIN Libro L ON R.isbn_libro = L.isbn
        INNER JOIN Categoria C ON L.id_categoria = C.id_categoria
        WHERE R.id_reserva = %s
        """
        
        resultados = await self._database.ejecutar_consulta(consulta, (id, ))

        if not resultados:
            return None
            
        return self.__mapear_a_objeto(resultados[0])

    async def consultar_todas(self) -> List[Reserva]:
        """Método que busca todas las reservas y las retorna."""

        consulta = """
        SELECT 
            R.id_reserva, R.fecha_reserva, R.estado AS estado_reserva,
            U.id_usuario, U.nombre AS nombre_usuario, U.apellido AS apellido_usuario, U.correo AS correo_usuario,
            L.isbn AS isbn_libro, C.id_categoria AS id_categoria_libro, C.nombre AS nombre_categoria, 
            L.titulo AS titulo_libro, L.autor AS autor_libro, L.anio_publicacion AS anio_publicacion_libro
        FROM Reserva R
        INNER JOIN Usuario U ON R.id_usuario = U.id_usuario
        INNER JOIN Libro L ON R.isbn_libro = L.isbn
        INNER JOIN Categoria C ON L.id_categoria = C.id_categoria
        """
        
        resultados = await self._database.ejecutar_consulta(consulta)
            
        return [self.__mapear_a_objeto(fila) for fila in resultados]
    
    async def consultar_pendientes(self) -> List[Reserva]:
        """Método que busca todas las reservas pendientes y las retorna."""

        consulta = """
        SELECT 
            R.id_reserva, R.fecha_reserva, R.estado AS estado_reserva,
            U.id_usuario, U.nombre AS nombre_usuario, U.apellido AS apellido_usuario, U.correo AS correo_usuario,
            L.isbn AS isbn_libro, C.id_categoria AS id_categoria_libro, C.nombre AS nombre_categoria, 
            L.titulo AS titulo_libro, L.autor AS autor_libro, L.anio_publicacion AS anio_publicacion_libro
        FROM Reserva R
        INNER JOIN Usuario U ON R.id_usuario = U.id_usuario
        INNER JOIN Libro L ON R.isbn_libro = L.isbn
        INNER JOIN Categoria C ON L.id_categoria = C.id_categoria
        WHERE R.estado = %s
        """
        
        resultados = await self._database.ejecutar_consulta(consulta, (EstadoReserva.PENDIENTE.value, ))
            
        return [self.__mapear_a_objeto(fila) for fila in resultados]
    
    async def consultar_primera_pendiente(self) -> Optional[Reserva]:
        """Método que busca la primera reserva pendiente y la retorna si existe."""

        consulta = """
        SELECT 
            R.id_reserva, R.fecha_reserva, R.estado AS estado_reserva,
            U.id_usuario, U.nombre AS nombre_usuario, U.apellido AS apellido_usuario, U.correo AS correo_usuario,
            L.isbn AS isbn_libro, C.id_categoria AS id_categoria_libro, C.nombre AS nombre_categoria, 
            L.titulo AS titulo_libro, L.autor AS autor_libro, L.anio_publicacion AS anio_publicacion_libro
        FROM Reserva R
        INNER JOIN Usuario U ON R.id_usuario = U.id_usuario
        INNER JOIN Libro L ON R.isbn_libro = L.isbn
        INNER JOIN Categoria C ON L.id_categoria = C.id_categoria
        WHERE R.estado = %s
        """

        resultados = await self._database.ejecutar_consulta(consulta, (EstadoReserva.PENDIENTE.value, ))

        if not resultados:
            return None
                    
        return self.__mapear_a_objeto(resultados[0])

    async def consultar_pendiente_por_libro_y_usuario(self, id_usuario: int, isbn_libro: str) -> Optional[Reserva]:
        """
        Método que busca una reserva pendiente correspondiente a un usuario y a un libro por su ID y ISBN respectivamente.  
        Si existe esa reserva la retorna.
        """

        consulta = """
        SELECT 
            R.id_reserva, R.fecha_reserva, R.estado AS estado_reserva,
            U.id_usuario, U.nombre AS nombre_usuario, U.apellido AS apellido_usuario, U.correo AS correo_usuario,
            L.isbn AS isbn_libro, C.id_categoria AS id_categoria_libro, C.nombre AS nombre_categoria, 
            L.titulo AS titulo_libro, L.autor AS autor_libro, L.anio_publicacion AS anio_publicacion_libro
        FROM Reserva R
        INNER JOIN Usuario U ON R.id_usuario = U.id_usuario
        INNER JOIN Libro L ON R.isbn_libro = L.isbn
        INNER JOIN Categoria C ON L.id_categoria = C.id_categoria
        WHERE U.id_usuario = %s AND L.isbn = %s AND R.estado = %s
        """

        resultados = await self._database.ejecutar_consulta(consulta, (id_usuario, isbn_libro, EstadoReserva.PENDIENTE.value))

        if not resultados:
            return None
                    
        return self.__mapear_a_objeto(resultados[0])
    
    async def consultar_pendientes_por_libro(self, isbn_libro: str) -> List[Reserva]:
        """
        Método que busca todas las reservas pendientes correspondientes a un libro por su ISBN. Si existe esa reserva la retorna.
        """

        consulta = """
        SELECT 
            R.id_reserva, R.fecha_reserva, R.estado AS estado_reserva,
            U.id_usuario, U.nombre AS nombre_usuario, U.apellido AS apellido_usuario, U.correo AS correo_usuario,
            L.isbn AS isbn_libro, C.id_categoria AS id_categoria_libro, C.nombre AS nombre_categoria, 
            L.titulo AS titulo_libro, L.autor AS autor_libro, L.anio_publicacion AS anio_publicacion_libro
        FROM Reserva R
        INNER JOIN Usuario U ON R.id_usuario = U.id_usuario
        INNER JOIN Libro L ON R.isbn_libro = L.isbn
        INNER JOIN Categoria C ON L.id_categoria = C.id_categoria
        WHERE L.isbn = %s AND R.estado = %s
        """

        resultados = await self._database.ejecutar_consulta(consulta, (isbn_libro, EstadoReserva.PENDIENTE.value))
                    
        return [self.__mapear_a_objeto(fila) for fila in resultados]
    
    async def consultar_pendientes_por_usuario(self, id_usuario: int) -> List[Reserva]:
        """
        Método que busca todas las reservas pendientes correspondientes a un usuario por su ID. Si existe esa reserva la retorna.
        """

        consulta = """
        SELECT 
            R.id_reserva, R.fecha_reserva, R.estado AS estado_reserva,
            U.id_usuario, U.nombre AS nombre_usuario, U.apellido AS apellido_usuario, U.correo AS correo_usuario,
            L.isbn AS isbn_libro, C.id_categoria AS id_categoria_libro, C.nombre AS nombre_categoria, 
            L.titulo AS titulo_libro, L.autor AS autor_libro, L.anio_publicacion AS anio_publicacion_libro
        FROM Reserva R
        INNER JOIN Usuario U ON R.id_usuario = U.id_usuario
        INNER JOIN Libro L ON R.isbn_libro = L.isbn
        INNER JOIN Categoria C ON L.id_categoria = C.id_categoria
        WHERE U.id_usuario = %s AND R.estado = %s
        """

        resultados = await self._database.ejecutar_consulta(consulta, (id_usuario, EstadoReserva.PENDIENTE.value))
                    
        return [self.__mapear_a_objeto(fila) for fila in resultados]
    
    async def actualizar_estado(self, id: int, estado: EstadoReserva) -> int:
        """
        Método que actualiza el estado de una reserva especifíca por su ID dependiendo del caso. 
        Retorna un número que no sea 0 si el registro se actualizo.
        """

        filtros = {"id_reserva": id}
        datos = {"estado": estado}
        
        return await self._database.actualizar(self.__TABLA, filtros, datos)

    def __mapear_a_objeto(self, fila: dict) -> Reserva:
        """Método privado que convierte cada fila de los resultados de la DB a un objeto Reserva real."""

        if hasattr(self._database, "convertir_string_a_datetime"):
            fecha_reserva_convertida = self._database.convertir_string_a_datetime(fila["fecha_reserva"])
        else:
            fecha_reserva_convertida = (
                fila["fecha_reserva"] if isinstance(fila["fecha_reserva"], datetime)
                else datetime.fromisoformat(str(fila["fecha_reserva"])))

        return Reserva(
            id_reserva=int(fila["id_reserva"]),
            usuario_asociado=Lector(
                id_usuario=int(fila["id_usuario"]),
                nombre=fila["nombre_usuario"],
                apellido=fila["apellido_usuario"],
                clave="",
                correo=fila["correo_usuario"]
            ),
            libro_asociado=Libro(
                isbn=fila["isbn_libro"],
                categoria_libro=Categoria(id_categoria=int(fila["id_categoria_libro"]), nombre=fila["nombre_categoria"]),
                titulo=fila["titulo_libro"],
                autor=fila["autor_libro"],
                anio_publicacion=int(fila["anio_publicacion_libro"])
            ),
            fecha_reserva=fecha_reserva_convertida,
            estado=EstadoReserva(fila["estado_reserva"])
        )
        