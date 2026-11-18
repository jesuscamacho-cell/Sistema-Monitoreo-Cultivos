
class ConfiguracionAmbiental:
    def __init__(self, temperatura_minima, temperatura_maxima,
                 humedad_minima, humedad_maxima):

        if not -50 <= temperatura_minima <= temperatura_maxima <= 100:
            raise ValueError("Los limites de temperatura deben estar entre -50 y 100 °C y en orden.")
        if not 0 <= humedad_minima <= humedad_maxima <= 100:
            raise ValueError("Los limites de humedad deben estar entre 0 y 100 % y en orden.")

        self.__temperatura_minima = temperatura_minima
        self.__temperatura_maxima = temperatura_maxima
        self.__humedad_minima = humedad_minima
        self.__humedad_maxima = humedad_maxima

    def consultar_temperatura(self):
        return self.__temperatura_minima, self.__temperatura_maxima

    def consultar_humedad(self):
        return self.__humedad_minima, self.__humedad_maxima

    def validar_temperatura(self, temperatura):
        return self.__temperatura_minima <= temperatura <= self.__temperatura_maxima

    def validar_humedad(self, humedad):
        return self.__humedad_minima <= humedad <= self.__humedad_maxima

    def cambiar_temperatura(self, minima, maxima):
        if minima > maxima:
            raise ValueError("La temperatura minima no puede superar la maxima")

        self.__temperatura_minima = minima
        self.__temperatura_maxima = maxima

    def cambiar_humedad(self, minima, maxima):
        if minima < 0 or maxima > 100 or minima > maxima:
            raise ValueError("Rango de humedad no valido")

        self.__humedad_minima = minima
        self.__humedad_maxima = maxima
