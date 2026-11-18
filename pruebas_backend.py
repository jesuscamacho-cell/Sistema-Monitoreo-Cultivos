"""Pruebas de persistencia sin modificar el Excel del usuario."""

import tempfile
from pathlib import Path
import unittest

from BackendExcel import BackendExcel
from Configuracio_ambiental import ConfiguracionAmbiental
from Cultivo import Cultivo
from Medicion import Medicion
from sistema_monitoreo import SistemaMonitoreo


class PruebasBackendExcel(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.archivo = Path(self.temporal.name) / "pruebas.xlsx"
        self.backend = BackendExcel(self.archivo)

    def tearDown(self):
        self.temporal.cleanup()

    def test_registro_y_permanencia(self):
        self.assertEqual(self.backend.listar_cultivos(), [])
        self.assertIsNone(self.backend.leer_configuracion())
        self.backend.guardar_configuracion(18, 28, 50, 80)
        identificador = self.backend.agregar_cultivo("Tomate", "Hortaliza", "Huerta")
        medicion_id = self.backend.agregar_medicion(identificador, 32, 35)

        segunda_sesion = BackendExcel(self.archivo)
        self.assertEqual(segunda_sesion.leer_configuracion()["temperatura_min"], 18)
        self.assertEqual(segunda_sesion.listar_cultivos()[0]["nombre"], "Tomate")
        self.assertEqual(segunda_sesion.listar_mediciones()[0]["id"], medicion_id)

    def test_editar_y_eliminar_en_cascada(self):
        identificador = self.backend.agregar_cultivo("Lechuga", "Hortaliza", "Patio")
        medicion_id = self.backend.agregar_medicion(identificador, 22, 60)
        self.backend.actualizar_cultivo(identificador, "Lechuga verde", "Hortaliza", "Jardin")
        self.backend.actualizar_medicion(medicion_id, 23, 65)
        self.assertEqual(self.backend.listar_cultivos()[0]["ubicacion"], "Jardin")
        self.assertEqual(self.backend.listar_mediciones()[0]["humedad"], 65)
        self.assertEqual(self.backend.eliminar_cultivo(identificador), 1)
        self.assertEqual(self.backend.listar_cultivos(), [])
        self.assertEqual(self.backend.listar_mediciones(), [])

    def test_validaciones_y_alertas(self):
        with self.assertRaises(ValueError):
            ConfiguracionAmbiental(30, 20, 50, 80)
        with self.assertRaises(ValueError):
            Medicion(float("nan"), 40)
        self.backend.agregar_cultivo("Fresa", "Frutal", "Huerta")
        with self.assertRaises(ValueError):
            self.backend.agregar_medicion(100, 22, 60)
        sistema = SistemaMonitoreo(ConfiguracionAmbiental(18, 28, 50, 80))
        cultivo = Cultivo(1, "Tomate", "Hortaliza", "Patio")
        sistema.registrar_cultivo(cultivo)
        medicion = Medicion(32, 35)
        sistema.registrar_medicion(1, medicion)
        self.assertEqual(len(cultivo.consultar_alertas()), 2)
        self.assertEqual(sistema.evaluar_medicion(medicion)["temperatura"], "ALTA")
        self.assertEqual(sistema.evaluar_medicion(medicion)["humedad"], "BAJA")


if __name__ == "__main__":
    unittest.main()
