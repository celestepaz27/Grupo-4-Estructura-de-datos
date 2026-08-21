import os
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, List, Optional

# Librerías externas oficiales instaladas 
import aiomysql
from dotenv import load_dotenv

# Se cargan las variables de entorno
load_dotenv()

class Database(ABC):
    """Clase abstracta base agnóstica al motor de datos"""
    
    def __init__(self):
        # Atributos protegidos (#) leídos del entorno con respaldos automáticos
        self._host: str = os.getenv("DB_HOST", "localhost")
        self._puerto: int = int(os.getenv("DB_PORT", 3306))
        self._usuario: str = os.getenv("DB_USER", "root")
        self._clave: str = os.getenv("DB_PASSWORD", "")
        self._nombre_bd: str = os.getenv("DB_NAME", "")
        self._esta_conectado: bool = False

    @abstractmethod
    async def _conectar(self) -> None:
        pass

    @abstractmethod
    async def _desconectar(self) -> None:
        pass

    @abstractmethod
    async def crear(self, tabla: str, datos: dict) -> int:
        pass

    @abstractmethod
    async def leer(self, tabla: str, filtros: dict = None) -> List[dict]:
        pass

    @abstractmethod
    async def actualizar(self, tabla: str, filtros: dict, datos: dict) -> int:
        pass

    @abstractmethod
    async def eliminar(self, tabla: str, filtros: dict) -> int:
        pass

    @abstractmethod
    async def ejecutar_consulta(self, consulta: str, valores: tuple = ()) -> List[dict]:
        pass

    async def __aenter__(self):
        await self._conectar()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self._desconectar()


class MySQLDatabase(Database):
    """Implementación concreta e indestructible con Pool asíncrono de la base de datos"""

    def __init__(self):
        super().__init__()
        self.__pool: Optional[aiomysql.Pool] = None

    async def _conectar(self) -> None:
        """Método protegido que inicializa el pool de conexiones asíncronas una sola vez al arrancar el sistema"""
        if not self._esta_conectado:
            try:
                # Inicialización robusta del Pool con control de contingencias de red
                # Por la propiedad minsize se permite como minimo 2 conexiones dormidas listas para usar
                # Por la propiedad maxsize se permite como máximo 10 conexiones simultáneas
                # Por connect_timeout, si hay una espera a una consulta en la red mayor a 5 segundos, se aborta la espera
                self.__pool = await aiomysql.create_pool(
                    host=self._host,
                    port=self._puerto,
                    user=self._usuario,
                    password=self._clave,
                    db=self._nombre_bd,
                    minsize=2,
                    maxsize=5,  
                    autocommit=True,
                    connect_timeout=5  
                )

                self._esta_conectado = True
                print("[AIOMYSQL] ¡Pool asíncrono real inicializado con éxito.")
            except Exception as e:
                print(f"[AIOMYSQL ERROR] Error inesperado al tratar de iniciar el pool asíncrono: {e}")
                self._esta_conectado = False                
        
    async def _desconectar(self) -> None:
        """Método protegido que destruye el pool y libera por completo los recursos al apagar el programa"""
        if self._esta_conectado and self.__pool:
            self.__pool.close()
            await self.__pool.wait_closed()
            self._esta_conectado = False
            print("[AIOMYSQL] Pool de conexiones liberado de la memoria RAM limpiamente.")

    async def __obtener_conexion_del_pool(self) -> Any:
        """
        Método interno privado para extraer conexiones activas. Retorna una conexion del pool si este está conectado.     
        """

        await self._conectar()  # Autoverifica que el pool siga activo

        if not self._esta_conectado:
            return None
        
        try:
            conexion = await self.__pool.acquire()
            return conexion
        except Exception as e:
            print(f"[AIOMYSQL EERROR] Error al extraer conexión asíncrona del pool: {e}")
            self._esta_conectado = False  # Resetea bandera si la red colapsó totalmente

        return None

    async def crear(self, tabla: str, datos: dict) -> int:
        """
        Método público para aplicar la operación INSERT en una tabla específica con sus datos por diccionario.
        Si devuelve un número distinto de 0 eso quiere decir que se agregaron los registros.
        """
        
        columnas = ", ".join(datos.keys())
        valores_placeholders = ", ".join(["%s"] * len(datos))
        query = f"INSERT INTO {tabla} ({columnas}) VALUES ({valores_placeholders})"

        conexion = await self.__obtener_conexion_del_pool()

        if not conexion:
            return 0 

        try:
            async with conexion:
                async with conexion.cursor() as cursor:
                    await cursor.execute(query, list(datos.values()))
                    await conexion.commit()

                    return cursor.lastrowid if cursor.lastrowid else cursor.rowcount
        except Exception as e:
            print(f"[DB ERROR] Fallo en operación CREAR sobre '{tabla}': {e}")
            return 0

    async def leer(self, tabla: str, filtros: dict = None) -> List[dict]:
        """
        Método público para aplicar la operación SELECT en una tabla específica con sus filtros opcionales por diccionario.
        Devuelve una lista de diccionarios que representa a los datos obtenidos.
        """
        
        query = f"SELECT * FROM {tabla}"
        valores = []
        
        if filtros:
            condiciones = " AND ".join([f"{k} = %s" for k in filtros.keys()])
            query += f" WHERE {condiciones}"
            valores = list(filtros.values())

        conexion = await self.__obtener_conexion_del_pool()

        if not conexion:
            return []
         
        try:
            async with conexion:
                async with conexion.cursor(aiomysql.DictCursor) as cursor:
                    await cursor.execute(query, valores)

                    resultados = await cursor.fetchall()
                    return resultados        
        except Exception as e:
            print(f"[DB ERROR] Fallo en operación LEER sobre '{tabla}': {e}")
            return []

    async def actualizar(self, tabla: str, filtros: dict, datos: dict) -> int:
        """
        Método público para aplicar la operación UPDATE en una tabla específica 
        con sus datos a cambiar y los filtros a aplicar ambos por diccionario.
        Si devuelve un número distinto de 0 eso quiere decir que se actualizaron los registros.
        """
        
        set_query = ", ".join([f"{k} = %s" for k in datos.keys()])
        where_query = " AND ".join([f"{k} = %s" for k in filtros.keys()])
        query = f"UPDATE {tabla} SET {set_query} WHERE {where_query}"
        
        valores = list(datos.values()) + list(filtros.values())
        
        conexion = await self.__obtener_conexion_del_pool()

        if not conexion:
            return 0
        
        try:
            async with conexion:
                async with conexion.cursor() as cursor:
                    await cursor.execute(query, valores)
                    await conexion.commit()

                    filas_afectadas = cursor.rowcount
                    return filas_afectadas
        except Exception as e:
            print(f"[DB ERROR] Fallo en operación ACTUALIZAR sobre '{tabla}': {e}")
            return 0

    async def eliminar(self, tabla: str, filtros: dict) -> int:
        """
        Método público para aplicar la operación DELETE en una tabla específica con sus filtros aplicados por diccionario
        Si devuelve un número distinto de 0 eso quiere decir que se eliminaron los registros.
        """

        where_query = " AND ".join([f"{k} = %s" for k in filtros.keys()])
        query = f"DELETE FROM {tabla} WHERE {where_query}"

        conexion = await self.__obtener_conexion_del_pool()

        if not conexion:
            return 0
        
        try:
            async with conexion:
                async with conexion.cursor() as cursor:
                    await cursor.execute(query, list(filtros.values()))
                    await conexion.commit()

                    filas_afectadas = cursor.rowcount
                    return filas_afectadas
        except Exception as e:
            print(f"[DB ERROR] Fallo en operación ELIMINAR sobre '{tabla}': {e}")
            return 0

    async def ejecutar_consulta(self, consulta, valores = ()) -> List[dict]:
        """
        Método público para ejecutar cualquier consulta SQL avanzada por medio de la operación SELECT. 
        Devuelve una lista de diccionarios que representa a los datos obtenidos.
        """

        # Se determina si la consulta devuelve filas por medio de SELECT
        es_SELECT = consulta.strip().upper().startswith("SELECT")

        if not es_SELECT:
            return []

        conexion = await self.__obtener_conexion_del_pool()

        if not conexion:
            return []
                    
        try:
            async with conexion:
                async with conexion.cursor(aiomysql.DictCursor) as cursor:
                    await cursor.execute(consulta, valores)

                    resultados = await cursor.fetchall()
                    return resultados   
        except Exception as e:
            print(f"[DB ERROR] Fallo en consulta avanzada: {e}\nConsulta: {consulta}")
            return []

    def formatear_fecha_para_db(self, fecha: Optional[datetime]) -> Optional[str]:
        """
        Método que convierte objetos datetime de los modelos a strings compatibles con DATETIME de MySQL.
        Retorna ese string compatible con MySQL.
        """

        if not fecha:
            return None
        return fecha.strftime('%Y-%m-%d %H:%M:%S')

    def convertir_string_a_datetime(self, fecha_str: Any) -> Optional[datetime]:
        """
        Método que transforma datos cronológicos crudos de la DB en objetos datetime puros.
        Retorna un objeto datetime desde la DB.
        """

        if not fecha_str:
            return None
        
        if isinstance(fecha_str, datetime):
            return fecha_str
        
        try:
            return datetime.strptime(str(fecha_str), '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return datetime.strptime(str(fecha_str), '%Y-%m-%d')
