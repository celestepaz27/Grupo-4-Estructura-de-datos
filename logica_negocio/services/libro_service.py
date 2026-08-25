from typing import Optional, Dict
from logica_negocio.interfaces import ILibroService, IOrdenadorLibros, IBuscadorLibros, IEjemplarService, ICategoriaService
from acceso_datos import ILibroRepositorio, Libro, Categoria
from logica_negocio.estructuras import ArbolAVL, DoublyLinkedList, quicksort, busqueda_binaria


class LibroService(ILibroService, IOrdenadorLibros, IBuscadorLibros):
    """Implementación concreta del servicio de libros para el catálogo centralizado de estos."""

    def __init__(
            self, 
            libro_repositorio: ILibroRepositorio, 
            ejemplar_service: IEjemplarService, 
            categoria_service: ICategoriaService
    ):
        self.__libro_repositorio = libro_repositorio
        self.__ejemplar_service = ejemplar_service
        self.__categoria_service = categoria_service
        
        self.__catalogo_libros: ArbolAVL[Libro] = ArbolAVL[Libro]()
        self.__indices_ISBN: Dict[str, Libro] = {}
        self.__catalogo_ordenado: DoublyLinkedList[Libro] = DoublyLinkedList[Libro]()

    async def _cargar_catalogo_libros(self) -> None:
        """
        Método interno protegido que sincroniza los libros de la base de datos con el Árbol AVL y la lista enlazada doble 
        que representan al catálogo de los libros.
        """

        lista_libros = await self.__libro_repositorio.consultar_todos()

        self.__catalogo_libros = ArbolAVL[Libro]()
        
        for libro in lista_libros:
            self.__catalogo_libros.insertar_nodo(libro)

        self.__catalogo_ordenado = DoublyLinkedList[Libro]()

        for libro in lista_libros:
            self.__catalogo_ordenado.insertar_al_final(libro)

        self._cargar_indices_ISBN()

    def _cargar_indices_ISBN(self) -> None:
        """
        Método interno protegido que puebla el diccionario local de ISBN's a partir de la lista enlazada doble en memoria 
        que posee uno de los catálogo de libros para favorecer a los accesos directos por ISBN.
        """

        self.__indices_ISBN.clear()

        for libro in self.__catalogo_ordenado.recorrer_adelante():
            self.__indices_ISBN[libro.isbn] = libro

    async def registrar_libro(self, libro: Libro) -> int:
        """
        Método que registra un libro en el repositorio de libros para su debida agregación en el sistema.\n
        Si devuelve un número distinto a 0, el libro quedo registrado.\n
        Verifica de forma estricta la unicidad del ISBN dentro del sistema.\n
        """

        if self.__catalogo_ordenado.obtener_tamanio() == 0:
            await self._cargar_catalogo_libros()

        if await self.existe_libro(libro.isbn):
            raise ValueError(f"Error de registro de libro: El libro con ISBN '{libro.isbn}' ya existe.")
        
        id_generado = await self.__libro_repositorio.registrar(libro)

        if id_generado <= 0:
            raise Exception(f"Error de registro de libro: El libro no se agregó al sistema.")

        await self._cargar_catalogo_libros()

        return id_generado
    
    async def modificar_libro(self, isbn: str, libro_modificado: Libro) -> int:
        """
        Método que desde el repositorio de libros, se modifica un libro del sistema.\n
        Si devuelve un número distinto a 0, el libro quedo actualizado.\n
        Si existia en el catálogo, se modifica también ese libro dentro de este.    
        """

        id_modificado = await self.__libro_repositorio.actualizar(isbn, libro_modificado)

        if id_modificado <= 0:
            raise Exception(f"Error de actualización de libro: El libro no se modificó.")

        await self._cargar_catalogo_libros()

        return id_modificado

    async def eliminar_libro(self, isbn: str) -> int:
        """
        Método que desde el repositorio de libros, se elimina un libro del sistema.\n
        Si devuelve un número distinto a 0, el libro quedo finalmente borrado.\n
        Si existia en el catálogo, se borra también ese libro dentro de este.    
        """

        id_eliminado = await self.__libro_repositorio.eliminar(isbn)

        if id_eliminado <= 0:
            raise Exception(f"Error de eliminación de libro: El libro no se eliminó del sistema.")

        await self._cargar_catalogo_libros()

        return id_eliminado
    
    async def consultar_libro(self, isbn: str) -> Optional[Libro]:
        """
        Método que consulta en el repositorio de libros sobre la existencia de un libro.\n
        Si existe devuelve ese registro en un objeto de tipo Libro, si no es así, se devuelve None.\n
        Si ya existe busca primero en el diccionario local; si no está, viaja al repositoro de libros.        
        """

        if self.__catalogo_ordenado.obtener_tamanio() == 0:
            await self._cargar_catalogo_libros()

        if isbn in self.__indices_ISBN:
            return self.__indices_ISBN[isbn]

        return await self.__libro_repositorio.consultar_por_isbn(isbn)

    def buscar_libros(self, criterio: str) -> DoublyLinkedList[Libro]:
        """
        Método que actúa como el buscador universal de libros en el catálogo.\n
        Filtra el catálogo buscando coincidencias por título o autor.\n
        Retorna una lista enlazada doble con los libros encontrados.
        """

        termino = criterio.strip().lower()

        if not termino:
            return self.__catalogo_ordenado

        libros_encontrados = DoublyLinkedList[Libro]()
    
        for libro in self.__catalogo_ordenado.recorrer_adelante():
            if termino in libro.titulo.lower() or termino in libro.autor.lower():
                libros_encontrados.insertar_al_final(libro)
                
        return libros_encontrados

    async def filtrar_libros_por_categoria(self, categoria: Categoria) -> DoublyLinkedList[Libro]:
        """
        Método que filtra por categoría sobre el repositorio de libros ciertos libros.\n
        Retorna una lista enlazada doble con los registros encontrados.        
        """

        categoria_valida = await self.__categoria_service.consultar_categoria(categoria.id_categoria)
        
        if not categoria_valida:
            raise ValueError(f"Error de categoría: La categoría con ID {categoria.id_categoria} no existe.")
                             
        libros_por_categoria = await self.__libro_repositorio.consultar_todos_por_categoria(categoria.id_categoria)

        lista_enlazada_doble_libros = DoublyLinkedList[Libro]()

        for libro in libros_por_categoria:
            lista_enlazada_doble_libros.insertar_al_final(libro)
            
        return lista_enlazada_doble_libros
    
    async def existe_libro(self, isbn: str) -> bool:
        """
        Método que verifica si el ISBN ingresado refleja que un usuario libro existe ya sea en el diccionario local 
        o en la base de datos respectiva.
        """        

        if self.__catalogo_ordenado.obtener_tamanio() == 0:
            await self._cargar_catalogo_libros()

        if isbn in self.__indices_ISBN:
            return True

        return await self.__libro_repositorio.consultar_por_isbn(isbn) is not None
    
    async def obtener_catalogo_libros(self) -> ArbolAVL[Libro]:
        """
        Método que retorna todo el catálogo de libros registrados en el sistema en forma de árbol AVL.
        """        

        if self.__catalogo_ordenado.obtener_tamanio() == 0 or len(self.__indices_ISBN) == 0:
            await self._cargar_catalogo_libros()

        return self.__catalogo_libros

    async def esta_disponible(self, isbn: str) -> bool:
        """
        Método que verifica si un libro mediante su ISBN posee ejemplares DISPONIBLES.
        """        

        return await self.__ejemplar_service.existen_ejemplares_disponibles(isbn)

    def ordenar_por_titulo(self) -> DoublyLinkedList[Libro]:
        """
        Método que ordena los libros en base al titulo y actualiza el orden para el catálogo.
        """

        libros = self.__catalogo_ordenado.recorrer_adelante()

        lista_ordenada_libros = quicksort(libros, key=lambda libro: libro.titulo.lower())

        return self.__refrescar_catalogo(lista_ordenada_libros)

    def ordenar_por_autor(self) -> DoublyLinkedList[Libro]:
        """
        Método que ordena los libros en base al autor y actualiza el orden para el catálogo.
        """

        libros = self.__catalogo_ordenado.recorrer_adelante()

        lista_ordenada_libros = quicksort(libros, key=lambda libro: libro.autor.lower())

        return self.__refrescar_catalogo(lista_ordenada_libros)

    def ordenar_por_ISBN(self) -> DoublyLinkedList[Libro]: 
        """
        Método que ordena los libros en base al ISBN y actualiza el orden para el catálogo.
        """

        libros = self.__catalogo_ordenado.recorrer_adelante()

        lista_ordenada_libros = quicksort(libros, key=lambda libro: libro.isbn)

        return self.__refrescar_catalogo(lista_ordenada_libros)

    def ordenar_por_anio(self) -> DoublyLinkedList[Libro]: 
        """
        Método que ordena los libros en base al año y actualiza el orden para el catálogo.
        """

        libros = self.__catalogo_ordenado.recorrer_adelante()

        lista_ordenada_libros = quicksort(libros, key=lambda libro: libro.anio_publicacion)

        return self.__refrescar_catalogo(lista_ordenada_libros)

    def __refrescar_catalogo(self, libros: list[Libro]) -> DoublyLinkedList[Libro]:
        """
        Método privado que refresca el catálogo de los libros según la colección de libros pasada como argumento 
        y retorna una lista enlazada doble según el orden de esa colección.
        """

        self.__catalogo_ordenado = DoublyLinkedList()

        for libro in libros:
            self.__catalogo_ordenado.insertar_al_final(libro)

        self.__catalogo_libros = ArbolAVL()

        for libro in libros:
            self.__catalogo_libros.insertar_nodo(libro)

        self._cargar_indices_ISBN()

        return self.__catalogo_ordenado

    def buscar_por_ISBN(self, isbn: str) -> Optional[Libro]:
        """
        Método que busca dentro del catálogo ya ordenado, un libro por su ISBN.\n
        Si existe lo devuelve como un objeto Libro, si no existe, devueve None.
        """

        libros_ordenados_por_ISBN = list(self.ordenar_por_ISBN().recorrer_adelante())

        return busqueda_binaria(
            libros_ordenados_por_ISBN, 
            objetivo=isbn.lower(), 
            key=lambda libro: libro.isbn.lower()
        )

    def buscar_por_titulo(self, titulo: str) -> Optional[Libro]:
        """
        Método que busca dentro del catálogo ya ordenado, un libro por su título.\n
        Si existe lo devuelve como un objeto Libro, si no existe, devueve None.
        """

        libros_ordenados_por_titulo = list(self.ordenar_por_titulo().recorrer_adelante())

        return busqueda_binaria(
            libros_ordenados_por_titulo, 
            objetivo=titulo.lower(), 
            key=lambda libro: libro.titulo.lower()
        )

    def buscar_por_autor(self, autor: str) -> DoublyLinkedList[Libro]:
        """
        Método que busca coincidencias parciales por autor recorriendo el catálogo ordenado.\n
        Retorna una lista enlazada doble con todos los libros encontrados del autor.
        """

        self.ordenar_por_autor()

        libros_encontrados_por_titulo = DoublyLinkedList[Libro]()

        for libro in self.__catalogo_ordenado.recorrer_adelante():
            if autor.strip().lower() in libro.autor.lower():
                libros_encontrados_por_titulo.insertar_al_final(libro)

        return libros_encontrados_por_titulo

    def buscar_por_anio(self, anio: int) -> DoublyLinkedList[Libro]:
        """
        Método que busca todos los libros publicados en un año específico recorriendo el catálogo ordenado.\n
        Retorna una lista enlazada doble con todos los libros encontrados de ese año.
        """

        self.ordenar_por_anio()

        libros_encontrados_por_anio = DoublyLinkedList[Libro]()

        for libro in self.__catalogo_ordenado.recorrer_adelante():
            if libro.anio_publicacion == anio:
                libros_encontrados_por_anio.insertar_al_final(libro)

        return libros_encontrados_por_anio
