# Grupo-4-Estructura-de-datos

### 📚 Sistema Asíncrono de Gestión Bibliotecaria

Este sistema de software fue desarrollado como proyecto final para el curso **Estructura de Datos (90401)** de la **Universidad Politécnica Internacional**. La aplicación implementa una arquitectura desacoplada por capas que combina interfaces gráficas asíncronas en tiempo real, estructuras de datos avanzadas en la memoria RAM y persistencia relacional en la nube. 

### 🛠️ Tecnologías Utilizadas

* **Lenguaje:** Python 3.13+
* **Interfaz Gráfica:** Tkinter (Nativo de Python)
* **Bucle de Eventos Gráficos:** async-tkinter-loop
* **Controlador de Base de Datos:** aiomysql (Persistencia asíncrona)
* **Motor Remoto de Base de Datos:** MySQL (Alojado en la nube de Railway)
* **Encriptación de Credenciales:** Bcrypt

### 🏗️ Estructuras de Datos Aplicadas (RAM Core)

El sistema cumple rigurosamente con los requerimientos del curso al movilizar tres familias distintas de estructuras de datos en la memoria intermedia: 

1. **Estructura Lineal Bidireccional (DoublyLinkedList):** Utilizada como la caché central del catálogo para renderizar flujos secuenciales y poblar los componentes de la interfaz de forma eficiente.
2. **Estructura Lineal FIFO (Cola):** Implementada a mano para gestionar el orden estricto de registro de las solicitudes de libros en el módulo de reservas.
3. **Estructura No Lineal Jerárquica (ArbolAVL):** Indexa el catálogo completo por el código ISBN del libro para permitir búsquedas y balanceos automáticos de nodos en tiempo logarítmico 𝑂(log 𝑛).

### ⚡ Algoritmia Avanzada Implementada

* **Ordenamiento Eficiente (Quicksort):** Se aplica la pila recursiva de Quicksort directamente sobre los iteradores de la memoria RAM para reordenar dinámicamente las listas por criterios de Título, Autor, Año o ISBN en tiempo 𝑂(𝑛log 𝑛)
.
* **Búsqueda Avanzada (Búsqueda Binaria):** Utilizada para localizar registros exactos en colecciones previamente ordenadas, dividiendo el espacio de búsqueda a la mitad en cada iteración.

### 🚀 Instrucciones de Instalación y Despliegue

Se deben seguir estos pasos humanos en la terminal para levantar el entorno de desarrollo: 

### 1. Clonar el repositorio

```bash
git clone https://github.com/celestepaz27/Grupo-4-Estructura-de-datos.git
cd Grupo-4-Estructura-de-datos
```

Usa el código con precaución.

### 2. Activar el entorno virtual (`.venv`)
Levanta tu entorno virtual aislado de Windows por medio de python -m venv .venv para asegurar que las dependencias asíncronas corran en su propio contenedor. Posteriormente digite este comando:

```bash
.venv\Scripts\activate
```

### 3. Instalar las dependencias de red indispensables

Asegúrate de instalar las librerías encargadas de orquestar el asincronismo y la encriptación de datos: 

bash

pip install aiomysql bcrypt async-tkinter-loop

### 4. Lanzar la aplicación principal

Inicia el orquestador global del ciclo de vida del software: 

```bash
python main.py
```
