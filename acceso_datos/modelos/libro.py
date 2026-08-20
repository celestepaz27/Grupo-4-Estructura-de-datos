from .categoria import Categoria


class Libro:
    """Clase que representa a los libros del sistema."""

    def __init__(self, isbn: str, categoria_libro: Categoria, titulo: str, autor: str, anio_publicacion: int):

        if not isbn.strip():
            raise ValueError("El ISBN no puede estar vacio.")
        
        self.__isbn = self.__validar_isbn(isbn.strip())
        self.categoria_libro = categoria_libro
        self.titulo = titulo
        self.autor = autor
        self.anio_publicacion = anio_publicacion

    @property
    def isbn(self) -> str:
        return self.__isbn

    @property
    def categoria_libro(self) -> Categoria:
        return self.__categoria_libro

    @categoria_libro.setter
    def categoria_libro(self, valor: Categoria) -> None:
        if not isinstance(valor, Categoria):
            raise TypeError("El valor de categoria_libro no corresponde a una Categoria.")
        self.__categoria_libro = valor

    @property
    def titulo(self) -> str:
        return self.__titulo

    @titulo.setter
    def titulo(self, valor: str) -> None:
        if not valor.strip():
            raise ValueError("El titulo del libro no puede estar vacío.")
        self.__titulo = valor.strip()

    @property
    def autor(self) -> str:
        return self.__autor

    @autor.setter
    def autor(self, valor: str) -> None:
        if not valor.strip():
            raise ValueError("El autor del libro no puede estar vacío.")
        self.__autor = valor.strip()

    @property
    def anio_publicacion(self) -> int:
        return self.__anio_publicacion

    @anio_publicacion.setter
    def anio_publicacion(self, valor: int) -> None:
        if valor <= 0:
            raise ValueError("El año debe ser mayor que 0.") 
        self.__anio_publicacion = valor

    @staticmethod
    def __validar_isbn(isbn : str) -> str:
        isbn_limpio = isbn.replace("-", "").replace(" ", "")

        if len(isbn_limpio) == 13:
            if not isbn_limpio.isdigit():
                raise ValueError("El ISBN-13 solo puede contener dígitos.")

            suma = sum(
                int(digito) * (1 if posicion % 2 == 0 else 3)
                for posicion, digito in enumerate(isbn_limpio[:12])
            )

            digito_control = (10 - (suma % 10)) % 10

            if int(isbn_limpio[-1]) != digito_control:
                raise ValueError("El ISBN-13 ingresado no es válido.")
            
        else:
            raise ValueError("El ISBN debe tener 13 dígitos.")

        return isbn_limpio
    
    def __lt__(self, otro: 'Libro') -> bool:
        """Método útil para enseñarle al ArbolAVL a comparar libros usando el operador '<' basado en el ISBN."""

        if not isinstance(otro, Libro):
            return NotImplemented
        return self.isbn_libro < otro.isbn_libro

    def __gt__(self, otro: 'Libro') -> bool:
        """Método útil para enseñarle al ArbolAVL a comparar libros usando el operador '>' basado en el ISBN."""
        
        if not isinstance(otro, Libro):
            return NotImplemented
        return self.isbn_libro > otro.isbn_libro
