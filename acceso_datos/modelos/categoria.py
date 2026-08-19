class Categoria:
    """Clase que representa a los objetos de tipo Categoria dentro del sistema."""
    
    def __init__(self, nombre: str, id_categoria: int = -1):
        self.__id_categoria = id_categoria
        self.nombre = nombre

    @property
    def id_categoria(self) -> int:
        return self.__id_categoria

    @property
    def nombre(self) -> str:
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not valor.strip():
            raise ValueError("El nombre de la categoría no puede estar vacío.")
        self.__nombre = valor.strip()
