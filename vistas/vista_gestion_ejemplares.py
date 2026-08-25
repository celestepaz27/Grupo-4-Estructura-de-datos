import tkinter as tk
from tkinter import messagebox
from typing import List
from async_tkinter_loop import async_handler
from logica_negocio import IEjemplarService, IPrestamoService
from acceso_datos import EstadoEjemplar, Sesion, Ejemplar, Libro


class VistaGestionEjemplares:
    """Gestión básica de ejemplares para un bibliotecario."""

    def __init__(
            self, 
            root, 
            sesion: Sesion, 
            ejemplar_service: IEjemplarService, 
            prestamo_service: IPrestamoService, 
            libro: Libro, 
            ejemplares: List[Ejemplar], 
            volver
        ):
        self.__root = root
        self.__sesion = sesion
        self.__ejemplar_service = ejemplar_service
        self.__prestamo_service = prestamo_service
        self.__libro = libro
        self.__ejemplares = ejemplares
        self.__volver = volver
        self.__inicializar_componentes()

    def __inicializar_componentes(self):
        for widget in self.__root.winfo_children():
            widget.destroy()

        tk.Button(self.__root, text="< Volver", command=self.__volver).pack(anchor="w", padx=10, pady=10)
        
        tk.Label(
            self.__root, 
            text=f"Ejemplares de {self.__libro.titulo}", 
            font=("Arial", 18, "bold")).pack(anchor="w", padx=20, pady=10)

        self.__lista = tk.Listbox(self.__root)
        self.__lista.pack(fill="both", expand=True, padx=20, pady=10)

        for ejemplar in self.__ejemplares:
            self.__lista.insert(tk.END, f"ID: {ejemplar.id_ejemplar} | Estado: {ejemplar.estado.value}")

        botones = tk.Frame(self.__root)
        botones.pack(fill="x", padx=20, pady=10)
        tk.Button(botones, text="Marcar disponible", command=async_handler(self.__marcar_disponible)).pack(side="left", padx=4)
        tk.Button(botones, text="Marcar dañado", command=async_handler(self.__marcar_danado)).pack(side="left", padx=4)
        
        tk.Button(botones, text="Eliminar seleccionado", command=async_handler(self.__eliminar_ejemplar)).pack(
            side="right", 
            padx=4
        )

    def __obtener_seleccionado(self):
        seleccion = self.__lista.curselection()
        return self.__ejemplares[seleccion[0]] if seleccion else None

    async def __marcar_disponible(self):
        ejemplar = self.__obtener_seleccionado()
        if ejemplar is None:
            messagebox.showwarning("Ejemplar", "Seleccione un ejemplar.")
            return
        await self.__ejemplar_service.modificar_estado_ejemplar(ejemplar.id_ejemplar, EstadoEjemplar.DISPONIBLE)
        messagebox.showinfo("Ejemplar", "Estado actualizado.")
        self.__volver()

    async def __marcar_danado(self):
        ejemplar = self.__obtener_seleccionado()
        if ejemplar is None:
            messagebox.showwarning("Ejemplar", "Seleccione un ejemplar.")
            return
        await self.__ejemplar_service.modificar_estado_ejemplar(ejemplar.id_ejemplar, EstadoEjemplar.DAÑADO)
        messagebox.showinfo("Ejemplar", "Estado actualizado.")
        self.__volver()

    async def __eliminar_ejemplar(self):
        ejemplar = self.__obtener_seleccionado()
        if ejemplar is None:
            messagebox.showwarning("Ejemplar", "Seleccione un ejemplar.")
            return
        try:
            await self.__ejemplar_service.eliminar_ejemplar(ejemplar.id_ejemplar)
            messagebox.showinfo("Ejemplar", "Ejemplar eliminado.")
            self.__volver()
        except Exception as ex:
            messagebox.showerror("Ejemplar", str(ex))
