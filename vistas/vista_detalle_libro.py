import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from async_tkinter_loop import async_handler

from .vista_gestion_ejemplares import VistaGestionEjemplares

from acceso_datos import Devolucion, Sesion, Libro, Lector
from logica_negocio import (
    ILibroService, 
    IEjemplarService, 
    IPrestamoService, 
    IDevolucionService, 
    IReservaService, 
)


class VistaDetalleLibro:
    """Detalle del libro y acciones según el rol autenticado."""

    def __init__(
        self,
        root,
        sesion: Sesion,
        libro_service: ILibroService,
        ejemplar_service: IEjemplarService,
        prestamo_service: IPrestamoService,
        devolucion_service: IDevolucionService,
        reserva_service: IReservaService,
        libro: Libro,
        volver,
    ):
        self.__root = root
        self.__sesion = sesion
        self.__libro_service = libro_service
        self.__ejemplar_service = ejemplar_service
        self.__prestamo_service = prestamo_service
        self.__devolucion_service = devolucion_service
        self.__reserva_service = reserva_service
        self.__libro = libro
        self.__volver = volver
        self.__inicializar_componentes()

    def __inicializar_componentes(self):
        for widget in self.__root.winfo_children():
            widget.destroy()

        tk.Button(self.__root, text="< Volver al catálogo", command=self.__volver).pack(anchor="w", padx=10, pady=10)

        frame = tk.Frame(self.__root, padx=30, pady=15)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text=self.__libro.titulo, font=("Arial", 20, "bold")).pack(anchor="w", pady=(0, 15))

        for texto in (
            f"ISBN: {self.__libro.isbn}",
            f"Autor: {self.__libro.autor}",
            f"Año: {self.__libro.anio_publicacion}",
            f"Categoría: {self.__libro.categoria_libro.nombre}"
        ):
            tk.Label(frame, text=texto, justify="left", anchor="w").pack(anchor="w", pady=3)

        acciones = tk.Frame(frame)
        acciones.pack(fill="x", pady=20)

        if isinstance(self.__sesion.usuario, Lector):
            tk.Button(
                acciones, 
                text="Solicitar préstamo / reserva", 
                command=async_handler(self.__solicitar_prestamo)).pack(fill="x", pady=4)
            
            tk.Button(
                acciones, 
                text="Solicitar devolución", 
                command=async_handler(self.__solicitar_devolucion)).pack(fill="x", pady=4)
            
        else:
            tk.Button(
                acciones, 
                text="Gestionar ejemplares", 
                command=async_handler(self.__gestionar_ejemplares)).pack(fill="x", pady=4)

            tk.Button(
                acciones, 
                text="Eliminar libro", 
                command=async_handler(self.__eliminar_libro)).pack(fill="x", pady=4)

    async def __solicitar_prestamo(self):
        try:
            await self.__prestamo_service.registrar_prestamo(self.__sesion.usuario, self.__libro)
            messagebox.showinfo("Préstamo", "Préstamo registrado correctamente.")
            self.__volver()
        except ValueError as ex:
            messagebox.showwarning("Solicitud", str(ex))
        except Exception as ex:
            messagebox.showerror("Préstamo", str(ex))

    async def __solicitar_devolucion(self):
        try:
            prestamos = await self.__prestamo_service.consultar_prestamos_activos_por_usuario(
                self.__sesion.usuario.id_usuario
            )

            objetivo = None
            for prestamo in prestamos.recorrer_adelante():
                if prestamo.ejemplar_asociado.libro_asociado.isbn == self.__libro.isbn:
                    objetivo = prestamo
                    break

            if objetivo is None:
                messagebox.showwarning("Devolución", "No existe un préstamo activo de este libro.")
                return

            devolucion = Devolucion(
                prestamo_asociado=objetivo,
                fecha_devolucion_real=datetime.now(),
                descripcion="Devolución solicitada desde el catálogo."
            )

            await self.__devolucion_service.registrar_devolucion(devolucion)
            messagebox.showinfo("Devolución", "Devolución registrada correctamente.")
            self.__volver()
        except Exception as ex:
            messagebox.showerror("Devolución", str(ex))

    async def __gestionar_ejemplares(self):
        ejemplares = await self.__ejemplar_service.consultar_ejemplares_por_libro(self.__libro.isbn)
        VistaGestionEjemplares(
            self.__root,
            self.__sesion,
            self.__ejemplar_service,
            self.__prestamo_service,
            self.__libro,
            ejemplares,
            self.__inicializar_componentes,
        )

    async def __eliminar_libro(self):
        try:
            await self.__libro_service.eliminar_libro(self.__libro.isbn)
            messagebox.showinfo("Libro", "Libro eliminado correctamente.")
            self.__volver()
        except Exception as ex:
            messagebox.showerror("Libro", str(ex))
