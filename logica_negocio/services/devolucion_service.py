from typing import Optional, List
from logica_negocio.interfaces import IDevolucionService, IPrestamoService, IEjemplarService, IReservaService 
from acceso_datos import IDevolucionRepositorio, Devolucion, EstadoEjemplar, EstadoPrestamo, EstadoReserva


class DevolucionService(IDevolucionService):
    """Implementación concreta del servicio de devoluciones."""

    def __init__(
            self, 
            devolucion_repositorio: IDevolucionRepositorio, 
            prestamo_service: IPrestamoService, 
            ejemplar_service: IEjemplarService, 
            reserva_service: IReservaService
    ):
        self.__devolucion_repositorio = devolucion_repositorio
        self.__prestamo_service = prestamo_service
        self.__ejemplar_service = ejemplar_service
        self.__reserva_service = reserva_service

    async def registrar_devolucion(self, devolucion: Devolucion) -> int:
        """
        Método que registra una devolución en el repositorio de devoluciones tras la solicitud de devolución sobre un préstamo.\n
        Si devuelve un número distinto a 0, la devolución quedo registrada.\n
        Mientras la devolución se registra, el préstamo respectivo se actualizado con el estado de FINALIZADO,
        el ejemplar asociado a este se actualiza con el estado de DISPONIBLE, y finalmente se procesa la siguiente 
        """

        prestamo_asociado = await self.__prestamo_service.consultar_prestamo_por_ID(devolucion.prestamo_asociado.id_prestamo)

        if not prestamo_asociado:
            raise ValueError("Error de devolución: El préstamo respectivo no existe.")

        if prestamo_asociado.estado not in (EstadoPrestamo.ACTIVO, EstadoPrestamo.VENCIDO):
            raise ValueError("Error de estados: Solo podrán devolverse préstamos de libros activos o vencidos.")

        if devolucion.fecha_devolucion_real <= prestamo_asociado.fecha_prestamo:
            raise ValueError("Error de devolución: La fecha de devolución debe ser posterior a la fecha de préstamo.")
      
        id_generado = await self.__devolucion_repositorio.registrar(devolucion)

        if id_generado <= 0:
            raise Exception(f"Error de registro de devolución: La devolución no se agrego al sistema.")

        fecha_actualizada = await self.__prestamo_service.devolver_prestamo(prestamo_asociado.id_prestamo)

        if fecha_actualizada <= 0:
            raise Exception("Error de registro de devolución: No se pudo registrar la fecha de devolución del préstamo.")

        id_prestamo_modificado = await self.__prestamo_service.actualizar_estado_prestamo(
            prestamo_asociado.id_prestamo,
            EstadoPrestamo.FINALIZADO
        )

        if id_prestamo_modificado <= 0:
            raise Exception("Error de actualización de préstamo: \
                            El estado del préstamo no se modifico tras registrar su respectiva devolución.")
        
        id_ejemplar_modificado = await self.__ejemplar_service.modificar_estado_ejemplar(
            prestamo_asociado.ejemplar_asociado.id_ejemplar,
            EstadoEjemplar.DISPONIBLE
        )
        
        if id_ejemplar_modificado <= 0:
            raise Exception(f"Error de actualización de ejemplar: \
                            El estado del ejemplar no se modifico tras registrar su respectiva devolución.")

        primera_reserva_pendiente = await self.__reserva_service.procesar_siguiente_reserva_pendiente(
            prestamo_asociado.ejemplar_asociado.libro_asociado.isbn
        )

        if primera_reserva_pendiente:
            nuevo_prestamo = await self.__prestamo_service.registrar_prestamo(
                primera_reserva_pendiente.usuario_asociado,
                primera_reserva_pendiente.libro_asociado
            )

            if nuevo_prestamo is None:
                raise Exception("Error de registro de préstamo." \
                "El nuevo préstamo que era anteriormente la primera reserva pendiente no fue registrada.")

            id_reserva_modificada = await self.__reserva_service.actualizar_estado_reserva(
                primera_reserva_pendiente.id_reserva, 
                EstadoReserva.ASIGNADA
            )

            if id_reserva_modificada <= 0:
                raise Exception("Error de actualización de reserva: La reserva finalmente no se asigno.")
        
        return id_generado
    
    async def obtener_devolucion_por_ID(self, id: int) -> Optional[Devolucion]:
        """
        Método que consulta en el repositorio de devoluciones sobre la existencia de una devolución por su ID.\n
        Si existe devuelve ese registro en un objeto de tipo Devolucion, si no es así, se devuelve None.
        """

        return await self.__devolucion_repositorio.consultar_por_ID(id)
    
    async def obtener_devolucion_por_prestamo(self, id_prestamo: int) -> Optional[Devolucion]:
        """
        Método que consulta en el repositorio de devoluciones sobre la existencia de una devolución 
        en base al préstamo al que está asociado.\n
        Si existe devuelve ese registro en un objeto de tipo Devolucion, si no es así, se devuelve None.
        """ 

        prestamo_asociado = await self.__prestamo_service.consultar_prestamo_por_ID(id_prestamo)

        if not prestamo_asociado:
            raise ValueError("Error de devolución: El préstamo respectivo no existe.")

        return await self.__devolucion_repositorio.consultar_por_prestamo(prestamo_asociado.id_prestamo)

    async def listar_devoluciones(self) -> List[Devolucion]:
        """
        Método que consulta en el repositorio de devoluciones sobre todas las devoluciones existentes.\n
        Retorna una lista con todos los registros encontrados.
        """

        return await self.__devolucion_repositorio.consultar_todas()
