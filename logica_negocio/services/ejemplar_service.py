from typing import Optional, List
from logica_negocio.interfaces import IEjemplarService
from acceso_datos import IEjemplarRepositorio, Ejemplar, EstadoEjemplar


class EjemplarService(IEjemplarService):
    """Implementación concreta del servicio de ejemplares para la gestión integral de copias de los libros del sistema."""

    def __init__(self, ejemplar_repositorio: IEjemplarRepositorio):
        self.__ejemplar_repositorio = ejemplar_repositorio

    async def registrar_ejemplar(self, ejemplar: Ejemplar) -> int:
        """
        Método que registra un ejemplar en el repositorio de ejemplares para su debida agregación en el sistema.\n
        Si devuelve un número distinto a 0, el ejemplar quedo registrado.\n
        Verifica de forma estricta que el ejemplar esté obligatoriamente asociado a un libro.\n
        """

        if ejemplar.libro_asociado is None:
            raise ValueError("Error de registro de ejemplar: Todo ejemplar debe estar asociado a un libro del catálogo.")

        id_generado = await self.__ejemplar_repositorio.registrar(ejemplar)
        
        if id_generado <= 0:
            raise Exception(f"Error de registro de ejemplar: El ejemplar no se agregó al sistema.")

        return id_generado
    
    async def modificar_estado_ejemplar(self, id: int, estado: EstadoEjemplar) -> int:
        """
        Método que desde el repositorio de ejemplares, se actualiza el estado de disponibilidad o daños de una copia específica.\n
        Si devuelve un número distinto a 0, el ejemplar quedo actualizado.\n
        """

        id_modificado = await self.__ejemplar_repositorio.actualizar_estado(id, estado)

        if id_modificado <= 0:
            raise Exception(f"Error de actualización: El estado del ejemplar no se modificó.")
        
        return id_modificado            

    async def eliminar_ejemplar(self, id: int) -> int:
        """
        Método que desde el repositorio de ejemplares, se elimina un ejemplar del sistema.\n
        Si devuelve un número distinto a 0, el ejemplar quedo finalmente borrado.\n
        """
       
        id_eliminado = await self.__ejemplar_repositorio.eliminar(id)

        if id_eliminado <= 0:
            raise Exception("Error de eliminación: El ejemplar no pudo ser borrado.")

        return id_eliminado

    async def consultar_ejemplar(self, id: int) -> Optional[Ejemplar]:
        """
        Método que consulta en el repositorio de ejemplares sobre la existencia de un ejemplar por su ID.\n
        Si existe devuelve ese registro en un objeto de tipo Ejemplar, si no es así, se devuelve None.\n
        """

        return await self.__ejemplar_repositorio.consultar_por_ID(id)

    async def consultar_ejemplares_por_libro(self, isbn: str) -> List[Ejemplar]:
        """Método que retorna todos los ejemplares asociados a un libro a partir de un ISBN específico."""

        ejemplares_por_libro = await self.__ejemplar_repositorio.consultar_por_libro(isbn)

        return ejemplares_por_libro

    async def consultar_ejemplares_disponibles_por_libro(self, isbn: str) -> List[Ejemplar]:
        """Método que retorna todos los ejemplares DISPONIBLES asociados a un libro a partir de un ISBN específico."""

        ejemplares_disponibles_por_libro = await self.__ejemplar_repositorio.consultar_disponibles_por_libro(isbn)
        
        return ejemplares_disponibles_por_libro

    async def obtener_primer_ejemplar_disponible(self, isbn: str) -> Optional[Ejemplar]:
        """
        Método que extrae la primera copia útil (DISPONIBLE) de un libro para el flujo inmediato de un nuevo préstamo.\n
        Si existe un ejemplar disponible se retorna un objeto de tipo Ejemplar, si no es así se retorna None.
        Eso indica que no existen ejemplares disponibles.
        """

        ejemplares_disponibles_por_libro = await self.__ejemplar_repositorio.consultar_disponibles_por_libro(isbn)

        return ejemplares_disponibles_por_libro[0] if ejemplares_disponibles_por_libro else None
    
    async def existen_ejemplares_disponibles(self, isbn: str) -> bool:
        """
        Método que verifica la existencia de al menos una copia útil (DISPONIBLE) 
        para el flujo necesarios de préstamos y reservas de un libro.
        """

        ejemplares_disponibles_por_libro = await self.__ejemplar_repositorio.consultar_disponibles_por_libro(isbn)

        return len(ejemplares_disponibles_por_libro) > 0
