
from Historial_mediciones import HistorialMediciones


class Cultivo:
    def __init__(self, id_cultivo, nombre, tipo_planta, ubicacion):
        self.__id_cultivo = id_cultivo
        self.__nombre = nombre
        self.__tipo_planta = tipo_planta
        self.__ubicacion = ubicacion

        # Cada cultivo tiene su propio historial y sus alertas
        self.__historial = HistorialMediciones()
        self.__alertas = []

    def mostrar_informacion(self):
        print("ID:", self.__id_cultivo)
        print("Nombre:", self.__nombre)
        print("Tipo de planta:", self.__tipo_planta)
        print("Ubicacion:", self.__ubicacion)

    def consultar_nombre(self):
        return self.__nombre

    def consultar_ubicacion(self):
        return self.__ubicacion

    def cambiar_ubicacion(self, nueva_ubicacion):
        if nueva_ubicacion.strip() == "":
            raise ValueError("La ubicacion no puede estar vacia")
        self.__ubicacion = nueva_ubicacion

    def registrar_medicion(self, medicion):
        self.__historial.agregar_medicion(medicion)

    def consultar_historial(self):
        return self.__historial.consultar_historial()

    def agregar_alerta(self, alerta):
        self.__alertas.append(alerta)

    def consultar_alertas(self):
        return self.__alertas.copy()

    def mostrar_historial(self):
        print("\nHistorial del cultivo:", self.__nombre)
        self.__historial.mostrar_historial()

    def mostrar_alertas(self):
        print("\nAlertas del cultivo:", self.__nombre)

        if len(self.__alertas) == 0:
            print("No hay alertas registradas.")
        else:
            for alerta in self.__alertas:
                alerta.mostrar_alerta()
                print()

    def consultar_id(self):
        return self.__id_cultivo
