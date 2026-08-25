from typing import Optional
from logica_negocio.interfaces import IReservaService, ILibroService, IUsuarioService
from acceso_datos import IReservaRepositorio, Reserva, EstadoReserva
from logica_negocio.estructuras import Cola, DoublyLinkedList, quicksort


class ReservaService(IReservaService):
    """
    Implementación concreta del servicio de reservas para apartados y gestión de colas de espera 
    para solicitudes de libros que no se registran en préstamos debido a la falta de ejemplares disponibles.
    """

    def __init__(self, reserva_repositorio: IReservaRepositorio, libro_service: ILibroService, usuario_service: IUsuarioService):
        self.__reserva_repositorio = reserva_repositorio
        self.__libro_service = libro_service
        self.__usuario_service = usuario_service

        self.__cola_reservas = Cola[Reserva]()

    async def _cargar_cola_reservas(self) -> None:
        """
        Método que cargar en una cola todas las reservas pendientes encoladas siguiendo el orden FIFO.
        """

        reservas_pendientes = await self.__reserva_repositorio.consultar_pendientes()

        reservas_pendientes_ordenadas = quicksort(
            reservas_pendientes,
            key=lambda reserva: reserva.fecha_reserva,
        )

        self.__cola_reservas = Cola[Reserva]()

        for reserva in reservas_pendientes_ordenadas:
            self.__cola_reservas.encolar(reserva)
    
    async def registrar_reserva(self, reserva: Reserva) -> int:
        """
        Método que registra una reserva en el repositorio de reservas para su debida agregación en el sistema.\n
        Representa a la lógica de cuando no hay disponibilidad de ejemplares cuando un Lector desea un préstamo.\n
        Si devuelve un número distinto a 0, la reserva quedo registrada.
        """

        if await self.__libro_service.esta_disponible(reserva.libro_asociado.isbn):
            raise ValueError("Error de registro de reserva: El libro tiene ejemplares disponibles. Solicite préstamo directo.")

        reserva_pendiente = (await self.__reserva_repositorio.consultar_pendiente_por_libro_y_usuario(
                reserva.usuario_asociado.id_usuario,
                reserva.libro_asociado.isbn,
            )
        )

        if reserva_pendiente:
            raise ValueError("Error de registro de reserva: El lector ya posee una reserva pendiente para este libro.")

        id_generado = await self.__reserva_repositorio.registrar(reserva)

        if id_generado <= 0:
            raise Exception("Error de registro de reserva: No se pudo registrar la reserva.")

        await self._cargar_cola_reservas()

        return id_generado
    
    async def cancelar_reserva(self, id: int) -> int: 
        """
        Método que cancela una reserva asignada del repositorio de reservas.\n
        Este tipo de reservas queda excluida de la cola de espera.\n
        Si devuelve un número distinto a 0, la reserva quedo cancelada finalmente.
        """

        reserva = await self.__reserva_repositorio.consultar_por_ID(id)

        if reserva is None:
            raise ValueError("Error de cancelación de reserva: La reserva no existe.")

        if reserva.estado == EstadoReserva.CANCELADA:
            raise ValueError("Error de cancelación de reserva: La reserva ya está cancelada.")

        if reserva.estado == EstadoReserva.ASIGNADA:
            raise ValueError("Error de cancelación de reserva: Una reserva ya asignada no puede cancelarse por este flujo.")

        id_modificado = await self.__reserva_repositorio.actualizar_estado(id, EstadoReserva.CANCELADA)

        if id_modificado <= 0:
            raise Exception("Error de cancelación de reserva: No se pudo cancelar finalmente la reserva.")

        await self._cargar_cola_reservas()

        return id_modificado
    
    async def procesar_siguiente_reserva_pendiente(self, isbn_libro: str) -> Optional[Reserva]:
        """
        Método que procesa y retorna la primera reserva en fila de espera de la cola de un libro.\n
        Si la cola está vacia, retorna None.
        """

        reservas_pendientes = await self.__reserva_repositorio.consultar_pendientes_por_libro(isbn_libro)

        if not reservas_pendientes:
            return None

        reservas_ordenadas = quicksort(
            reservas_pendientes,
            key=lambda reserva: reserva.fecha_reserva
        )

        return reservas_ordenadas[0]
    
    async def consultar_reserva_por_ID(self, id: int) -> Optional[Reserva]: 
        """
        Método que consulta en el repositorio de reservas sobre la existencia de una reserva por su ID.\n
        Si existe devuelve ese registro en un objeto de tipo Reserva, si no es así, se devuelve None.
        """

        if self.__cola_reservas.obtener_tamanio() == 0:
            await self._cargar_cola_reservas()

        return await self.__reserva_repositorio.consultar_por_ID(id)

    async def consultar_reservas(self) -> DoublyLinkedList[Reserva]: 
        """
        Método que consulta en el repositorio de reservas sobre todas las reservas registradas.\n
        Retorna una lista doble enlazada con todos las reservas encontradas.
        """
       
        reservas = await self.__reserva_repositorio.consultar_todas()

        lista_enlazada_doble_reservas = DoublyLinkedList[Reserva]()
        
        for reserva in reservas:
            lista_enlazada_doble_reservas.insertar_al_final(reserva)

        return lista_enlazada_doble_reservas
    
    async def consultar_reservas_pendientes(self) -> DoublyLinkedList[Reserva]: 
        """
        Método que consulta en el repositorio de reservas sobre todas las reservas pendientes registradas.\n
        Retorna una lista doble enlazada con todos las reservas pendientes encontradas.
        """
       
        reservas_pendientes = await self.__reserva_repositorio.consultar_pendientes()

        lista_enlazada_doble_reservas = DoublyLinkedList[Reserva]()
        
        for reserva in reservas_pendientes:
            lista_enlazada_doble_reservas.insertar_al_final(reserva)

        return lista_enlazada_doble_reservas
    
    async def consultar_primera_reserva_pendiente(self) -> Optional[Reserva]: 
        """
        Método que consulta en el repositorio de reservas sobre la existencia de una primera reserva pendiente en orden.\n
        Si existe devuelve ese registro en un objeto de tipo Reserva, si no es así, se devuelve None.
        """

        if self.__cola_reservas.obtener_tamanio() == 0:
            await self._cargar_cola_reservas()

        return await self.__reserva_repositorio.consultar_primera_pendiente()
    
    async def consultar_reserva_pendiente_por_libro_y_usuario(self, id_usuario: int, isbn_libro: str) -> Optional[Reserva]: 
        """
        Método que consulta en el repositorio de reservas sobre la existencia de una reserva pendiente 
        que posee un usuario específico sobre un libro.\n
        Si existe devuelve ese registro en un objeto de tipo Reserva, si no es así, se devuelve None.
        """

        if self.__cola_reservas.obtener_tamanio() == 0:
            await self._cargar_cola_reservas()

        usuario_a_consultar = await self.__usuario_service.consultar_usuario(id_usuario)

        if not usuario_a_consultar:
            raise ValueError("Error de consulta de reservas: El usuario a consultar no existe.")
        
        return await self.__reserva_repositorio.consultar_pendiente_por_libro_y_usuario(id_usuario, isbn_libro)
    
    async def consultar_reservas_pendientes_por_libro(self, isbn_libro: str) -> DoublyLinkedList[Reserva]: 
        """
        Método que consulta en el repositorio de reservas sobre todas las reservas pendientes registradas para un libro.\n
        Retorna una lista doble enlazada con todos las reservas pendientes encontradas asociadas a un libro por su ISBN.
        """
       
        reservas_pendientes_por_libro = await self.__reserva_repositorio.consultar_pendientes_por_libro(isbn_libro)

        lista_enlazada_doble_reservas = DoublyLinkedList[Reserva]()
        
        for reserva in reservas_pendientes_por_libro:
            lista_enlazada_doble_reservas.insertar_al_final(reserva)

        return lista_enlazada_doble_reservas
    
    async def consultar_reservas_pendientes_por_usuario(self, id_usuario: int) -> DoublyLinkedList[Reserva]: 
        """
        Método que consulta en el repositorio de reservas sobre todas las reservas pendientes registradas 
        correspondientes a un usuario.\n
        Retorna una lista doble enlazada con todos las reservas pendientes encontradas asociadas a un usuario por su ID.
        """

        usuario_a_consultar = await self.__usuario_service.consultar_usuario(id_usuario)

        if not usuario_a_consultar:
            raise ValueError("Error de consulta de reservas: El usuario a consultar no existe.")
          
        reservas_pendientes_por_usuario = await self.__reserva_repositorio.consultar_pendientes_por_usuario(id_usuario)

        lista_enlazada_doble_reservas = DoublyLinkedList[Reserva]()
        
        for reserva in reservas_pendientes_por_usuario:
            lista_enlazada_doble_reservas.insertar_al_final(reserva)

        return lista_enlazada_doble_reservas
    
    async def actualizar_estado_reserva(self, id, estado: EstadoReserva) -> int:
        """
        Método que desde el repositorio de reservas, actualiza el estado de una reserva.\n
        Si devuelve un número distinto a 0, la reserva quedo actualizada con su nuevo estado.
        """

        reserva = await self.consultar_reserva_por_ID(id)

        if reserva is None:
            raise ValueError("Error de actualización de reserva: La reserva no existe.")

        id_modificado = await self.__reserva_repositorio.actualizar_estado(id, estado)

        if id_modificado <= 0:
            raise Exception(f"Error de actualización de reserva: La reserva no se modifico.")

        await self._cargar_cola_reservas()

        return id_modificado      
    
    async def existen_reservas_pendientes_para_libro(self, isbn_libro: str) -> bool:
        """
        Método que verifica en el repositorio de reservas, si un libro posee reservas pendientes actualmente.
        """

        return len(await self.__reserva_repositorio.consultar_pendientes_por_libro(isbn_libro)) > 0

    async def existen_reservas_pendientes_para_usuario(self, id_usuario: int) -> bool:
        """
        Método que verifica en el repositorio de reservas, si un usuario posee reservas pendientes actualmente.
        """

        usuario_a_consultar = await self.__usuario_service.consultar_usuario(id_usuario)

        if not usuario_a_consultar:
            raise ValueError("Error de existencia de reservas: El usuario a consultar no existe.")
        
        return len(await self.__reserva_repositorio.consultar_pendientes_por_usuario(id_usuario)) > 0    
