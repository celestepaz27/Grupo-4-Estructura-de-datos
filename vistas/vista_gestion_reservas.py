import tkinter as tk
from tkinter import messagebox
from async_tkinter_loop import async_handler
from logica_negocio import IReservaService


class VistaGestionReservas:
    """Consulta y cancelación de reservas."""

    def __init__(self, root, reserva_service: IReservaService, volver):
        self.__root = root
        self.__reserva_service = reserva_service
        self.__volver = volver
        self.__reservas = []
        self.__inicializar_componentes()

    def __inicializar_componentes(self):
        for widget in self.__root.winfo_children():
            widget.destroy()

        tk.Button(self.__root, text="< Volver", command=self.__volver).pack(anchor="w", padx=10, pady=10)
        tk.Label(self.__root, text="Gestión de reservas", font=("Arial", 18, "bold")).pack(anchor="w", padx=20, pady=10)

        self.__lista = tk.Listbox(self.__root)
        self.__lista.pack(fill="both", expand=True, padx=20, pady=10)

        tk.Button(self.__root, text="Cargar pendientes", command=async_handler(self.__cargar_reservas)).pack(
            fill="x", 
            padx=20, 
            pady=4
        )

        tk.Button(self.__root, text="Cancelar seleccionada", command=async_handler(self.__cancelar_reserva)).pack(
            fill="x", 
            padx=20, 
            pady=4
        )

        self.__root.after(10, async_handler(self.__cargar_reservas))

    async def __cargar_reservas(self):
        try:
            reservas = await self.__reserva_service.consultar_reservas_pendientes()
            self.__reservas = list(reservas.recorrer_adelante())
            self.__lista.delete(0, tk.END)
            for reserva in self.__reservas:
                self.__lista.insert(
                    tk.END, f"#{reserva.id_reserva} | {reserva.usuario_asociado.nombre} {reserva.usuario_asociado.apellido} | \
                    {reserva.libro_asociado.titulo} | {reserva.estado.value}"
                )
        except Exception as ex:
            messagebox.showerror("Reservas", str(ex))

    async def __cancelar_reserva(self):
        seleccion = self.__lista.curselection()
        if not seleccion:
            messagebox.showwarning("Reservas", "Seleccione una reserva.")
            return

        reserva = self.__reservas[seleccion[0]]
        try:
            await self.__reserva_service.cancelar_reserva(reserva.id_reserva)
            messagebox.showinfo("Reservas", "Reserva cancelada.")
            await self.__cargar_reservas()
        except Exception as ex:
            messagebox.showerror("Reservas", str(ex))
