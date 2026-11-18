from Cultivo import Cultivo
from Medicion import Medicion
from Configuracio_ambiental import ConfiguracionAmbiental
from sistema_monitoreo import SistemaMonitoreo


class InterfazConsola:
    def __init__(self):
        print("======================================")
        print("     SISTEMA DE MONITOREO PARA CULTIVOS    ")
        print("======================================")
        print("\nPrimero vamos a configurar los rangos ambientales.")

        temperatura_minima = self._leer_decimal("Temperatura minima permitida (°C): ")
        temperatura_maxima = self._leer_decimal("Temperatura maxima permitida (°C): ")
        humedad_minima = self._leer_decimal("Humedad minima permitida (%): ")
        humedad_maxima = self._leer_decimal("Humedad maxima permitida (%): ")

        self.__configuracion = ConfiguracionAmbiental(
            temperatura_minima,
            temperatura_maxima,
            humedad_minima,
            humedad_maxima
        )
        self.__sistema = SistemaMonitoreo(self.__configuracion)
        self.__siguiente_id = 1

    def iniciar(self):
        while True:
            print("\n========== MENU PRINCIPAL ==========")
            print("1. Registrar cultivo")
            print("2. Registrar medicion")
            print("3. Consultar cultivos")
            print("4. Ver historiales")
            print("5. Consultar alertas")
            print("6. Ver resumen")
            print("7. Salir")

            opcion = input("Seleccione una opcion: ").strip()

            if opcion == "1":
                self.registrar_cultivo()
            elif opcion == "2":
                self.registrar_medicion()
            elif opcion == "3":
                self.consultar_cultivos()
            elif opcion == "4":
                self.__sistema.mostrar_historiales()
            elif opcion == "5":
                self.__sistema.mostrar_alertas()
            elif opcion == "6":
                self.__sistema.mostrar_resumen()
            elif opcion == "7":
                print("\nGracias por utilizar el sistema, Vuelva pronto")
                break
            else:
                print("Opcion no valida. Intente nuevamente.")

    def registrar_cultivo(self):
        print("\n--- REGISTRO DE CULTIVO ---")
        nombre = input("Nombre del cultivo: ").strip()
        tipo_planta = input("Tipo de planta: ").strip()
        ubicacion = input("Ubicacion del cultivo: ").strip()

        if not nombre or not tipo_planta or not ubicacion:
            print("Error: todos los campos son obligatorios.")
            return

        cultivo = Cultivo(
            self.__siguiente_id,
            nombre,
            tipo_planta,
            ubicacion
        )
        self.__sistema.registrar_cultivo(cultivo)

        print("Cultivo registrado correctamente.")
        print("ID asignado:", self.__siguiente_id)
        self.__siguiente_id += 1

    def registrar_medicion(self):
        print("\n--- REGISTRO DE MEDICION ---")

        cultivos = self.__sistema.consultar_cultivos()
        if not cultivos:
            print("Todavia no hay cultivos registrados.")
            return

        self.consultar_cultivos()
        id_cultivo = self._leer_entero("Ingrese el ID del cultivo: ")

        try:
            temperatura = self._leer_decimal("Temperatura actual (°C): ")
            humedad = self._leer_decimal("Humedad actual (%): ")

            medicion = Medicion(temperatura, humedad)
            self.__sistema.registrar_medicion(id_cultivo, medicion)

            print("\nMedicion registrada correctamente.")
            print("--- RESULTADO DEL ANALISIS ---")
            print("Cultivo:", self.__sistema.buscar_cultivo(id_cultivo).consultar_nombre())
            print("Temperatura:", temperatura, "°C")
            print("Humedad:", humedad, "%")

            if self.__configuracion.validar_temperatura(temperatura):
                print("Temperatura: ADECUADA")
            elif temperatura < self.__configuracion.consultar_temperatura()[0]:
                print("Temperatura: BAJA")
            else:
                print("Temperatura: ALTA")

            if self.__configuracion.validar_humedad(humedad):
                print("Humedad: ADECUADA")
            elif humedad < self.__configuracion.consultar_humedad()[0]:
                print("Humedad: BAJA")
            else:
                print("Humedad: ALTA")

            print("\nRecomendacion: revise las variables que aparecen fuera del rango permitido.")
        except ValueError as error:
            print("No se pudo registrar la medicion:", error)

    def consultar_cultivos(self):
        print("\n--- CULTIVOS REGISTRADOS ---")
        cultivos = self.__sistema.consultar_cultivos()

        if not cultivos:
            print("No hay cultivos registrados.")
            return

        for cultivo in cultivos:
            cultivo.mostrar_informacion()
            print("-----------------------------")

    @staticmethod
    def _leer_decimal(mensaje):
        while True:
            try:
                return float(input(mensaje))
            except ValueError:
                print("Entrada no valida. Ingrese un numero.")

    @staticmethod
    def _leer_entero(mensaje):
        while True:
            try:
                return int(input(mensaje))
            except ValueError:
                print("Entrada no valida. Ingrese un numero entero.")
