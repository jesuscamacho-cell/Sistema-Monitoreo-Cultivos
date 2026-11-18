"""Persistencia de cultivos, mediciones y rangos mediante openpyxl."""

from datetime import datetime
from pathlib import Path
import shutil

from openpyxl import Workbook, load_workbook


class BackendExcel:
    def __init__(self, ruta_archivo=None):
        self.ruta_archivo = Path(ruta_archivo or Path(__file__).parent / "datos_cultivos.xlsx")
        self._inicializar_archivo()

    def _inicializar_archivo(self):
        if self.ruta_archivo.exists():
            libro = load_workbook(self.ruta_archivo)
            try:
                if not {"Cultivos", "Mediciones", "Configuracion"}.issubset(libro.sheetnames):
                    raise ValueError("El Excel no contiene las hojas necesarias del proyecto.")
            finally:
                libro.close()
            return

        libro = Workbook()
        cultivos = libro.active
        cultivos.title = "Cultivos"
        cultivos.append(["id", "nombre", "tipo_planta", "ubicacion"])
        mediciones = libro.create_sheet("Mediciones")
        mediciones.append(["id", "id_cultivo", "temperatura", "humedad", "fecha_hora"])
        configuracion = libro.create_sheet("Configuracion")
        configuracion.append(["temperatura_min", "temperatura_max", "humedad_min", "humedad_max"])
        libro.save(self.ruta_archivo)
        libro.close()

    @staticmethod
    def _registros(hoja):
        filas = hoja.iter_rows(values_only=True)
        columnas = next(filas)
        return [dict(zip(columnas, fila)) for fila in filas if fila[0] is not None]

    @staticmethod
    def _fila_por_id(hoja, identificador):
        for numero in range(2, hoja.max_row + 1):
            if hoja.cell(numero, 1).value == identificador:
                return numero
        raise ValueError(f"No existe el registro con ID {identificador}.")

    @staticmethod
    def _siguiente_id(hoja):
        ids = [fila[0] for fila in hoja.iter_rows(min_row=2, values_only=True) if isinstance(fila[0], int)]
        return max(ids, default=0) + 1

    def listar_cultivos(self):
        libro = load_workbook(self.ruta_archivo, read_only=True, data_only=True)
        try:
            return self._registros(libro["Cultivos"])
        finally:
            libro.close()

    def agregar_cultivo(self, nombre, tipo_planta, ubicacion):
        if not all((nombre.strip(), tipo_planta.strip(), ubicacion.strip())):
            raise ValueError("Nombre, tipo y ubicacion son obligatorios.")
        libro = load_workbook(self.ruta_archivo)
        try:
            hoja = libro["Cultivos"]
            identificador = self._siguiente_id(hoja)
            hoja.append([identificador, nombre.strip(), tipo_planta.strip(), ubicacion.strip()])
            libro.save(self.ruta_archivo)
            return identificador
        finally:
            libro.close()

    def actualizar_cultivo(self, identificador, nombre, tipo_planta, ubicacion):
        if not all((nombre.strip(), tipo_planta.strip(), ubicacion.strip())):
            raise ValueError("Nombre, tipo y ubicacion son obligatorios.")
        libro = load_workbook(self.ruta_archivo)
        try:
            hoja = libro["Cultivos"]
            numero = self._fila_por_id(hoja, identificador)
            for columna, valor in enumerate((nombre.strip(), tipo_planta.strip(), ubicacion.strip()), 2):
                hoja.cell(numero, columna).value = valor
            libro.save(self.ruta_archivo)
        finally:
            libro.close()

    def eliminar_cultivo(self, identificador):
        libro = load_workbook(self.ruta_archivo)
        try:
            cultivos = libro["Cultivos"]
            fila = self._fila_por_id(cultivos, identificador)
            cultivos.delete_rows(fila)
            mediciones = libro["Mediciones"]
            eliminadas = 0
            for numero in range(mediciones.max_row, 1, -1):
                if mediciones.cell(numero, 2).value == identificador:
                    mediciones.delete_rows(numero)
                    eliminadas += 1
            libro.save(self.ruta_archivo)
            return eliminadas
        finally:
            libro.close()

    def listar_mediciones(self, id_cultivo=None):
        libro = load_workbook(self.ruta_archivo, read_only=True, data_only=True)
        try:
            registros = self._registros(libro["Mediciones"])
            if id_cultivo is not None:
                registros = [m for m in registros if m["id_cultivo"] == id_cultivo]
            return registros
        finally:
            libro.close()

    def agregar_medicion(self, id_cultivo, temperatura, humedad, fecha_hora=None):
        libro = load_workbook(self.ruta_archivo)
        try:
            self._fila_por_id(libro["Cultivos"], id_cultivo)
            hoja = libro["Mediciones"]
            identificador = self._siguiente_id(hoja)
            hoja.append([identificador, id_cultivo, temperatura, humedad, fecha_hora or datetime.now()])
            libro.save(self.ruta_archivo)
            return identificador
        finally:
            libro.close()

    def actualizar_medicion(self, identificador, temperatura, humedad):
        libro = load_workbook(self.ruta_archivo)
        try:
            hoja = libro["Mediciones"]
            numero = self._fila_por_id(hoja, identificador)
            hoja.cell(numero, 3).value = temperatura
            hoja.cell(numero, 4).value = humedad
            libro.save(self.ruta_archivo)
        finally:
            libro.close()

    def eliminar_medicion(self, identificador):
        libro = load_workbook(self.ruta_archivo)
        try:
            hoja = libro["Mediciones"]
            hoja.delete_rows(self._fila_por_id(hoja, identificador))
            libro.save(self.ruta_archivo)
        finally:
            libro.close()

    def leer_configuracion(self):
        libro = load_workbook(self.ruta_archivo, read_only=True, data_only=True)
        try:
            datos = self._registros(libro["Configuracion"])
            return datos[0] if datos else None
        finally:
            libro.close()

    def guardar_configuracion(self, temperatura_min, temperatura_max, humedad_min, humedad_max):
        libro = load_workbook(self.ruta_archivo)
        try:
            hoja = libro["Configuracion"]
            valores = [temperatura_min, temperatura_max, humedad_min, humedad_max]
            for columna, valor in enumerate(valores, 1):
                hoja.cell(2, columna).value = valor
            libro.save(self.ruta_archivo)
        finally:
            libro.close()

    def exportar_copia(self, destino):
        destino = Path(destino)
        if destino.resolve() == self.ruta_archivo.resolve():
            raise ValueError("La copia debe tener un nombre o ubicacion diferente.")
        shutil.copy2(self.ruta_archivo, destino)
