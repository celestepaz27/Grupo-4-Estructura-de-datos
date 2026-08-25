import tkinter as tk
from tkinter import messagebox
from async_tkinter_loop import async_handler

from .vista_detalle_libro import VistaDetalleLibro
from .vista_mi_perfil import VistaMiPerfil
from .vista_mis_prestamos import VistaMisPrestamos
from .vista_gestion_usuarios import VistaGestionUsuarios
from .vista_gestion_prestamos import VistaGestionPrestamos
from .vista_gestion_reservas import VistaGestionReservas

from acceso_datos import Lector, Bibliotecario, Sesion

from logica_negocio import (
    LibroService,
    IAutenticacionService,
    IEjemplarService,
    IPrestamoService,
    IDevolucionService,
    IReservaService,
    IUsuarioService,
    ICategoriaService
)


class VistaCatalogo:
    """Ventana principal posterior al Login. Cambia opciones según el rol."""

    def __init__(
        self,
        root,
        sesion: Sesion,
        autenticacion_service: IAutenticacionService,
        libro_service: LibroService,
        ejemplar_service: IEjemplarService,
        prestamo_service: IPrestamoService,
        devolucion_service: IDevolucionService,
        reserva_service: IReservaService,
        usuario_service: IUsuarioService,
        categoria_service: ICategoriaService,
        on_logout,
    ):
        self.__root = root
        self.__sesion = sesion
        self.__autenticacion_service = autenticacion_service
        self.__libro_service = libro_service
        self.__ejemplar_service = ejemplar_service
        self.__prestamo_service = prestamo_service
        self.__devolucion_service = devolucion_service
        self.__reserva_service = reserva_service
        self.__usuario_service = usuario_service
        self.__categoria_service = categoria_service
        self.__on_logout = on_logout
        self.__libros_mostrados = []
        self.__inicializar_componentes()

    def __inicializar_componentes(self):
        for widget in self.__root.winfo_children():
            widget.destroy()

        self.__root.title("Sistema de Gestión Bibliotecaria - Catálogo")

        ancho, alto = 1000, 650
        x = int((self.__root.winfo_screenwidth() / 2) - (ancho / 2))
        y = int((self.__root.winfo_screenheight() / 2) - (alto / 2))
        self.__root.geometry(f"{ancho}x{alto}+{x}+{y}")

        self.__root.resizable(True, True)

        self.__crear_navbar()
        self.__crear_catalogo()

    def __crear_navbar(self):
        navbar = tk.Frame(self.__root, relief="raised", bd=1)
        navbar.pack(fill="x")

        tk.Label(
            navbar,
            text=f"Biblioteca | {self.__sesion.usuario.nombre} {self.__sesion.usuario.apellido}",
            font=("Arial", 11, "bold")
        ).pack(side="left", padx=12, pady=8)

        tk.Button(navbar, text="Cerrar sesión", command=self.__cerrar_sesion).pack(side="right", padx=8, pady=5)
        tk.Button(navbar, text="Mi perfil", command=self.__abrir_mi_perfil).pack(side="right", padx=4, pady=5)

        if isinstance(self.__sesion.usuario, Lector):
            tk.Button(navbar, text="Mis préstamos", command=self.__abrir_mis_prestamos).pack(side="right", padx=4, pady=5)
        else:
            tk.Button(navbar, text="Gestión de reservas", command=self.__abrir_gestion_reservas).pack(
                side="right", 
                padx=4, 
                pady=5
            )

            tk.Button(navbar, text="Gestión de préstamos", command=self.__abrir_gestion_prestamos).pack(
                side="right", 
                padx=4, 
                pady=5
            )

            tk.Button(navbar, text="Gestión de usuarios", command=self.__abrir_gestion_usuarios).pack(
                side="right", 
                padx=4, 
                pady=5
            )

    def __crear_catalogo(self):
        contenedor = tk.Frame(self.__root, padx=15, pady=15)
        contenedor.pack(fill="both", expand=True)

        tk.Label(contenedor, text="Catálogo de libros", font=("Arial", 18, "bold")).pack(anchor="w", pady=(0, 12))

        barra = tk.Frame(contenedor)
        barra.pack(fill="x", pady=(0, 10))
        tk.Label(barra, text="Buscar:").pack(side="left")

        self.__txt_busqueda = tk.Entry(barra, width=35)
        self.__txt_busqueda.pack(side="left", padx=6)
        tk.Button(barra, text="Buscar", command=self.__buscar_libros).pack(side="left", padx=3)
        tk.Button(barra, text="Mostrar todos", command=async_handler(self.__cargar_libros)).pack(side="left", padx=3)

        opciones = tk.Frame(contenedor)
        opciones.pack(fill="x", pady=(0, 8))
        tk.Button(opciones, text="Ordenar por título", command=self.__ordenar_titulo).pack(side="left", padx=2)
        tk.Button(opciones, text="Ordenar por autor", command=self.__ordenar_autor).pack(side="left", padx=2)
        tk.Button(opciones, text="Ordenar por ISBN", command=self.__ordenar_isbn).pack(side="left", padx=2)
        tk.Button(opciones, text="Ordenar por año", command=self.__ordenar_anio).pack(side="left", padx=2)

        self.__tabla = tk.Listbox(contenedor, font=("Consolas", 10))
        self.__tabla.pack(fill="both", expand=True)
        self.__tabla.bind("<Double-Button-1>", self.__abrir_libro_seleccionado)

        if isinstance(self.__sesion.usuario, Bibliotecario):
            tk.Button(contenedor, text="Registrar libro", command=self.__registrar_libro).pack(fill="x", pady=(10, 0))

        self.__root.after(10, async_handler(self.__cargar_libros))

    async def __cargar_libros(self):
        try:
            catalogo = await self.__libro_service.obtener_catalogo_libros()
            self.__tabla.delete(0, tk.END)
            self.__libros_mostrados = catalogo.recorrer_In_Orden().recorrer_adelante()
            self.__mostrar_libros(self.__libros_mostrados)
        except Exception as ex:
            print(f"[CATALOGO] Error: {ex}")
            messagebox.showerror("Catálogo", "No se pudieron cargar los libros.")

    def __buscar_libros(self):
        try:
            resultado = self.__libro_service.buscar_libros(self.__txt_busqueda.get().strip())
            self.__libros_mostrados = resultado.recorrer_adelante()
            self.__mostrar_libros(self.__libros_mostrados)
        except Exception as ex:
            messagebox.showerror("Búsqueda", str(ex))

    def __mostrar_libros(self, libros):
        self.__tabla.delete(0, tk.END)
        for libro in libros:
            self.__tabla.insert(
                tk.END,
                f"{libro.isbn} | {libro.titulo} | {libro.autor} | {libro.anio_publicacion}"
            )

    def __ordenar_titulo(self):
        self.__libros_mostrados = self.__libro_service.ordenar_por_titulo().recorrer_adelante()
        self.__mostrar_libros(self.__libros_mostrados)

    def __ordenar_autor(self):
        self.__libros_mostrados = self.__libro_service.ordenar_por_autor().recorrer_adelante()
        self.__mostrar_libros(self.__libros_mostrados)

    def __ordenar_isbn(self):
        self.__libros_mostrados = self.__libro_service.ordenar_por_ISBN().recorrer_adelante()
        self.__mostrar_libros(self.__libros_mostrados)

    def __ordenar_anio(self):
        self.__libros_mostrados = self.__libro_service.ordenar_por_anio().recorrer_adelante()
        self.__mostrar_libros(self.__libros_mostrados)

    def __abrir_libro_seleccionado(self, _event=None):
        seleccion = self.__tabla.curselection()
        if not seleccion:
            return

        libro = self.__libros_mostrados[seleccion[0]]
        VistaDetalleLibro(
            self.__root,
            self.__sesion,
            self.__libro_service,
            self.__ejemplar_service,
            self.__prestamo_service,
            self.__devolucion_service,
            self.__reserva_service,
            libro,
            self.__inicializar_componentes,
        )

    def __registrar_libro(self):
        messagebox.showinfo("CRUD de libros", "Formulario de registro de libro pendiente de integrar.")

    def __abrir_mi_perfil(self):
        VistaMiPerfil(self.__root, self.__sesion, self.__usuario_service, self.__inicializar_componentes)

    def __abrir_mis_prestamos(self):
        VistaMisPrestamos(self.__root, self.__sesion, self.__prestamo_service, self.__inicializar_componentes)

    def __abrir_gestion_usuarios(self):
        VistaGestionUsuarios(self.__root, self.__usuario_service, self.__inicializar_componentes)

    def __abrir_gestion_prestamos(self):
        VistaGestionPrestamos(self.__root, self.__prestamo_service, self.__usuario_service, self.__inicializar_componentes)

    def __abrir_gestion_reservas(self):
        VistaGestionReservas(self.__root, self.__reserva_service, self.__inicializar_componentes)

    def __cerrar_sesion(self):
        self.__autenticacion_service.cerrar_sesion()
        self.__on_logout()
