"""Pruebas de la accion de refrescar sin abrir una ventana de Tkinter."""

import unittest
from unittest.mock import Mock, patch

from InterfazGrafica import InterfazGrafica


class PruebasRefrescoInterfaz(unittest.TestCase):
    def setUp(self):
        # No se necesita pantalla para verificar la accion del boton.
        self.interfaz = InterfazGrafica.__new__(InterfazGrafica)
        self.interfaz.actualizar_tablas = Mock()

    def test_refrescar_recarga_tablas(self):
        resultado = self.interfaz.refrescar_datos()
        self.interfaz.actualizar_tablas.assert_called_once_with()
        self.assertEqual(resultado, "break")

    def test_refrescar_informa_si_excel_no_se_puede_leer(self):
        self.interfaz.actualizar_tablas.side_effect = OSError("Excel no disponible")
        with patch("InterfazGrafica.messagebox.showerror") as aviso:
            resultado = self.interfaz.refrescar_datos()
        aviso.assert_called_once_with("Error al actualizar", "Excel no disponible")
        self.assertEqual(resultado, "break")


if __name__ == "__main__":
    unittest.main()
