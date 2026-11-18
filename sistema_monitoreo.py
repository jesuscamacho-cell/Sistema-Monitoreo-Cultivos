

from alerta_temperatura import AlertaTemperatura
from alerta_humedad import AlertaHumedad


class SistemaMonitoreo:
    def __init__(self, configuracion):
        self.__cultivos = []
        self.__configuracion = configuracion

    def registrar_cultivo(self, cultivo):
        self.__cultivos.append(cultivo)

    def consultar_cultivos(self):
        return self.__cultivos.copy()

    def buscar_cultivo(self, id_cultivo):
        for cultivo in self.__cultivos:
            if cultivo.consultar_id() == id_cultivo:
                return cultivo

        raise ValueError("No se encontro el cultivo")

    def registrar_medicion(self, id_cultivo, medicion):
        cultivo = self.buscar_cultivo(id_cultivo)

        cultivo.registrar_medicion(medicion)
        self.analizar_condiciones(cultivo, medicion)

    def analizar_condiciones(self, cultivo, medicion):
        if self.__configuracion is None:
            return
        temperatura = medicion.consultar_temperatura()
        humedad = medicion.consultar_humedad()

        if not self.__configuracion.validar_temperatura(temperatura):
            alerta = AlertaTemperatura(temperatura)
            cultivo.agregar_alerta(alerta)

        if not self.__configuracion.validar_humedad(humedad):
            alerta = AlertaHumedad(humedad)
            cultivo.agregar_alerta(alerta)

    def evaluar_medicion(self, medicion):
        if self.__configuracion is None:
            raise ValueError("Primero configure los rangos ambientales.")

        temperatura = medicion.consultar_temperatura()
        humedad = medicion.consultar_humedad()
        temp_min, temp_max = self.__configuracion.consultar_temperatura()
        hum_min, hum_max = self.__configuracion.consultar_humedad()

        def estado(valor, minimo, maximo):
            if valor < minimo:
                return "BAJA"
            if valor > maximo:
                return "ALTA"
            return "ADECUADA"

        return {
            "temperatura": estado(temperatura, temp_min, temp_max),
            "humedad": estado(humedad, hum_min, hum_max),
        }

    def mostrar_historiales(self):
        for cultivo in self.__cultivos:
            cultivo.mostrar_historial()

    def mostrar_alertas(self):
        for cultivo in self.__cultivos:
            cultivo.mostrar_alertas()

    def mostrar_resumen(self):
        print("\n--- RESUMEN DEL SISTEMA ---")
        print("Cantidad de cultivos:", len(self.__cultivos))

        total_mediciones = 0
        total_alertas = 0

        for cultivo in self.__cultivos:
            total_mediciones += len(cultivo.consultar_historial())
            total_alertas += len(cultivo.consultar_alertas())

        print("Cantidad de mediciones:", total_mediciones)
        print("Cantidad de alertas:", total_alertas)
