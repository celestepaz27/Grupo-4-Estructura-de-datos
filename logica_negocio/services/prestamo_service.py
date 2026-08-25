from typing import Optional
from datetime import datetime, timedelta
from logica_negocio.interfaces import (
    IPrestamoService, 
    ILibroService, 
    IReservaService, 
    IUsuarioService, 
    IDevolucionService, 
    IEjemplarService
)

from logica_negocio.estructuras import DoublyLinkedList
from acceso_datos import (
    Prestamo, 
    Usuario, 
    Lector, 
    Libro, 
    EstadoPrestamo, 
    IPrestamoRepositorio, 
    EstadoEjemplar, 
    EstadoReserva,
    Reserva
)


class PrestamoService(IPrestamoService):
    """Implementación concreta del servicio de préstamos para su control."""

    def __init__(
            self, 
            prestamo_repositorio: IPrestamoRepositorio, 
            libro_service: ILibroService,
            reserva_service: IReservaService,
            usuario_service: IUsuarioService,
            ejemplar_service: IEjemplarService):
        
        self.__prestamo_repositorio = prestamo_repositorio

        self.__libro_service = libro_service
        self.__reserva_service = reserva_service
        self.__usuario_service = usuario_service
        self.__ejemplar_service = ejemplar_service
        
        self.__prestamos: DoublyLinkedList[Prestamo] = DoublyLinkedList[Prestamo]()

    async def _cargar_prestamos(self) -> None:
        """
        Método interno protegido que sincroniza los préstamos activos y vencidos 
        con la lista enlazada doble local de préstamos.
        """

        prestamos_activos = await self.__prestamo_repositorio.consultar_activos()
        prestamos_vencidos = await self.__prestamo_repositorio.consultar_vencidos()
        
        self.__prestamos = DoublyLinkedList[Prestamo]()
        
        for prestamo in prestamos_activos:
            if datetime.now() > prestamo.fecha_vencimiento:
                await self.__prestamo_repositorio.actualizar_estado(prestamo.id_prestamo, EstadoPrestamo.VENCIDO.value)
                prestamo.estado = EstadoPrestamo.VENCIDO
                self.__prestamos.insertar_al_final(prestamo)
            else:
                self.__prestamos.insertar_al_final(prestamo)
                
        for prestamo in prestamos_vencidos:
            self.__prestamos.insertar_al_final(prestamo)

    async def registrar_prestamo(self, usuario: Usuario, libro: Libro) -> Prestamo:
        """
        Método que registra un préstamo en el repositorio de préstamos para su debida agregación en el sistema.\n
        Representa a la lógica de la solicitud de un Lector para el préstamo para un libro.\n
        Verifica de forma estricta que el lector no posea préstamos vencidos pendientes de devolución,
        si posee ya uno activo a cierto libro, o si hay disponibilidad de ejemplares sobre ese libro.
        Si no hay disponibilidad de ejemplares, se registra mediante una reserva.\n
        Si el préstamo finalmente queda registrado, se modifica el estado del ejemplar asignado autómaticamente.
        """

        usuario_a_consultar = await self.__usuario_service.consultar_usuario(usuario.id_usuario)

        if not usuario_a_consultar:
            raise ValueError("Error de solicitud de préstamo: El usuario a consultar no existe.")

        if not isinstance(usuario, Lector):
            raise PermissionError("Error de permiso. Solo un lector puede solicitar préstamos.")

        if not await self.validar_elegibilidad_usuario(usuario.id_usuario):
            raise ValueError("Error de solicitud de préstamo: El lector posee préstamos vencidos pendientes de devolución.")
            
        prestamo_duplicado = await self.consultar_prestamo_activo_por_libro_y_usuario(usuario.id_usuario, libro.isbn)

        if prestamo_duplicado:
            raise ValueError("Error de solicitud de préstamo: El lector ya posee un préstamo activo asociado a este libro.")

        if await self.__reserva_service.consultar_reserva_pendiente_por_libro_y_usuario(usuario.id_usuario, libro.isbn):
            raise ValueError("Error de solicitud de préstamo: El lector posee reserva pendiente de este libro.")
        
        if not await self.validar_disponibilidad_libro(libro.isbn):

            await self.__reserva_service.registrar_reserva(Reserva(
                usuario_asociado=usuario,
                libro_asociado=libro,
                fecha_reserva=datetime.now(),
                estado=EstadoReserva.PENDIENTE
            ))

            raise ValueError("Error de solicitud de préstamo: No hay ejemplares disponibles. Procesando mediante reserva...")

        ejemplar_util = await self.__ejemplar_service.obtener_primer_ejemplar_disponible(libro.isbn)

        if ejemplar_util is None:
            raise ValueError("Error de solicitud de préstamo: No hay ejemplares disponibles para este libro.")

        if ejemplar_util.estado != EstadoEjemplar.DISPONIBLE:
            raise ValueError("Error de solicitud de préstamo: El ejemplar seleccionado no está disponible.")

        if await self.consultar_prestamo_activo_por_ejemplar(ejemplar_util.id_ejemplar):
            raise ValueError("Error de solicitud de préstamo: El ejemplar ya se encuentra asociado a un préstamo activo.")
      
        fecha_inicio = datetime.now()
        fecha_vencimiento = fecha_inicio + timedelta(days=7)

        nuevo_prestamo = Prestamo(
            usuario_asociado=usuario,
            ejemplar_asociado=ejemplar_util,
            fecha_prestamo=fecha_inicio,
            fecha_vencimiento=fecha_vencimiento,
            estado=EstadoPrestamo.ACTIVO
        )

        id_generado = await self.__prestamo_repositorio.registrar(nuevo_prestamo)

        if id_generado <= 0:
            raise Exception(f"Error de solicitud de préstamo: La solicitud del préstamo no se registró.")

        id_ejemplar_modificado = await self.__ejemplar_service.modificar_estado_ejemplar(
            ejemplar_util.id_ejemplar,
            EstadoEjemplar.PRESTADO
        )
        
        if id_ejemplar_modificado <= 0:
            raise Exception(f"Error de actualización de ejemplar: \
                            El estado del ejemplar no se modifico tras registrar su respectivo préstamo.")

        await self._cargar_prestamos()

        return nuevo_prestamo
    
    async def devolver_prestamo(self, id: int) -> int:
        """
        Método que cierra un préstamo activo del repositorio de préstamos.\n
        Si devuelve un número distinto a 0, el préstamo quedo devuelto con su fecha de devolución.
        """

        prestamo = await self.consultar_prestamo_por_ID(id)

        if prestamo is None:
            raise ValueError("Error de devolución de préstamo: El préstamo no existe.")

        if prestamo.estado not in (EstadoPrestamo.ACTIVO, EstadoPrestamo.VENCIDO):
            raise ValueError("Error de devolución de préstamo: Solo se pueden devolver préstamos activos o vencidos.")

        if datetime.now() <= prestamo.fecha_prestamo:
            raise ValueError("Error de devolución de préstamo: La fecha de devolución debe ser posterior al inicio.")

        id_prestamo_devuelto = await self.__prestamo_repositorio.asignar_fecha_devolucion(id, datetime.now())

        if id_prestamo_devuelto <= 0:
            raise Exception(f"Error de actualización de préstamo: \
                            No se asigno una fecha de devolución al respectivo préstamo.")
        
        await self._cargar_prestamos()

        return id_prestamo_devuelto

    async def consultar_prestamo_por_ID(self, id: int) -> Optional[Prestamo]:
        """
        Método que consulta en el repositorio de préstamos sobre la existencia de uno.\n
        Si existe devuelve ese registro en un objeto de tipo Préstamo, si no es así, se devuelve None.\n
        """

        if self.__prestamos.obtener_tamanio() == 0:
            await self._cargar_prestamos()
            
        return await self.__prestamo_repositorio.consultar_por_ID(id)

    async def consultar_prestamos_por_usuario(self, id_usuario: int) -> DoublyLinkedList[Prestamo]: 
        """
        Método que consulta en el repositorio de préstamos sobre todos los préstamos asociados a un usuario por su ID.\n
        Retorna una lista doble enlazada con todos los préstamos asociados encontrados.\n
        """

        usuario_a_consultar = await self.__usuario_service.consultar_usuario(id_usuario)

        if not usuario_a_consultar:
            raise ValueError("Error de consulta de préstamos: El usuario a consultar no existe.")

        prestamos_por_usuario = await self.__prestamo_repositorio.consultar_todos_por_usuario(id_usuario)

        lista_enlazada_doble_prestamos = DoublyLinkedList[Prestamo]()
        
        for prestamo in prestamos_por_usuario:
            lista_enlazada_doble_prestamos.insertar_al_final(prestamo)

        return lista_enlazada_doble_prestamos
    
    async def consultar_prestamos_por_libro(self, isbn_libro: str) -> DoublyLinkedList[Prestamo]:
        """
        Método que consulta en el repositorio de préstamos sobre todos los préstamos asociados a un libro por su ISBN.\n
        Retorna una lista doble enlazada con todos los préstamos asociados encontrados.\n
        """

        prestamos_por_libro = await self.__prestamo_repositorio.consultar_todos_por_libro(isbn_libro)

        lista_enlazada_doble_prestamos = DoublyLinkedList[Prestamo]()
        
        for prestamo in prestamos_por_libro:
            lista_enlazada_doble_prestamos.insertar_al_final(prestamo)

        return lista_enlazada_doble_prestamos

    async def consultar_prestamos_activos(self) -> DoublyLinkedList[Prestamo]:
        """
        Método que consulta en el repositorio de préstamos sobre todos los préstamos activos.\n
        Retorna una lista doble enlazada con todos los préstamos encontrados.
        """

        prestamos_activos = await self.__prestamo_repositorio.consultar_activos()

        lista_enlazada_doble_prestamos = DoublyLinkedList[Prestamo]()
        
        for prestamo in prestamos_activos:
            lista_enlazada_doble_prestamos.insertar_al_final(prestamo)

        return lista_enlazada_doble_prestamos

    async def consultar_prestamos_vencidos(self) -> DoublyLinkedList[Prestamo]:
        """
        Método que consulta en el repositorio de préstamos sobre todos los préstamos vencidos.\n
        Retorna una lista doble enlazada con todos los préstamos encontrados.
        """

        prestamos_vencidos = await self.__prestamo_repositorio.consultar_vencidos()

        lista_enlazada_doble_prestamos = DoublyLinkedList[Prestamo]()
        
        for prestamo in prestamos_vencidos:
            lista_enlazada_doble_prestamos.insertar_al_final(prestamo)

        return lista_enlazada_doble_prestamos

    async def consultar_prestamos_activos_por_usuario(self, id_usuario: int) -> DoublyLinkedList[Prestamo]: 
        """
        Método que consulta en el repositorio de préstamos sobre todos los préstamos activos asociados a un usuario.\n
        Retorna una lista doble enlazada con todos los préstamos asociados a un usuario encontrados.
        """

        usuario_a_consultar = await self.__usuario_service.consultar_usuario(id_usuario)

        if not usuario_a_consultar:
            raise ValueError("Error de consulta de préstamos: El usuario a consultar no existe.")
        
        prestamos_activos_por_usuario = await self.__prestamo_repositorio.consultar_activos_por_usuario(id_usuario)

        lista_enlazada_doble_prestamos = DoublyLinkedList[Prestamo]()
        
        for prestamo in prestamos_activos_por_usuario:
            lista_enlazada_doble_prestamos.insertar_al_final(prestamo)

        return lista_enlazada_doble_prestamos

    async def consultar_prestamos_vencidos_por_usuario(self, id_usuario: int) -> DoublyLinkedList[Prestamo]: 
        """
        Método que consulta en el repositorio de préstamos sobre todos los préstamos vencidos asociados a un usuario.\n
        Retorna una lista doble enlazada con todos los préstamos asociados a un usuario encontrados.
        """

        usuario_a_consultar = await self.__usuario_service.consultar_usuario(id_usuario)

        if not usuario_a_consultar:
            raise ValueError("Error de consulta de préstamos: El usuario a consultar no existe.")
        
        prestamos_vencidos_por_usuario = await self.__prestamo_repositorio.consultar_vencidos_por_usuario(id_usuario)

        lista_enlazada_doble_prestamos = DoublyLinkedList[Prestamo]()
        
        for prestamo in prestamos_vencidos_por_usuario:
            lista_enlazada_doble_prestamos.insertar_al_final(prestamo)

        return lista_enlazada_doble_prestamos

    async def consultar_prestamos_activos_por_libro(self, isbn_libro: str) -> DoublyLinkedList[Prestamo]: 
        """
        Método que consulta en el repositorio de préstamos sobre todos los préstamos activos asociados a un libro.\n
        Retorna una lista doble enlazada con todos los préstamos asociados a un libro encontrados.
        """

        prestamos_activos_por_libro = await self.__prestamo_repositorio.consultar_activos_por_libro(isbn_libro)

        lista_enlazada_doble_prestamos = DoublyLinkedList[Prestamo]()
        
        for prestamo in prestamos_activos_por_libro:
            lista_enlazada_doble_prestamos.insertar_al_final(prestamo)

        return lista_enlazada_doble_prestamos

    async def consultar_prestamos_vencidos_por_libro(self, isbn_libro: str) -> DoublyLinkedList[Prestamo]: 
        """
        Método que consulta en el repositorio de préstamos sobre todos los préstamos vencidos asociados a un libro.\n
        Retorna una lista doble enlazada con todos los préstamos asociados a un libro encontrados.
        """

        prestamos_vencidos_por_libro = await self.__prestamo_repositorio.consultar_vencidos_por_libro(isbn_libro)

        lista_enlazada_doble_prestamos = DoublyLinkedList[Prestamo]()
        
        for prestamo in prestamos_vencidos_por_libro:
            lista_enlazada_doble_prestamos.insertar_al_final(prestamo)

        return lista_enlazada_doble_prestamos

    async def consultar_prestamo_activo_por_libro_y_usuario(self, id_usuario: int, isbn_libro: str) -> Optional[Prestamo]: 
        """
        Método que consulta en el repositorio de préstamos sobre si un usuario contiene un préstamo activo asociado a un libro.\n
        Si existe devuelve ese registro en un objeto de tipo Préstamo, si no es así, se devuelve None.
        """

        if self.__prestamos.obtener_tamanio() == 0:
            await self._cargar_prestamos()

        usuario_a_consultar = await self.__usuario_service.consultar_usuario(id_usuario)

        if not usuario_a_consultar:
            raise ValueError("Error de consulta de préstamos: El usuario a consultar no existe.")
        
        return await self.__prestamo_repositorio.consultar_activo_por_usuario_y_id_libro(id_usuario, isbn_libro)

    async def consultar_prestamo_activo_por_ejemplar(self, id_ejemplar: int) -> Optional[Prestamo]:
        """
        Método que consulta en el repositorio de préstamos sobre si un ejemplar posee un préstamo activo actualmente.\n
        Si existe devuelve ese registro en un objeto de tipo Préstamo, si no es así, se devuelve None.
        """

        if self.__prestamos.obtener_tamanio() == 0:
            await self._cargar_prestamos()

        return await self.__prestamo_repositorio.consultar_activo_por_ejemplar(id_ejemplar)
    
    def consultar_prestamos(self) -> DoublyLinkedList[Prestamo]: 
        return self.__prestamos
    
    async def modificar_fecha_vencimiento_prestamo(self, id: int, fecha: datetime) -> int: 
        """
        Método que desde el repositorio de préstamos, actualiza la fecha de vencimiento de un préstamo.\n
        Si devuelve un número distinto a 0, el préstamo quedo actualizado con su nueva fecha.
        """

        prestamo = await self.consultar_prestamo_por_ID(id)

        if prestamo is None:
            raise ValueError("Error de actualización de préstamo: El préstamo no existe.")

        if fecha <= prestamo.fecha_prestamo:
            raise ValueError("Error de actualización de préstamo: " \
            "La fecha de vencimiento debe ser posterior a la fecha de inicio.")

        id_modificado = await self.__prestamo_repositorio.actualizar_fecha_vencimiento(prestamo.id_prestamo, fecha)

        if id_modificado <= 0:
            raise Exception(f"Error de actualización de préstamo: El préstamo no se modifico.")

        await self._cargar_prestamos()

        return id_modificado      
    
    async def actualizar_estado_prestamo(self, id: int, estado: EstadoPrestamo) -> int: 
        """
        Método que desde el repositorio de préstamos, actualiza el estado de un préstamo.\n
        Si devuelve un número distinto a 0, el préstamo quedo actualizado con su nuevo estado.
        """

        prestamo = await self.consultar_prestamo_por_ID(id)

        if prestamo is None:
            raise ValueError("Error de actualización de préstamo: El préstamo no existe.")

        id_modificado = await self.__prestamo_repositorio.actualizar_estado(id, estado)

        if id_modificado <= 0:
            raise Exception(f"Error de actualización de préstamo: El préstamo no se modifico.")

        await self._cargar_prestamos()

        return id_modificado      

    async def existen_prestamos_vencidos_para_usuario(self, id_usuario: int) -> bool:
        """
        Método que verifica en el repositorio de préstamos, si un usuario posee préstamos vencidos actualmente.
        """

        usuario_a_consultar = await self.__usuario_service.consultar_usuario(id_usuario)

        if not usuario_a_consultar:
            raise ValueError("Error de existencia de préstamos: El usuario a consultar no existe.")
        
        return len(await self.__prestamo_repositorio.consultar_vencidos_por_usuario(id_usuario)) > 0

    async def validar_elegibilidad_usuario(self, id_usuario: int) -> bool: 
        """
        Método que verifica en el repositorio de préstamos, si un usuario es elegible para solicitar préstamos.
        """

        usuario_a_consultar = await self.__usuario_service.consultar_usuario(id_usuario)

        if not usuario_a_consultar:
            raise ValueError("Error de validación de usuario: El usuario a consultar no existe.")
        
        return not await self.existen_prestamos_vencidos_para_usuario(id_usuario)
    
    async def validar_disponibilidad_libro(self, isbn_libro: str) -> bool: 
        """
        Método que verifica si un libro posee copias o ejemplares disponibles para préstamos.
        """

        return await self.__libro_service.esta_disponible(isbn_libro)
    
    async def obtener_plazo_actual_prestamo(self, id: int, id_usuario: int) -> timedelta: 
        """
        Método que desde el repositorio de préstamos, obtiene el plazo actual del préstamo respectivo del usuario.
        """        

        usuario_a_consultar = await self.__usuario_service.consultar_usuario(id_usuario)

        if not usuario_a_consultar:
            raise ValueError("Error de plazo de préstamos: El usuario a consultar no existe.")
        
        prestamo = await self.consultar_prestamo_por_ID(id)

        if prestamo is None:
            raise ValueError("Error de existencia de préstamo: El préstamo respectivo no existe.")

        return prestamo.fecha_vencimiento - datetime.now()
