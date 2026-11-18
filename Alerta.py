
class Alerta:
    def __init__(self, mensaje):
        self.__mensaje = mensaje

    def consultar_mensaje(self):
        return self.__mensaje

    def mostrar_alerta(self):
        print("ALERTA:", self.__mensaje)

    def generar_mensaje(self):
        return self.__mensaje
