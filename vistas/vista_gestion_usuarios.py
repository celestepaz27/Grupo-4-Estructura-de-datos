import tkinter as tk
from tkinter import messagebox
from async_tkinter_loop import async_handler
from logica_negocio import IUsuarioService


class VistaGestionUsuarios:
    """Ventana administrativa para usuarios."""

    def __init__(self, root, usuario_service: IUsuarioService, volver):
        self.__root = root
        self.__usuario_service = usuario_service
        self.__volver = volver
        self.__usuarios = []
        self.__inicializar_componentes()

    def __inicializar_componentes(self):
        for widget in self.__root.winfo_children():
            widget.destroy()

        tk.Button(self.__root, text="< Volver", command=self.__volver).pack(anchor="w", padx=10, pady=10)
        tk.Label(self.__root, text="Gestión de usuarios", font=("Arial", 18, "bold")).pack(anchor="w", padx=20, pady=10)

        self.__lista = tk.Listbox(self.__root)
        self.__lista.pack(fill="both", expand=True, padx=20, pady=10)

        tk.Button(self.__root, text="Cargar usuarios", command=async_handler(self.__cargar_usuarios)).pack(
            fill="x", 
            padx=20, 
            pady=4
        )

        tk.Button(self.__root, text="Eliminar seleccionado", command=async_handler(self.__eliminar_usuario)).pack(
            fill="x", 
            padx=20, 
            pady=4
        )

        self.__root.after(10, async_handler(self.__cargar_usuarios))

    async def __cargar_usuarios(self):
        try:
            usuarios = await self.__usuario_service.obtener_usuarios()
            self.__usuarios = list(usuarios.recorrer_adelante())
            self.__lista.delete(0, tk.END)
            for usuario in self.__usuarios:
                self.__lista.insert(
                    tk.END, 
                    f"#{usuario.id_usuario} | {usuario.nombre} {usuario.apellido} | {usuario.correo} | {type(usuario).__name__}"
                )
        except Exception as ex:
            messagebox.showerror("Usuarios", str(ex))

    async def __eliminar_usuario(self):
        seleccion = self.__lista.curselection()
        if not seleccion:
            messagebox.showwarning("Usuarios", "Seleccione un usuario.")
            return

        usuario = self.__usuarios[seleccion[0]]
        try:
            await self.__usuario_service.eliminar_usuario(usuario.id_usuario)
            messagebox.showinfo("Usuarios", "Usuario eliminado.")
            await self.__cargar_usuarios()
        except Exception as ex:
            messagebox.showerror("Usuarios", str(ex))
