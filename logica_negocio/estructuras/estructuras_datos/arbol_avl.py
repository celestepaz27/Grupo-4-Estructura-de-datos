from typing import Optional, TypeVar, Generic
from .lista_enlazada_doble import DoublyLinkedList

T = TypeVar('T')


class NodoAVL(Generic[T]):
    """
    Clase que representa a cada nodo que formara parte de un árbol AVL (ArbolAVL[T]). 
    Cada nodo es representado por NodoAVL[T].
    """

    def __init__(self, dato: T):
        self.dato: T = dato
        self.izquierda: Optional['NodoAVL[T]'] = None
        self.derecha: Optional['NodoAVL[T]'] = None
        self.altura: int = 1

    @property
    def dato(self) -> T:
        return self.__dato

    @dato.setter
    def dato(self, valor: T) -> None:
        self.__dato = valor

    @property
    def izquierda(self) -> Optional['NodoAVL[T]']:
        return self.__izquierda

    @izquierda.setter
    def izquierda(self, nodo: Optional['NodoAVL[T]']) -> None:
        self.__izquierda = nodo

    @property
    def derecha(self) -> Optional['NodoAVL[T]']:
        return self.__derecha

    @derecha.setter
    def derecha(self, nodo: Optional['NodoAVL[T]']) -> None:
        self.__derecha = nodo

    @property
    def altura(self) -> int:
        return self.__altura

    @altura.setter
    def altura(self, valor: int) -> None:
        self.__altura = valor


class ArbolAVL(Generic[T]):
    """
    Clase que representa a un árbol AVL, la cual recibe en su estructura varios objetos de tipo NodoAVL[T]. 
    Cada árbol es representado por ArbolAVL[T]. Esta estructura aplica auto-balanceo de los datos.
    """

    def __init__(self):
        self.__raiz: Optional[NodoAVL[T]] = None

    def insertar_nodo(self, valor: T) -> None:
        """
        Método público que insertará un nodo en el árbol a partir de un valor.
        """

        self.__raiz = self.__insertar(self.__raiz, valor)

    def eliminar_nodo(self, valor: T) -> None:
        """
        Método público que eliminará un nodo del árbol a partir de un valor.
        """

        self.__raiz = self.__eliminar(self.__raiz, valor)

    def buscar_nodo(self, valor: T) -> Optional[T]:
        """
        Método público que buscara un nodo del árbol a partir de un valor. Si lo encuentra lo retorna.
        """

        nodo = self.__buscar(self.__raiz, valor)
        return nodo.dato if nodo else None

    def obtener_minimo(self) -> Optional[T]:
        """
        Método público que retorna el valor del nodo que tiene el valor más pequeño del árbol si existe.\n
        Este nodo se caracteriza por ser un nodo totalmente ubicado en los subárboles respectivos izquierdos.\n
        """

        if not self.__raiz:
            return None
        nodo = self.__obtener_nodo_minimo(self.__raiz)
        return nodo.dato

    def obtener_maximo(self) -> Optional[T]:
        """
        Método público que retorna el valor del nodo que posee el valor más grande del árbol si existe.\n
        Este nodo se caracteriza por ser un nodo totalmente ubicado en los subárboles respectivos derechos.
        """
        
        if not self.__raiz:
            return None
        actual = self.__raiz
        while actual.derecha:
            actual = actual.derecha
        return actual.dato

    def recorrer_In_Orden(self) -> DoublyLinkedList[T]:
        """
        Método público que recorrerá todo el árbol siguiendo el recorrido In-Order.\n
        Retorna los elementos del árbol en una lista enlazada doble (DoublyLinkedList[T]) ordenada de menor a mayor. 
        """

        lista = DoublyLinkedList[T]()
        self.__in_orden_recursivo(self.__raiz, lista)
        return lista

    def recorrer_Pre_Orden(self) -> DoublyLinkedList[T]:
        """
        Método público que recorrerá todo el árbol siguiendo el recorrido Pre-Order.\n
        Retorna los elementos del árbol en una lista enlazada doble (DoublyLinkedList[T]) siguiendo el mismo orden del árbol. 
        """

        lista = DoublyLinkedList[T]()
        self.__pre_orden_recursivo(self.__raiz, lista)
        return lista

    def recorrer_Post_Orden(self) -> DoublyLinkedList[T]:
        """
        Método público que recorrerá todo el árbol siguiendo el recorrido Post-Order.\n
        Retorna los elementos del árbol en una lista enlazada doble (DoublyLinkedList[T])
        siguiendo el orden como si se borrará el árbol. 
        """

        lista = DoublyLinkedList[T]()
        self.__post_orden_recursivo(self.__raiz, lista)
        return lista

    def __insertar(self, nodo: Optional[NodoAVL[T]], valor: T) -> NodoAVL[T]:
        """
        Este método inserta un nodo en el árbol a partir de otro.\n
        Funciona mediante recursión donde en la busqueda se guardan los pasos en una pila de ejecución.\n
        Si el valor del nodo a añadir es menor que el nodo actual, se ejecuta self.__insertar(nodo.izquierda, valor).
        Si es mayor, va a la derecha. Se sigue ese ciclo bajando escalón por escalón.\n
        Cuando se llega a un brazo vacío (None), se crea físicamente el objeto NodoAVL(valor) en la RAM y lo conecta en el flujo.\n
        El árbol se auto-balancea por cada nodo desde la última llamada hasta la primera del método actual.
        """

        if not nodo:
            return NodoAVL(valor)

        if valor < nodo.dato:
            nodo.izquierda = self.__insertar(nodo.izquierda, valor)
        elif valor > nodo.dato:
            nodo.derecha = self.__insertar(nodo.derecha, valor)
        else:
            return nodo  

        return self.__balancear(nodo)

    def __eliminar(self, nodo: Optional[NodoAVL[T]], valor: T) -> Optional[NodoAVL[T]]:
        """
        Este método trata de eliminar un nodo en el árbol a partir de otro.\n
        Funciona mediante recursión donde se va guardando los pasos en una pila de ejecución.\n
        Si el valor del nodo a buscar es menor que el nodo actual, se apila self.__eliminar(nodo.izquierda, valor).
        Si es mayor, se apila self.__eliminar(nodo.derecha, valor). Se sigue ese ciclo bajando escalón por escalón.\n
        
        Cuando se encuentra el nodo a eliminar, se siguen estos 3 posibles flujos:
        - Caso 1: El nodo no tiene hijos, donde se devuelve None en ese caso ya eliminado el nodo respectivo.
        - Caso 2. El nodo solo tiene un hijo vivo, donde se destruye el enlace del nodo a borrar y sube el hijo que quedó vivo.
        - Caso 3. El nodo posee dos hijos. Es un caso complejo y requiere de estos pasos:
            1. Se llama a self.__obtener_nodo_minimo(nodo.derecha) para buscar al sucesor inmediato que representa
               al nodo más pequeño de toda la rama derecha.
            2. Se copia el valor de ese sucesor y se reemplaza por encima del nodo a borrar.
            3. Para eliminar el nodo duplicado que quedó abajo, se vuelve a llamar a self.__eliminar(nodo.derecha, sucesor.dato).
            4. Finalmente se auto-balancea toda la estructura.

        Retorna el nodo finalmente eliminado del flujo si existia.
        """

        if not nodo:
            return None

        if valor < nodo.dato:
            nodo.izquierda = self.__eliminar(nodo.izquierda, valor)
        elif valor > nodo.dato:
            nodo.derecha = self.__eliminar(nodo.derecha, valor)
        else:
            # Caso 1 o 2: Nodo con un solo hijo o sin hijos
            if not nodo.izquierda:
                return nodo.derecha
            elif not nodo.derecha:
                return nodo.izquierda

            # Caso 3: Nodo con dos hijos. Se busca el sucesor inmediato (mínimo a la derecha)
            sucesor = self.__obtener_nodo_minimo(nodo.derecha)
            nodo.dato = sucesor.dato
            nodo.derecha = self.__eliminar(nodo.derecha, sucesor.dato)

        return self.__balancear(nodo)

    def __buscar(self, nodo: Optional[NodoAVL[T]], valor: T) -> Optional[NodoAVL[T]]:
        """
        Este método tratar de encontrar un posible nodo en el árbol por medio de su valor, basandose de otro nodo.\n

        Se aplica el recorrido sobre el árbol por medio de recursión donde se apilan llamadas hasta encontrar el valor a buscar.\n

        Si no se encontro, se retorna None, si se encontro devuelve el nodo específico con el valor. Desde ahi se desapilan las
        llamadas desde donde se encontro valor (si fue encontrado) hasta la raíz. 
        """
                
        if not nodo or nodo.dato == valor:
            return nodo
        if valor < nodo.dato:
            return self.__buscar(nodo.izquierda, valor)
        return self.__buscar(nodo.derecha, valor)

    def __rotacion_izquierda(self, x: NodoAVL[T]) -> NodoAVL[T]:
        """
        Este método se activa cuando el árbol se cae de más hacia el brazo derecho.\n
        El parametro x representa a un nodo el cual posee el valor más bajo de todo el árbol,
        pero si sus nodos hijos o subárboles son valores que parten de ahí totalmente de manera ascendente, 
        se aplica esta rotación.\n
        Esta rotación permitirá reequilibrar el árbol cuando la diferencia de altura entre los subárboles es menor a 1.\n
        Retorna el nuevo nodo raíz del árbol, representante a y.
        """

        # Se identifica inicialmente el flujo inicial del árbol
        y = x.derecha
        T2 = y.izquierda

        # Se ejecuta rotación de punteros
        y.izquierda = x
        x.derecha = T2

        # Se actualiza las alturas del nodo x y el nodo y
        x.altura = 1 + max(self.__obtener_altura(x.izquierda), self.__obtener_altura(x.derecha))
        y.altura = 1 + max(self.__obtener_altura(y.izquierda), self.__obtener_altura(y.derecha))

        # Retorna el nuevo nodo raíz
        return y

    def __rotacion_derecha(self, y: NodoAVL[T]) -> NodoAVL[T]:
        """
        Este método se activa cuando el árbol se cae de más hacia el brazo izquierdo.\n
        El parametro y representa a un nodo el cual posee el valor más alto de todo el árbol,
        pero si sus nodos hijos o subárboles son valores que parten de ahí totalmente de manera descendiente, 
        se aplica esta rotación.\n
        Esta rotación permitirá reequilibrar el árbol cuando la diferencia de altura entre los subárboles es mayor a 1.\n
        Retorna el nuevo nodo raíz del árbol, representante a x.
        """

        # Se identifica inicialmente el flujo inicial del árbol
        x = y.izquierda
        T2 = x.derecha

        # Se ejecuta rotación de punteros
        x.derecha = y
        y.izquierda = T2

        # Se actualiza las alturas del nodo x y el nodo y
        y.altura = 1 + max(self.__obtener_altura(y.izquierda), self.__obtener_altura(y.derecha))
        x.altura = 1 + max(self.__obtener_altura(x.izquierda), self.__obtener_altura(x.derecha))

        # Retorna el nuevo nodo raíz
        return x

    def __balancear(self, nodo: NodoAVL[T]) -> NodoAVL[T]:
        """
        Método que realiza el balanceo automático de un nodo en el árbol AVL.

        Este método es el núcleo del auto-balanceo del árbol. Se encarga de
        calcular las alturas, evaluar el factor de balanceo y aplicar las
        rotaciones necesarias ya sean simples o dobles para mantener el árbol optimizado.

        Flujo de ejecución paso a paso:
        -------------------------------
        1. VALIDACIÓN INICIAL: Si el nodo es nulo (subárbol vacío), se retorna tal cual.
        2. ACTUALIZACIÓN DE ALTURA: Se recalcula la altura del nodo actual basándose
        en la altura máxima de sus hijos (izquierdo y derecho) más 1.
        3. FACTOR DE BALANCEO: Se calcula la diferencia de altura (izq - der). El
        rango ideal para un AVL es [-1, 0, 1]. Cualquier otro valor necesitará de un balanceo.

        Los 4 Casos de Desbalanceo y sus soluciones para balancear:
        -------------------------------------------
        * CASO 1: Rotación Izquierda - Izquierda.\n
        Condición: balance > 1 (cargado de más en el brazo izquierdo) 
        y el hijo izquierdo tiene balance >= 0 (cargado igual en el brazo izquierdo del subárbol izquierdo).\n
        Solución: Se corrige con una sola rotación a la derecha.\n

        * CASO 2: Rotación Izquierda - Derecha.\n
        Condición: balance > 1 (cargado de más en el brazo izquierdo) 
        y el hijo izquierdo tiene balance < 0 (cargado en el brazo derecho del subárbol izquierdo).\n
        Solución: Requiere una doble rotación: 
        1. Una rotación a la izquierda en el subárbol izquierdo para transformar el problema en una 
        rotación izquierda - izquierda para el nodo actual.\n 
        2. Después, una rotación a la derecha en el nodo actual para finalizar el balanceo.\n

        * CASO 3: Rotación Derecha - Derecha.\n
        Condición: balance < -1 (cargado de más en el brazo derecho) 
        y el hijo derecho tiene balance <= 0 (cargado igualmente en el brazo derecho del subárbol derecho).\n
        Solución: Se corrige con una sola rotación a la izquierda.\n

        * CASO 4: Rotación Derecha - Izquierda.\n
        Condición: balance < -1 (cargado de más en el brazo derecho) 
        y el hijo derecho tiene balance > 0 (cargado en el brazo izquierdo del subárbol derecho).\n
        Solución: Requiere una doble rotación: 
        1. Una rotación a la derecha en el subárbol derecho para transformar el problema en una 
        rotación derecha - derecha para el nodo actual.\n 
        2. Después, una rotación a la izquierda en el nodo actual para resolver el balanceo.\n

        El método devolverá la nueva raíz del respectivo subárbol, donde pueden existir rotaciones o no.
        """

        if not nodo:
            return nodo

        # Se actualiza la altura del nodo actual
        nodo.altura = 1 + max(self.__obtener_altura(nodo.izquierda), self.__obtener_altura(nodo.derecha))

        # Se obtiene el factor de balanceo
        factor_balanceo = self.__obtener_factor_balanceo(nodo)

        # Se obtiene esos factores para los subarboles izquierdos y derechos respectivamente
        factor_balanceo_hijo_izquierdo = self.__obtener_factor_balanceo(nodo.izquierda)
        factor_balanceo_hijo_derecho = self.__obtener_factor_balanceo(nodo.derecha)

        # Rotación Izquierda - Izquierda (Desbalanceo Externo Izquierdo). Requiere solo una rotación.
        if factor_balanceo > 1 and factor_balanceo_hijo_izquierdo >= 0:
            return self.__rotacion_derecha(nodo)

        # Rotación Izquierda - Derecha (Desbalanceo Interno Izquierdo). Requiere doble rotación.
        if factor_balanceo > 1 and factor_balanceo_hijo_izquierdo < 0:
            nodo.izquierda = self.__rotacion_izquierda(nodo.izquierda)
            return self.__rotacion_derecha(nodo)

        # Rotación Derecha - Derecha (Desbalanceo Externo Derecho). Requiere solo una rotación.
        if factor_balanceo < -1 and factor_balanceo_hijo_derecho <= 0:
            return self.__rotacion_izquierda(nodo)

        # Rotación Derecha - Izquierdo (Desbalanceo Interno Derecho). Requiere doble rotación.
        if factor_balanceo < -1 and factor_balanceo_hijo_derecho > 0:
            nodo.derecha = self.__rotacion_derecha(nodo.derecha)
            return self.__rotacion_izquierda(nodo)

        # Retorna el nuevo nodo raíz
        return nodo

    def __obtener_altura(self, nodo: Optional[NodoAVL[T]]) -> int:
        """
        Método que verifica la propiedad de altura de un nodo existente en el árbol.\n 
        Un nodo vacío (cuando es None) no tiene altura, devuelve 0 en altura. 
        Si el nodo existe, simplemente devuelve el valor guardado en su atributo de altura. 
        """

        if not nodo:
            return 0
        return nodo.altura

    def __obtener_factor_balanceo(self, nodo: Optional[NodoAVL[T]]) -> int:
        """
        Método que retorna el resultado de la resta que define la salud del árbol AVL: Altura_Izquierda - Altura_Derecha.\n
        Si devuelve 0, el nodo está perfectamente equilibrado en ambos brazos.\n
        Si retorna 1, el brazo izquierdo es un nivel más alto que el derecho, lo cual sigue siendo válido.\n
        Si devuelve -1, el brazo derecho es un nivel más alto. También sigue siendo válido.\n
        Si retorna un número mayor a 1 o un número menor a -1, 
        el árbol está inclinado de más y se deberá balancear o rotar inmediatamente por su respectivo método de balanceo.
        """

        if not nodo:
            return 0
        return self.__obtener_altura(nodo.izquierda) - self.__obtener_altura(nodo.derecha)

    def __obtener_nodo_minimo(self, nodo: NodoAVL[T]) -> NodoAVL[T]:
        """
        Método que trata de encontrar el valor más pequeño de una rama y si se encuentra lo devuelve.\n
        Por su naturaleza, los valores menores siempre se ramifican al brazo izquierdo. 
        Se ejecuta un bucle while actual.izquierda, moviéndose hacia abajo y a la izquierda hasta que ya no haya más hijos. 
        El último nodo alcanzado es el mínimo absoluto.
        """
                
        actual = nodo
        while actual.izquierda:
            actual = actual.izquierda
        return actual

    def __in_orden_recursivo(self, nodo: Optional[NodoAVL[T]], lista: DoublyLinkedList[T]) -> None:
        """
        Este método recorre todo el árbol desde el subárbol izquierdo menor, entre medio procesa la raiz actual 
        y llega hasta el subárbol derecho mayor.\n

        Funciona por medio de dos rondas de recursión: 
        - La primera ronda se apilan las llamadas a los recorridos desde la raiz, 
          accediendo a los subárboles izquierdos respectivos hasta la hoja izquierda con el valor más pequeño.
          Cuando se desapilan estas invocaciones se sigue el recorrido In-Order desde el brazo izquierdo menor hasta la raiz.\n

        - Entre medio se añade la raíz.\n
          
        - La segunda ronda se apilan las llamadas a los recorridos desde la raiz,
          accediendo a los subárboles derechos respectivos hasta la hoja derecha con el valor más grande.
          Cuando se desapilan estas invocaciones se sigue el recorrido In-Order desde la raiz hasta el brazo derecho mayor.\n

        Cuando se terminen esas rondas, la colección respectiva tendra los elementos ordenados desde el menor hasta el mayor.
        """

        if nodo:
            self.__in_orden_recursivo(nodo.izquierda, lista)
            lista.insertar_al_final(nodo.dato)
            self.__in_orden_recursivo(nodo.derecha, lista)

    def __pre_orden_recursivo(self, nodo: Optional[NodoAVL[T]], lista: DoublyLinkedList[T]) -> None:
        """
        Este método recorre todo el árbol desde la raíz, accediendo primero a todo el brazo izquierdo, para posteriormente
        acceder a todo el brazo derecho.\n

        El primer elemento añadido es la raíz, los demás se agregaran en base a 2 rondas de recursión:
        - La primera ronda se apilan las llamadas a los recorridos desde la raiz, 
          accediendo a los subárboles izquierdos respectivos hasta la hoja izquierda con el valor más pequeño.
          Cuando se desapilan estas invocaciones se sigue el recorrido Pre-Order desde el raíz hasta el brazo izquierdo menor.

        - La segunda ronda se apilan las llamadas a los recorridos desde la raiz,
          accediendo a los subárboles derechos respectivos hasta la hoja derecha con el valor más grande.
          Cuando se desapilan estas invocaciones se sigue el recorrido Pre-Order 
          volviendo desde la raiz hasta el brazo derecho mayor.\n

        Cuando se terminen esas rondas, la colección respectiva tendrá la misma estructura actual del árbol en orden.
        """

        if nodo:
            lista.insertar_al_final(nodo.dato)
            self.__pre_orden_recursivo(nodo.izquierda, lista)
            self.__pre_orden_recursivo(nodo.derecha, lista)

    def __post_orden_recursivo(self, nodo: Optional[NodoAVL[T]], lista: DoublyLinkedList[T]) -> None:
        """
        Este método recorre todo el árbol desde el subárbol izquierdo menor, posteriormente al subárbol derecho menor 
        para finalmente acceder a la raíz.\n

        Funciona por medio de dos rondas de recursión: 
        - La primera ronda se apilan las llamadas a los recorridos desde la raiz, 
          accediendo a los subárboles izquierdos respectivos hasta la hoja izquierda con el valor más pequeño.
          Cuando se desapilan estas invocaciones se sigue el recorrido Post-Order desde el brazo izquierdo menor hasta la raíz.

        - La segunda ronda se apilan las llamadas a los recorridos desde la raiz,
          accediendo a los subárboles derechos respectivos hasta la hoja derecha con el valor más grande.
          Cuando se desapilan estas invocaciones se sigue el recorrido Post-Order desde el brazo derecho menor hasta la raíz.\n

        Cuando se terminen esas rondas, se agrega al final la raíz del árbol. Este recorrido es óptimo para cuando se desea
        borrar árboles.
        """

        if nodo:
            self.__post_orden_recursivo(nodo.izquierda, lista)
            self.__post_orden_recursivo(nodo.derecha, lista)
            lista.insertar_al_final(nodo.dato)
