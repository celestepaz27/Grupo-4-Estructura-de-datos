import os
from urllib.request import urlopen

URL_ENV = "https://gist.github.com/AndresMontanaro/e04a643a7080591d3f72db93c57cc302/raw/ae7c7dd3e1ee7104e4761e38023de50de98244d1/.env"

def descargar_env_si_no_existe() -> None:

    nombre_archivo = ".env"
    
    if not os.path.exists(nombre_archivo):

        print("Configurando conexión remota por primera vez...")
        
        try:
            with urlopen(URL_ENV, timeout=5) as respuesta:
                contenido = respuesta.read().decode('utf-8')
                
            with open(nombre_archivo, "w", encoding="utf-8") as archivo:
                archivo.write(contenido)
                
            print("Conexión remota configurada con éxito.")
        except Exception as e:
            print(f"Error crítico inesperado al configurar la conexión remota: {e}")
