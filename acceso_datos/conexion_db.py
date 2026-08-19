import os
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, List, Optional

# Librerías externas oficiales instaladas 
from mysql.connector.aio.pooling import MySQLConnectionPool
from mysql.connector import Error
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
        self.__pool: Optional[MySQLConnectionPool] = None

    async def _conectar(self) -> None:
        """Método protegido que inicializa el pool de conexiones asíncronas una sola vez al arrancar el sistema"""
        if not self._esta_conectado:
            try:
                # Inicialización robusta del Pool con control de contingencias de red
                # Por la propiedad pool_size se permite hasta 5 conexiones simultáneas reciclables en la RAM
                # Por la propiedad connection_timeout se corta la conexión tras 5s si el internet se congela
                self.__pool = MySQLConnectionPool(
                    pool_name="biblioteca_pool",
                    pool_size=5,  
                    host=self._host,
                    port=self._puerto,
                    user=self._usuario,
                    password=self._clave,
                    database=self._nombre_bd,
                    connection_timeout=5  
                )
                self._esta_conectado = True
                print("[POOL] Motor asíncrono y Pool de conexiones inicializados.")
            except Error as err:
                print(f"[ERROR] No se pudo inicializar el Pool de base de datos: {err}")
                self._esta_conectado = False
            except Exception as e:
                print(f"[ERROR] Error inesperado al tratar de iniciar el Pool de base de datos: {e}")
                self._esta_conectado = False                

    async def _desconectar(self) -> None:
        """Método protegido que destruye el pool y libera por completo los recursos al apagar el programa"""
        if self._esta_conectado and self.__pool:
            try:
                del self.__pool
                self.__pool = None
                self._esta_conectado = False
                print("[POOL] Pool de conexiones liberado de la memoria RAM limpiamente.")
            except Error as e:
                print(f"[ERROR] Fallo al destruir el pool: {e}")

    async def __obtener_conexion_del_pool(self) -> Any:
        """
        Método interno privado para extraer conexiones activas y tolerar microcortes de Wi-Fi.
        Retorna una conexion del pool si este está conectado.     
        """
        await self._conectar()  # Autoverifica que el pool siga activo

        if self._esta_conectado and self.__pool:
            try:
                conexion = await self.__pool.get_connection()

                # Si la conexión extraída del pool murió por inactividad de red, fuerza reconexión
                if not conexion.is_connected():
                    await conexion.reconnect(attempts=2, delay=1)

                return conexion
            except Error:
                self._esta_conectado = False  # Resetea bandera si la red colapsó totalmente

        return None

    async def crear(self, tabla: str, datos: dict) -> int:
        """
        Método público para aplicar la operación INSERT en una tabla específica con sus datos por diccionario.
        Si devuelve un número distinto de 0 eso quiere decir que se agregaron los registros.
        """

        conexion = await self.__obtener_conexion_del_pool()

        if not conexion:
            return 0
        
        columnas = ", ".join(datos.keys())
        valores_placeholders = ", ".join(["%s"] * len(datos))
        query = f"INSERT INTO {tabla} ({columnas}) VALUES ({valores_placeholders})"
        
        try:
            async with conexion.cursor() as cursor:
                await cursor.execute(query, list(datos.values()))
                last_id = cursor.lastrowid

            await conexion.commit()

            return last_id 
        except Error as err:
            print(f"[DB ERROR] Fallo en operación CREAR sobre '{tabla}': {err}")
            return 0
        finally:
            if conexion:
                await conexion.close()  # Devuelve la conexión viva al Pool inmediatamente

    async def leer(self, tabla: str, filtros: dict = None) -> List[dict]:
        """
        Método público para aplicar la operación SELECT en una tabla específica con sus filtros opcionales por diccionario.
        Devuelve una lista de diccionarios que representa a los datos obtenidos.
        """

        conexion = await self.__obtener_conexion_del_pool()

        if not conexion:
            return []
        
        query = f"SELECT * FROM {tabla}"
        valores = []
        
        if filtros:
            condiciones = " AND ".join([f"{k} = %s" for k in filtros.keys()])
            query += f" WHERE {condiciones}"
            valores = list(filtros.values())
            
        try:
            async with conexion.cursor(dictionary=True) as cursor:
                await cursor.execute(query, valores)
                resultados = await cursor.fetchall()

            return resultados

        except Error as err:
            print(f"[DB ERROR] Fallo en operación LEER sobre '{tabla}': {err}")
            return []
        finally:
            if conexion:
                await conexion.close()

    async def actualizar(self, tabla: str, filtros: dict, datos: dict) -> int:
        """
        Método público para aplicar la operación UPDATE en una tabla específica 
        con sus datos a cambiar y los filtros a aplicar ambos por diccionario.
        Si devuelve un número distinto de 0 eso quiere decir que se actualizaron los registros.
        """

        conexion = await self.__obtener_conexion_del_pool()

        if not conexion:
            return 0
        
        set_query = ", ".join([f"{k} = %s" for k in datos.keys()])
        where_query = " AND ".join([f"{k} = %s" for k in filtros.keys()])
        query = f"UPDATE {tabla} SET {set_query} WHERE {where_query}"
        
        valores = list(datos.values()) + list(filtros.values())
        
        try:
            async with conexion.cursor() as cursor:
                await cursor.execute(query, valores)
                filas_afectadas = cursor.rowcount

            await conexion.commit()

            return filas_afectadas
        except Error as err:
            print(f"[DB ERROR] Fallo en operación ACTUALIZAR sobre '{tabla}': {err}")
            return 0
        finally:
            if conexion:
                await conexion.close()

    async def eliminar(self, tabla: str, filtros: dict) -> int:
        """
        Método público para aplicar la operación DELETE en una tabla específica con sus filtros aplicados por diccionario
        Si devuelve un número distinto de 0 eso quiere decir que se eliminaron los registros.
        """

        conexion = await self.__obtener_conexion_del_pool()

        if not conexion:
            return 0
        
        where_query = " AND ".join([f"{k} = %s" for k in filtros.keys()])
        query = f"DELETE FROM {tabla} WHERE {where_query}"
        
        try:
            async with conexion.cursor() as cursor:
                await cursor.execute(query, list(filtros.values()))
                filas_afectadas = cursor.rowcount

            await conexion.commit()

            return filas_afectadas
        except Error as err:
            print(f"[DB ERROR] Fallo en operación ELIMINAR sobre '{tabla}': {err}")
            return 0
        finally:
            if conexion:
                await conexion.close()

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
                
            async with conexion.cursor(dictionary=True) as cursor:
                await cursor.execute(consulta, valores)
                resultados = await cursor.fetchall()

            return resultados

        except Error as err:
            print(f"[DB ERROR] Fallo en consulta avanzada: {err}\Consulta: {consulta}")
            return []
        finally:
            if conexion:
                await conexion.close()        

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
