import tkinter as tk
from async_tkinter_loop import async_handler

from tkinter import messagebox, simpledialog
from datetime import datetime
from logica_negocio import IPrestamoService, IUsuarioService


class VistaGestionPrestamos:
    """Consulta de préstamos por lector y modificación de vencimiento."""

    def __init__(self, root, prestamo_service: IPrestamoService, usuario_service: IUsuarioService, volver):
        self.__root = root
        self.__prestamo_service = prestamo_service
        self.__usuario_service = usuario_service
        self.__volver = volver
        self.__prestamos = []
        self.__inicializar_componentes()

    def __inicializar_componentes(self):
        for widget in self.__root.winfo_children():
            widget.destroy()

        tk.Button(self.__root, text="< Volver", command=self.__volver).pack(anchor="w", padx=10, pady=10)
        tk.Label(self.__root, text="Gestión de préstamos", font=("Arial", 18, "bold")).pack(anchor="w", padx=20, pady=10)

        barra = tk.Frame(self.__root)
        barra.pack(fill="x", padx=20)
        tk.Label(barra, text="ID lector:").pack(side="left")
        self.__txt_usuario = tk.Entry(barra, width=15)
        self.__txt_usuario.pack(side="left", padx=5)
        tk.Button(barra, text="Consultar", command=async_handler(self.__consultar_prestamos)).pack(side="left")

        self.__lista = tk.Listbox(self.__root)
        self.__lista.pack(fill="both", expand=True, padx=20, pady=15)
        tk.Button(self.__root, text="Modificar vencimiento", command=self.__modificar_vencimiento).pack(
            fill="x", 
            padx=20, 
            pady=(0, 10)
        )

    async def __consultar_prestamos(self):
        try:
            id_usuario = int(self.__txt_usuario.get())
            prestamos = await self.__prestamo_service.consultar_prestamos_por_usuario(id_usuario)
            self.__prestamos = list(prestamos.recorrer_adelante())
            self.__lista.delete(0, tk.END)
            for prestamo in self.__prestamos:
                self.__lista.insert(
                    tk.END, 
                    f"#{prestamo.id_prestamo} | {prestamo.ejemplar_asociado.libro_asociado.titulo} \
                      | {prestamo.estado.value} | Vence: {prestamo.fecha_vencimiento:%Y-%m-%d}"
                )
        except Exception as ex:
            messagebox.showerror("Préstamos", str(ex))

    def __modificar_vencimiento(self):
        seleccion = self.__lista.curselection()
        if not seleccion:
            messagebox.showwarning("Préstamos", "Seleccione un préstamo.")
            return

        nueva_fecha = simpledialog.askstring(
            "Nuevo vencimiento",
            "Digite la nueva fecha (YYYY-MM-DD):"
        )

        if not nueva_fecha:
            return

        try:
            fecha = datetime.strptime(nueva_fecha, "%Y-%m-%d")
            prestamo = self.__prestamos[seleccion[0]]
            self.__ejecutar_modificacion(prestamo.id_prestamo, fecha)
        except ValueError:
            messagebox.showerror("Fecha", "Formato inválido. Use YYYY-MM-DD.")

    def __ejecutar_modificacion(self, id_prestamo, fecha):
        import asyncio

        async def operar_modificacion():
            try:
                await self.__prestamo_service.modificar_fecha_vencimiento_prestamo(id_prestamo, fecha)
                messagebox.showinfo("Préstamos", "Fecha de vencimiento actualizada.")
                await self.__consultar_prestamos()
            except Exception as ex:
                messagebox.showerror("Préstamos", str(ex))

        asyncio.create_task(operar_modificacion())
