from typing import Optional, Dict
from logica_negocio.interfaces import IUsuarioService
from logica_negocio.estructuras import DoublyLinkedList
from acceso_datos import Usuario, IUsuarioRepositorio
from utilidades.seguridad import encriptar_contrasenia


class UsuarioService(IUsuarioService):
    """Implementación concreta del servicio de usuarios para la gestión integral de lectores y bibliotecarios."""

    def __init__(self, usuario_repositorio: IUsuarioRepositorio):
        self.__usuario_repositorio = usuario_repositorio
        self.__indices_usuarios: Dict[int, Usuario] = {}

    async def _cargar_usuarios_diccionario(self) -> None:
        """Método que sincroniza la base de datos con el diccionario de indexación para todos los usuarios del sistema."""
        
        lista_usuarios = await self.__usuario_repositorio.consultar_todos()
        self.__indices_usuarios.clear()
        for usuario in lista_usuarios:
            self.__indices_usuarios[usuario.id_usuario] = usuario

    async def registrar_usuario(self, usuario: Usuario) -> int:
        """
        Método que registra un usuario en el repositorio de usuarios para su debida agregación en el sistema.\n
        Si devuelve un número distinto a 0, el usuario quedo registrado.\n
        Verifica de forma estricta que el correo institucional no se encuentre duplicado.\n
        """

        if not self.__indices_usuarios:
            await self._cargar_usuarios_diccionario()

        # Se valida que el correo a ingresar no esté duplicado
        if await self.existe_correo(usuario.correo):
            raise ValueError(f"Error de registro: El correo '{usuario.correo}' ya está registrado.")
        
        usuario_con_clave_hasheada = type(usuario)(
            nombre=usuario.nombre,
            apellido=usuario.apellido,
            clave=encriptar_contrasenia(usuario.clave),
            correo=usuario.correo,
        )

        id_generado = await self.__usuario_repositorio.registrar(usuario_con_clave_hasheada)

        if id_generado <= 0:
            raise Exception(f"Error de registro: El usuario no se agrego al sistema.")

        usuario_con_clave_hasheada.id_usuario = id_generado
        self.__indices_usuarios[id_generado] = usuario_con_clave_hasheada

        return id_generado

    async def eliminar_usuario(self, id: int) -> int:
        """
        Método que desde el repositorio de usuarios, se elimina un usuario del sistema.\n
        Si devuelve un número distinto a 0, el usuario quedo finalmente borrado.\n
        Si existia en el diccionario local, se borra también ese usuario de este.        
        """

        id_eliminado = await self.__usuario_repositorio.eliminar(id)

        if id_eliminado <= 0:
            raise Exception(f"Error de eliminación de usuario: El usuario no se elimino del sistema.")

        self.__indices_usuarios.pop(id, None)

        return id_eliminado

    async def consultar_usuario(self, id: int) -> Optional[Usuario]:
        """
        Método que consulta en el repositorio de usuarios sobre la existencia de un usuario.\n
        Si existe devuelve ese registro en un objeto de tipo Usuario, si no es así, se devuelve None.\n
        Si ya existe busca primero en el diccionario local; si no está, viaja al repositoro de usuarios.        
        """

        if not self.__indices_usuarios:
            await self._cargar_usuarios_diccionario()
            
        if id in self.__indices_usuarios:
            return self.__indices_usuarios[id]

        usuario = await self.__usuario_repositorio.consultar_por_ID(id)

        if usuario:
            self.__indices_usuarios[usuario.id_usuario] = usuario

        return usuario

    async def modificar_usuario(self, id: int, usuario_modificado: Usuario) -> int:
        """
        Método que desde el repositorio de usuarios, se modifica un usuario del sistema.\n
        Si devuelve un número distinto a 0, el usuario quedo actualizado.\n
        Si existia en el diccionario local, se modifica también ese usuario dentro de este.    
        """

        id_modificado = await self.__usuario_repositorio.actualizar(id, usuario_modificado)

        if id_modificado <= 0:
            raise Exception(f"Error de actualización: El usuario no se modifico.")
        
        self.__indices_usuarios[id] = usuario_modificado
        
        return id_modificado

    async def buscar_usuario_por_correo(self, correo: str) -> Optional[Usuario]:
        """
        Método que busca en el repositorio de usuarios sobre la existencia de un usuario por su correo.\n
        Se busca linealmente el objeto en el diccionario local primero. Si no lo encuentra, busca en el repositorio respectivo.\n
        Si existe devuelve ese registro en un objeto de tipo Usuario, si no es así, se devuelve None.\n
        """

        if not self.__indices_usuarios:
            await self._cargar_usuarios_diccionario()

        for usuario in self.__indices_usuarios.values():
            if usuario.correo.strip().lower() == correo.strip().lower():
                return usuario

        usuario = await self.__usuario_repositorio.consultar_por_correo(correo)

        if usuario:
            self.__indices_usuarios[usuario.id_usuario] = usuario

        return usuario

    async def existe_correo(self, correo: str) -> bool:
        """
        Método que verifica si el correo ingresado de un usuario existe ya sea en el diccionario local 
        o en la base de datos respectiva.
        """        

        return await self.buscar_usuario_por_correo(correo) is not None

    async def obtener_usuarios(self) -> DoublyLinkedList[Usuario]:
        """
        Método que transforma el diccionario indexado a una lista enlazada doble (DoublyLinkedList)
        de todos los usuarios del sistema.
        """

        await self._cargar_usuarios_diccionario()
        
        lista_enlazada_doble_usuarios = DoublyLinkedList[Usuario]()

        for usuario in self.__indices_usuarios.values():
            lista_enlazada_doble_usuarios.insertar_al_final(usuario)
            
        return lista_enlazada_doble_usuarios
