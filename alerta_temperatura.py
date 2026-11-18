
from Alerta import Alerta


class AlertaTemperatura(Alerta):
    def __init__(self, temperatura):
        self.__temperatura = temperatura

        mensaje = self.generar_mensaje()
        super().__init__(mensaje)

    def generar_mensaje(self):
        return "Temperatura fuera del rango permitido."

    def consultar_temperatura(self):
        return self.__temperatura

    def mostrar_alerta(self):
        print("ALERTA DE TEMPERATURA")
        print("Temperatura registrada:", self.__temperatura, "°C")
        print(self.consultar_mensaje())
