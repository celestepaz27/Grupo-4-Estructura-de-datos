from typing import List, Optional
from .repositorio_generico import Repositorio
from acceso_datos.interfaces import IUsuarioRepositorio
from acceso_datos.modelos import Usuario, Lector, Bibliotecario
from acceso_datos.conexion_db import Database


class UsuarioRepositorio(Repositorio, IUsuarioRepositorio):
    """
    Implementación concreta del repositorio de usuarios utilizando como estado interno 
    cualquier objeto que sea de la abstracción Database.
    """

    def __init__(self, database: Database):
        super().__init__(database)
        self.__TABLA = "Usuario"

    async def registrar(self, usuario: Usuario) -> int:
        """
        Método que inserta un usuario (Lector o Bibliotecario) en la base de datos.
        Retorna un número que no sea 0 si el registro se realizo.
        """

        tipo = "Bibliotecario" if isinstance(usuario, Bibliotecario) else "Lector"
        
        datos = {
            "nombre": usuario.nombre,
            "apellido": usuario.apellido,
            "clave": usuario.clave,
            "correo": usuario.correo,
            "tipo_usuario": tipo
        }
        
        return await self._database.crear(self.__TABLA, datos)

    async def consultar_por_ID(self, id: int) -> Optional[Usuario]:
        """
        Método que busca un usuario por su ID y retorna la instancia correcta (Lector/Bibliotecario).
        Retorna un posible objeto de tipo Usuario si este existe en la base de datos.
        """

        consulta = """
            SELECT id_usuario, nombre, apellido, correo, tipo_usuario
            FROM Usuario WHERE id_usuario = %s
        """

        resultados = await self._database.ejecutar_consulta(consulta, (id, ))

        if not resultados:
            return None
            
        return self.__mapear_a_objeto(resultados[0])

    async def consultar_por_correo(self, correo: str) -> Optional[Usuario]:
        """
        Método que busca un usuario por su correo electrónico y retorna la instancia correcta (Lector/Bibliotecario).
        Devuelve un posible objeto de tipo Usuario si este existe en la base de datos.
        """

        filtros = {"correo": correo}
        resultados = await self._database.leer(self.__TABLA, filtros)
        
        if not resultados:
            return None
            
        return self.__mapear_a_objeto(resultados[0])

    async def consultar_todos(self) -> List[Usuario]:
        """Método que retorna todos los usuarios registrados en el sistema"""

        consulta = "SELECT id_usuario, nombre, apellido, correo, tipo_usuario FROM Usuario"

        resultados = await self._database.ejecutar_consulta(consulta)
        
        return [self.__mapear_a_objeto(fila) for fila in resultados]

    async def actualizar(self, id: int, usuario: Usuario) -> int:
        """
        Método que actualiza los datos de un usuario existente filtrado por ID.
        Retorna un número que no sea 0 si el registro se actualizo.
        """

        filtros = {"id_usuario": id}
        
        datos = {
            "nombre": usuario.nombre,
            "apellido": usuario.apellido,
        }
        
        return await self._database.actualizar(self.__TABLA, filtros, datos)

    async def eliminar(self, id: int) -> int:
        """
        Método que elimina un usuario de la base de datos por su ID.
        Retorna un número que no sea 0 si el registro se borro.
        """

        filtros = {"id_usuario": id}

        return await self._database.eliminar(self.__TABLA, filtros)

    def __mapear_a_objeto(self, fila: dict) -> Usuario:
        """Método privado que convierte cada fila de los resultados de la DB a un objeto Lector o Bibliotecario real."""

        if fila["tipo_usuario"] == "Bibliotecario":
            return Bibliotecario(
                id_usuario=int(fila["id_usuario"]),
                nombre=fila["nombre"],
                apellido=fila["apellido"],
                clave=fila.get("clave", ""),
                correo=fila["correo"]
            )
        else:
            return Lector(
                id_usuario=int(fila["id_usuario"]),
                nombre=fila["nombre"],
                apellido=fila["apellido"],
                clave=fila.get("clave", ""),
                correo=fila["correo"]
            )
