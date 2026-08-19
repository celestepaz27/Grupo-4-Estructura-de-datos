import bcrypt

def encriptar_contrasenia(clave_plana: str) -> str:
    """
    Método que genera un Salt aleatorio y encripta la contraseña.
    Retorna un string listo para la columna de contraseña.
    """

    # Se convierte el string a bytes
    clave_bytes = clave_plana.encode('utf-8')
    
    # Se genera el Salt aleatorio y se aplica el Hash 
    salt = bcrypt.gensalt()
    hash_bytes = bcrypt.hashpw(clave_bytes, salt)
    
    # Se convierte de vuelta a string para usarlo mejor en los repositorios
    return hash_bytes.decode('utf-8')


def verificar_contrasenia(clave_plana: str, hash_almacenado: str) -> bool:
    """
    Método que compara la contraseña que ingrese el usuario con el hash almacenado. Extrae el Salt automáticamente.
    """

    # Se convierten la clave plana y el hash almacenado en bytes
    clave_bytes = clave_plana.encode('utf-8')
    hash_bytes = hash_almacenado.encode('utf-8')
    
    # bcrypt extraerá el Salt del propio hash_bytes y valida si coincide
    return bcrypt.checkpw(clave_bytes, hash_bytes)
