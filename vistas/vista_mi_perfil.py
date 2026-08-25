import tkinter as tk
from tkinter import messagebox
from logica_negocio import IUsuarioService
from acceso_datos import Sesion


class VistaMiPerfil:
    """Consulta básica del usuario autenticado."""

    def __init__(self, root, sesion: Sesion, usuario_service: IUsuarioService, volver):
        self.__root = root
        self.__sesion = sesion
        self.__usuario_service = usuario_service
        self.__volver = volver
        self.__inicializar_componentes()

    def __inicializar_componentes(self):
        for widget in self.__root.winfo_children():
            widget.destroy()

        tk.Button(self.__root, text="< Volver", command=self.__volver).pack(anchor="w", padx=10, pady=10)
        frame = tk.Frame(self.__root, padx=30, pady=20)
        frame.pack(fill="both", expand=True)

        usuario = self.__sesion.usuario
        tk.Label(frame, text="Mi perfil", font=("Arial", 20, "bold")).pack(anchor="w", pady=(0, 15))
        tk.Label(frame, text=f"Nombre: {usuario.nombre}").pack(anchor="w", pady=4)
        tk.Label(frame, text=f"Apellido: {usuario.apellido}").pack(anchor="w", pady=4)
        tk.Label(frame, text=f"Correo: {usuario.correo}").pack(anchor="w", pady=4)
        tk.Label(frame, text=f"Rol: {type(usuario).__name__}").pack(anchor="w", pady=4)

        tk.Button(
            frame,
            text="Modificar información",
            command=lambda: messagebox.showinfo("Mi perfil", "Formulario de modificación pendiente de integrar.")
        ).pack(fill="x", pady=20)
