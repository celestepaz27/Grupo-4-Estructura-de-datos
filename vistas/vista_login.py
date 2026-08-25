import tkinter as tk
from tkinter import messagebox
from async_tkinter_loop import async_handler
from logica_negocio import IAutenticacionService


class VistaLogin:
    """Clase encargada de renderizar la interfaz gráfica de login."""
    
    def __init__(self, root: tk.Tk, autenticacion_service: IAutenticacionService, al_autenticar_exitoso):
        self.__root = root
        self.__autenticacion_service = autenticacion_service

        # Callback para avisarle al main.py que debe destruir esta ventana y abrir el catálogo
        self.__al_autenticar_exitoso = al_autenticar_exitoso
        
        self.__inicializar_componentes()

    def __inicializar_componentes(self):
        """Método privado que crea los elementos visuales de la ventana (Labels, Entries y Botones)"""

        for widget in self.__root.winfo_children():
            widget.destroy()

        self.__root.title("Sistema de Gestión Bibliotecaria - Inicio de Sesión")

        ancho, alto = 400, 350
        x = int((self.__root.winfo_screenwidth() / 2) - (ancho / 2))
        y = int((self.__root.winfo_screenheight() / 2) - (alto / 2))
        self.__root.geometry(f"{ancho}x{alto}+{x}+{y}")

        self.__root.resizable(False, False)

        frame_central = tk.Frame(self.__root, padx=30, pady=30)
        frame_central.pack(expand=True, fill="both")

        lbl_titulo = tk.Label(
            frame_central, 
            text="Sistema de Biblioteca", 
            font=("Arial", 18, "bold"),
            fg="#2c3e50"
        )
        lbl_titulo.pack(pady=(0, 20))

        lbl_correo = tk.Label(frame_central, text="Correo Institucional:", font=("Arial", 10))
        lbl_correo.pack(anchor="w", pady=(5, 2))
        
        self.__txt_correo = tk.Entry(frame_central, font=("Arial", 11), width=30)
        self.__txt_correo.pack(ipady=4, pady=(0, 10))
        self.__txt_correo.insert(0, "@edu.upolitecnica.cr")

        lbl_clave = tk.Label(frame_central, text="Contraseña:", font=("Arial", 10))
        lbl_clave.pack(anchor="w", pady=(5, 2))
        
        self.__txt_clave = tk.Entry(frame_central, font=("Arial", 11), width=30, show="*")
        self.__txt_clave.pack(ipady=4, pady=(0, 20))

        self.__btn_ingresar = tk.Button(
            frame_central,
            text="Iniciar Sesión",
            font=("Arial", 11, "bold"),
            bg="#3498db",
            fg="white",
            cursor="hand2",
            command=async_handler(self.__procesar_login)
        )
        self.__btn_ingresar.pack(fill="x", ipady=6)

        self.__txt_correo.focus_set()

    async def __procesar_login(self):
        """
        Método interno que incluye manejador asíncrono que procesa las credenciales ingresadas por el usuario para iniciar sesión.
        """

        correo = self.__txt_correo.get().strip()
        clave = self.__txt_clave.get().strip()

        if not correo or not clave or correo == "@edu.upolitecnica.cr":
            messagebox.showwarning("Campos Vacíos", "Por favor, complete todos los campos de texto.")
            return

        if "@" not in correo:
            messagebox.showwarning("Formato de correo inválido", "Correo con formato inválido. Debe poseer @.")
            return 

        try:
            self.__btn_ingresar.config(state="disabled", text="Autenticando...")
            self.__root.config(cursor="watch")
            
            sesion_activa = await self.__autenticacion_service.iniciar_sesion(correo, clave)

            self.__al_autenticar_exitoso(sesion_activa)

        except ValueError as ve:
            print(f"[UI ERROR] Datos ingresados inválidos: {ve}")
            messagebox.showerror(
                "Acceso Denegado", 
                "El correo o la contraseña son incorrectos.\nVerifique los datos."
            )
        except Exception as ex:
            # Si el connect_timeout=5 se sobrepasa ante esperas excesivas ante la red, cae aquí sin congelarse
            print(f"[UI ERROR] Fallo en el flujo de autenticación: {ex}")
            messagebox.showerror(
                "Error de Conexión", 
                "No se pudo conectar con el servidor.\nIntente de nuevo en unos segundos."
            )
        finally:
            try:
                if self.__root.winfo_exists() and self.__btn_ingresar.winfo_exists():
                    self.__btn_ingresar.config(state="normal", text="Iniciar Sesión")
                    self.__root.config(cursor="")
            except Exception:
                pass
