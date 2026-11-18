
from Alerta import Alerta


class AlertaHumedad(Alerta):
    def __init__(self, humedad):
        self.__humedad = humedad

        mensaje = self.generar_mensaje()
        super().__init__(mensaje)

    def generar_mensaje(self):
        return "Humedad fuera del rango permitido."

    def consultar_humedad(self):
        return self.__humedad

    def mostrar_alerta(self):
        print("ALERTA DE HUMEDAD")
        print("Humedad registrada:", self.__humedad, "%")
        print(self.consultar_mensaje())
