"""
tarea_1.py
------------
"""
__author__ = 'Lenika Elizabeth Montoya Valencia'

import entornos_o
from random import choice,random
from copy import deepcopy

class NueveCuartos():
    """
    Clase del entorno 9 cuartos en  una matriz 3x3, donde hay tres niveles y tres cuartos
    en cada nivel. La aspiradora puede moverse entre los cuartos y limpiar el cuarto actual.
    El estado del robot se representa como ([(x,y) del robot],[limpio,sucio])

    Las acciones legales son "ir_Derecha", "ir_Izquierda", "subir", "bajar", "limpiar" y "nada".
    No todas las acciones son posibles en todos los estados.
    La percepcion es una tupla que contiene la ubicacion de la aspiradora y el estado del cuarto actual(robot,estado_habitacion).
    """

    def __init__(self, estado_inicial=[(0, 0), [["sucio" for _ in range(3)] for _ in range(3)]]):
        self.x = estado_inicial
        self.costo = 0


    def percepcion(self):
        ubicacion_robot = self.x[0]
        return ubicacion_robot, self.x[1][ubicacion_robot[0]][ubicacion_robot[1]]

    def accion_legal(self, accion):
        piso, cuarto =  self.x[0]
        if accion == 'ir_Derecha':
            return cuarto < 2
        if accion == 'ir_Izquierda':
            return cuarto > 0
        if accion == 'subir':
            return piso < 2 and cuarto == 2
        if accion == 'bajar':
            return piso > 0 and cuarto == 0
        return accion in ["limpiar", "nada"]

    def transicion(self, accion):
        if not self.accion_legal(accion):
            accion = "nada"

        robot, cuartos = self.x[0], self.x[1]
        cuartos = deepcopy(cuartos) 
        if accion == "nada" and "sucio" in [room for floor in cuartos for room in floor]:
            self.costo += 1
        elif accion == "limpiar":
            self.costo += 1
            cuartos[robot[0]][robot[1]] = "limpio"
        elif accion == "ir_Derecha":
            self.costo += 2
            robot = (robot[0], robot[1] + 1)
        elif accion == "ir_Izquierda":
            self.costo += 2
            robot = (robot[0], robot[1] - 1)
        elif accion == "bajar":
            self.costo += 3
            robot = (robot[0] - 1, robot[1])
        elif accion == "subir":
            self.costo += 3
            robot = (robot[0] + 1, robot[1])

        self.x = (robot, cuartos)

class AgenteAleatorioNueveCuartos(entornos_o.Agente):
    """
    Un agente que escoge una acción aleatoria de las acciones legales.
    """
    def __init__(self, acciones):
        self.acciones = acciones

    def programa(self, _):
        return choice(self.acciones)

class AgenteReactivoNueveCuartos(entornos_o.Agente):
    """
    Un agente reactivo basado en modelo para la Matriz de Habitaciones.
    """
    def __init__(self):
        """
        Inicializa el modelo suponiendo que todo está sucio(peor de los casos)
        """
        self.modelo = [(0, 0), [["sucio" for _ in range(3)] for _ in range(3)]]
   
    def comportamiento(self, percepcion):
        robot, estado_habitacion = percepcion

        # Actualizar el modelo
        self.modelo[0] = robot
        self.modelo[1][robot[0]][robot[1]] = estado_habitacion

        habitaciones = self.modelo[1]

        if estado_habitacion == "sucio":
            return "limpiar"

        for piso in range(3):
            for cuarto in range(3):
                if habitaciones[piso][cuarto] == "sucio":
                    if robot[0] < piso and robot[1] == 2:
                        return "subir"
                    elif robot[0] > piso and robot[1] == 0:
                        return "bajar"

                    if robot[0] == piso:
                        if robot[1] < cuarto:
                            return "ir_Derecha"
                        elif robot[1] > cuarto:
                            return "ir_Izquierda"

                    if robot[0] < piso and robot[1] != 2:
                        return "ir_Derecha"
                    elif robot[0] > piso and robot[1] != 0:
                        return "ir_Izquierda"
        return "nada"

class NueveCuartosCiego(NueveCuartos):
    """
    Solo permite percepciones de la posición del robot.
    No de si el cuarto se encuentra limpio o sucio.
    """
    def percepcion(self):
        return self.x[0]

class AgenteReactivoCiega(AgenteReactivoNueveCuartos):
    """
    Agente reactivo Ciego basado en modelo Nueve Cuartos Ciego
    """
    def comportamiento(self, percepcion):
        ubicacion = percepcion

        self.modelo[0] = ubicacion

        habitaciones = self.modelo[1]

        if habitaciones[ubicacion[0]][ubicacion[1]] == "sucio":
            habitaciones[ubicacion[0]][ubicacion[1]] = "limpio"
            return "limpiar"

        for fila in range(3):
            for columna in range(3):
                if habitaciones[fila][columna] == "sucio":
                    if ubicacion[0] < fila and ubicacion[1] == 2:
                        return "subir"
                    elif ubicacion[0] > fila and ubicacion[1] == 0:
                        return "bajar"

                    if ubicacion[0] == fila:
                        if ubicacion[1] < columna:
                            return "ir_Derecha"
                        elif ubicacion[1] > columna:
                            return "ir_Izquierda"

                    if ubicacion[0] < fila and ubicacion[1] != 2:
                        return "ir_Derecha"
                    elif ubicacion[0] > fila and ubicacion[1] != 0:
                        return "ir_Izquierda"

        return "esperar"
    
class NueveCuartosEstocastica(NueveCuartos):
    """
    Variante estocástica de Nueve Cuartos:
        - 80% probabilidad de éxito en limpiar/moverse
        - 10% de fallar haciendo nada
        - 10% de ejecutar un movimiento aleatorio
    """
    def transicion(self, accion):
        if not self.accion_legal(accion):
            accion = "esperar"

        ubicacion, habitaciones = self.x[0], deepcopy(self.x[1])
        aleatorio = random()

        if accion == "limpiar":
            self.costo += 1
            habitaciones[ubicacion[0]][ubicacion[1]] = "limpio" if aleatorio < 0.8 else "sucio"

        elif accion in ["ir_Derecha", "ir_Izquierda", "subir", "bajar"]:
            if aleatorio < 0.8:
                ubicacion = self._mover(ubicacion, accion)
            elif aleatorio < 0.9:
                pass  
            else:
                accion_aleatoria = choice([a for a in ["ir_Izquierda", "ir_Derecha", "subir", "bajar"] if self.accion_legal(a)])
                ubicacion = self._mover(ubicacion, accion_aleatoria)
            self.costo += 2 if accion in ["ir_Izquierda", "ir_Derecha"] else 3

        elif accion == "nadar":
            self.costo += 1 if "sucio" in [hab for piso in habitaciones for hab in piso] else 0

        self.x = (ubicacion, habitaciones)

    def _mover(self, ubicacion, accion):
        if accion == "ir_Derecha":
            return (ubicacion[0], ubicacion[1] + 1)
        elif accion == "ir_Izquierda":
            return (ubicacion[0], ubicacion[1] - 1)
        elif accion == "subir":
            return (ubicacion[0] + 1, ubicacion[1])
        elif accion == "bajar":
            return (ubicacion[0] - 1, ubicacion[1])
        return ubicacion
    
def test():
    """
    Prueba de entornos y agentes, midiendo desempeño
    """

    x0 = [(0, 0), [["sucio" for _ in range(3)] for _ in range(3)]]
    acciones = ["ir_Derecha", "ir_Izquierda", "subir", "bajar", "limpiar", "esperar"]

    pruebas = [
        ("Aleatorio Normal", NueveCuartos(x0), AgenteAleatorioNueveCuartos(acciones)),
        ("Reactivo Normal", NueveCuartos(x0), AgenteReactivoNueveCuartos()),
        ("Aleatorio Ciego", NueveCuartosCiego(x0), AgenteAleatorioNueveCuartos(acciones)),
        ("Reactivo Ciego", NueveCuartosCiego(x0), AgenteReactivoCiega()),
        ("Aleatorio Estocástico", NueveCuartosEstocastica(x0), AgenteAleatorioNueveCuartos(acciones)),
        ("Reactivo Estocástico", NueveCuartosEstocastica(x0), AgenteReactivoNueveCuartos()),
    ]

    resultados = []

    for nombre, entorno, agente in pruebas:
        entornos_o.simulador(entorno, agente, 200)

        resultados.append((nombre, entorno.costo))

    print("\nResumen de Resultados:")
    print("-" * 30)
    for nombre, costo in resultados:
        print(f"Agente: {nombre:25s} | Costo total: {costo}")

if __name__ == "__main__":
    test()
