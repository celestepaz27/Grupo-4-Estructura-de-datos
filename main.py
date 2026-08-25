import asyncio
import tkinter as tk
from async_tkinter_loop import async_mainloop, async_handler

from utilidades.configurar_entorno import descargar_env_si_no_existe
from acceso_datos import *
from logica_negocio import *
from vistas import VistaLogin, VistaCatalogo


root = None
sesion_activa = None
accion_actual = "LOGIN"  # Puede ser "LOGIN", "CATALOGO" o "CERRAR_SESION"


_autenticacion_service = None
_usuario_service = None
_categoria_service = None
_ejemplar_service = None
_libro_service = None
_reserva_service = None
_prestamo_service = None
_devolucion_service = None


def procesar_autenticacion_exitosa(sesion: Sesion):
    """Callback síncrono que recibe la sesión y le ordena al bucle principal cambiar de pantalla."""
    global sesion_activa, accion_actual
    sesion_activa = sesion
    accion_actual = "CATALOGO" 


def volver_al_login():
    """Callback síncrono que ordena cerrar la sesión y regresar al formulario inicial."""
    global accion_actual
    _autenticacion_service.cerrar_sesion()
    accion_actual = "CERRAR_SESION" 


def limpiar_root():
    """Borra herméticamente todos los widgets activos de la ventana principal."""
    if root and root.winfo_exists():
        for widget in root.winfo_children():
            widget.destroy()


@async_handler
async def arrancar_aplicacion():
    """Controla el ciclo de vida de la aplicación y renderiza las vistas de forma secuencial."""

    global root, sesion_activa, accion_actual
    global _autenticacion_service, _usuario_service, _categoria_service, _ejemplar_service
    global _libro_service, _reserva_service, _prestamo_service, _devolucion_service

    try:

        descargar_env_si_no_existe()

        async with MySQLDatabase() as database:
            usuario_repositorio = UsuarioRepositorio(database)
            categoria_repositorio = CategoriaRepositorio(database)
            libro_repositorio = LibroRepositorio(database)
            ejemplar_repositorio = EjemplarRepositorio(database)
            prestamo_repositorio = PrestamoRepositorio(database)
            reserva_repositorio = ReservaRepositorio(database)
            devolucion_repositorio = DevolucionRepositorio(database)

            _autenticacion_service = AutenticacionService(usuario_repositorio)
            _usuario_service = UsuarioService(usuario_repositorio)
            _categoria_service = CategoriaService(categoria_repositorio)
            _ejemplar_service = EjemplarService(ejemplar_repositorio)
            _libro_service = LibroService(libro_repositorio, _ejemplar_service, _categoria_service)
            _reserva_service = ReservaService(reserva_repositorio, _libro_service, _usuario_service)
            
            _prestamo_service = PrestamoService(
                prestamo_repositorio, _libro_service, _reserva_service, 
                _usuario_service, _ejemplar_service
            )

            _devolucion_service = DevolucionService(
                devolucion_repositorio, _prestamo_service, _ejemplar_service, _reserva_service
            )

            VistaLogin(root, _autenticacion_service, procesar_autenticacion_exitosa)
            print("[MAIN] Aplicación iniciada. Esperando login...")

            estado_anterior = "LOGIN"
            
            while root and root.winfo_exists():
                await asyncio.sleep(0.05) 

                if accion_actual == "CATALOGO" and estado_anterior != "CATALOGO":

                    limpiar_root()
                    
                    VistaCatalogo(
                        root, sesion_activa, _autenticacion_service, _libro_service,
                        _ejemplar_service, _prestamo_service, _devolucion_service,
                        _reserva_service, _usuario_service, _categoria_service, volver_al_login
                    )
                    estado_anterior = "CATALOGO"
                    print("[MAIN] Catálogo principal inyectado y activo.")

                elif accion_actual == "CERRAR_SESION":

                    limpiar_root()

                    VistaLogin(root, _autenticacion_service, procesar_autenticacion_exitosa)
                    accion_actual = "LOGIN"
                    estado_anterior = "LOGIN"
                    print("[MAIN] Estado reseteado con éxito. Listo para re-autenticar.")

    except Exception as e:
        print(f"[ERROR CRÍTICO EN MAIN]. Ocurrió este error inesperado: {e}")


def main():
    global root  
    root = tk.Tk()
    root.title("Sistema de Gestión Bibliotecaria")

    ancho, alto = 400, 350
    x = int((root.winfo_screenwidth() / 2) - (ancho / 2))
    y = int((root.winfo_screenheight() / 2) - (alto / 2))
    root.geometry(f"{ancho}x{alto}+{x}+{y}")

    root.resizable(False, False)

    root.after(0, arrancar_aplicacion)
    async_mainloop(root)


if __name__ == "__main__":
    main()
