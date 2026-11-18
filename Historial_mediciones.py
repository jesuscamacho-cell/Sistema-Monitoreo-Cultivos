
class HistorialMediciones:
    def __init__(self):
        self.__mediciones = []

    def agregar_medicion(self, medicion):
        self.__mediciones.append(medicion)

    def consultar_historial(self):
        return self.__mediciones.copy()

    def mostrar_historial(self):
        if len(self.__mediciones) == 0:
            print("No hay mediciones registradas.")
        else:
            for numero, medicion in enumerate(self.__mediciones, start=1):
                print("\nMedicion numero:", numero)
                medicion.mostrar_medicion()

    def calcular_promedio_temperatura(self):
        if len(self.__mediciones) == 0:
            raise ValueError("No hay mediciones para calcular el promedio")

        total = 0

        for medicion in self.__mediciones:
            total += medicion.consultar_temperatura()

        return total / len(self.__mediciones)

    def calcular_promedio_humedad(self):
        if len(self.__mediciones) == 0:
            raise ValueError("No hay mediciones para calcular el promedio")

        total = 0

        for medicion in self.__mediciones:
            total += medicion.consultar_humedad()

        return total / len(self.__mediciones)
