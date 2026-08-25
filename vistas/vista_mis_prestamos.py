import tkinter as tk
from tkinter import messagebox
from async_tkinter_loop import async_handler
from logica_negocio import IPrestamoService
from acceso_datos import Sesion


class VistaMisPrestamos:
    """Listado de préstamos del lector."""

    def __init__(self, root, sesion: Sesion, prestamo_service: IPrestamoService, volver):
        self.__root = root
        self.__sesion = sesion
        self.__prestamo_service = prestamo_service
        self.__volver = volver
        self.__inicializar_componentes()

    def __inicializar_componentes(self):
        for widget in self.__root.winfo_children():
            widget.destroy()

        tk.Button(self.__root, text="< Volver", command=self.__volver).pack(anchor="w", padx=10, pady=10)
        tk.Label(self.__root, text="Mis préstamos", font=("Arial", 18, "bold")).pack(anchor="w", padx=20, pady=10)
        self.__lista = tk.Listbox(self.__root)
        self.__lista.pack(fill="both", expand=True, padx=20, pady=10)
        self.__cargar_prestamos()

    @async_handler
    async def __cargar_prestamos(self):
        try:
            prestamos = await self.__prestamo_service.consultar_prestamos_por_usuario(self.__sesion.usuario.id_usuario)
            self.__lista.delete(0, tk.END)
            for prestamo in prestamos.recorrer_adelante():
                self.__lista.insert(
                    tk.END,
                    f"#{prestamo.id_prestamo} | {prestamo.ejemplar_asociado.libro_asociado.titulo} | \
                    {prestamo.estado.value} | Vence: {prestamo.fecha_vencimiento:%Y-%m-%d}"
                )
        except Exception as ex:
            messagebox.showerror("Préstamos", str(ex))
