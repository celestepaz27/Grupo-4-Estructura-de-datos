from typing import Optional
from logica_negocio.interfaces.iautenticacion_service import IAutenticacionService
from acceso_datos.interfaces.iusuario_repositorio import IUsuarioRepositorio
from acceso_datos.modelos.usuarios import Usuario, Sesion
from utilidades.seguridad import verificar_contrasenia


class AutenticacionService(IAutenticacionService):
    """
    Implementación concreta del servicio de autenticación utilizando como estado interno 
    cualquier objeto que tenga la capacidad de aplicar las funciones del repositorio de usuarios.
    """

    def __init__(self, usuario_repositorio: IUsuarioRepositorio):
        self.__usuario_repositorio: IUsuarioRepositorio = usuario_repositorio
        self.__sesion_actual: Optional[Sesion] = None

    async def iniciar_sesion(self, correo: str, clave: str) -> Sesion:
        """
        Método que busca al usuario por su correo y clave, valida esas credenciales y si es así genera un objeto de 
        tipo Sesion que representa a la autenticación.
        """

        credenciales_validas = await self._validar_credenciales(correo, clave)
        
        if not credenciales_validas:
            raise ValueError("Error de autenticación: Correo o contraseña incorrectos.")

        usuario: Usuario = await self.__usuario_repositorio.consultar_por_correo(correo)
        
        nueva_sesion = Sesion(usuario=usuario)
        nueva_sesion.iniciar_sesion() # Cambia el estado interno de la Sesion a Activo y se asigna la fecha de ingreso

        self.__sesion_actual = nueva_sesion
        return self.__sesion_actual

    def cerrar_sesion(self) -> None:
        """Método que cierra la sesión actual si existe una activa"""

        if self.__sesion_actual:
            self.__sesion_actual.cerrar_sesion() # Cambia el estado interno de la Sesion a Inactivo
            self.__sesion_actual = None
        
    def obtener_sesion_actual(self) -> Sesion:
        """Método que retorna la sesión activa actual"""

        if not self.__sesion_actual:
            raise ValueError("No hay ninguna sesión activa en este momento.")
        return self.__sesion_actual

    def obtener_usuario_autenticado(self) -> Usuario:
        """Método que retorna el objeto Usuario (Lector o Bibliotecario) que está usando el sistema."""

        if not self.__sesion_actual:
            raise ValueError("No hay ningún usuario autenticado.")
        return self.__sesion_actual.usuario

    async def _validar_credenciales(self, correo: str, clave: str) -> bool:
        """Método interno protegido que verifica de manera segura las credenciales del usuario."""

        usuario: Optional[Usuario] = await self.__usuario_repositorio.consultar_por_correo(correo)
        
        if not usuario:
            return False 
            
        return verificar_contrasenia(clave, usuario.clave)
