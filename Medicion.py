
from datetime import datetime
from math import isfinite


class Medicion:
    def __init__(self, temperatura, humedad, fecha_hora=None):
        if not isfinite(temperatura) or temperatura < -50 or temperatura > 100:
            raise ValueError("Temperatura fuera de rango valido")

        if not isfinite(humedad) or humedad < 0 or humedad > 100:
            raise ValueError("La humedad debe estar entre 0 y 100")

        self.__temperatura = temperatura
        self.__humedad = humedad
        self.__fecha_hora = fecha_hora or datetime.now()

    def consultar_temperatura(self):
        return self.__temperatura

    def consultar_humedad(self):
        return self.__humedad

    def consultar_fecha_hora(self):
        return self.__fecha_hora

    def mostrar_medicion(self):
        print("Temperatura:", self.__temperatura, "°C")
        print("Humedad:", self.__humedad, "%")
        print("Fecha y hora:", self.__fecha_hora.strftime("%d/%m/%Y %H:%M:%S"))
