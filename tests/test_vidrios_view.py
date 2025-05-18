import unittest
from PyQt6.QtWidgets import QApplication, QTableWidgetItem
from modules.vidrios.view import VidriosView
import sys

app = QApplication.instance() or QApplication(sys.argv)

class TestVidriosView(unittest.TestCase):
    def setUp(self):
        self.view = VidriosView(usuario_actual="testuser")

    def test_layout_and_headers(self):
        # El layout principal debe existir y ser QVBoxLayout
        self.assertIsNotNone(self.view.layout())
        # La tabla debe tener headers correctos
        headers = [self.view.tabla_vidrios.horizontalHeaderItem(i).text() for i in range(self.view.tabla_vidrios.columnCount())]
        self.assertEqual(headers, self.view.vidrios_headers)

    def test_header_safe_methods(self):
        header = self.view.tabla_vidrios.horizontalHeader()
        # Todos los métodos de header deben ser seguros
        if header is not None:
            self.assertTrue(hasattr(header, 'setContextMenuPolicy'))
            self.assertTrue(hasattr(header, 'setSectionsMovable'))

    def test_qr_export_robust(self):
        # Caso 1: Sin selección (no debe lanzar excepción)
        try:
            self.view.mostrar_qr_item_seleccionado()
        except Exception as e:
            self.fail(f"Sin selección lanzó excepción: {e}")
        # Caso 2: Selección con item None
        self.view.tabla_vidrios.setRowCount(1)
        # No se setea item, debe ser robusto
        self.view.tabla_vidrios.selectRow(0)
        try:
            self.view.mostrar_qr_item_seleccionado()
        except Exception as e:
            self.fail(f"Selección con item None lanzó excepción: {e}")
        # Caso 3: Selección con item válido pero texto vacío
        self.view.tabla_vidrios.setItem(0, 0, QTableWidgetItem(""))
        self.view.tabla_vidrios.selectRow(0)
        try:
            self.view.mostrar_qr_item_seleccionado()
        except Exception as e:
            self.fail(f"Selección con texto vacío lanzó excepción: {e}")
        # Caso 4: Selección con item válido y texto válido
        self.view.tabla_vidrios.setItem(0, 0, QTableWidgetItem("VIDRIO-TEST"))
        self.view.tabla_vidrios.selectRow(0)
        try:
            self.view.mostrar_qr_item_seleccionado()
        except Exception as e:
            self.fail(f"Selección válida lanzó excepción: {e}")

if __name__ == "__main__":
    unittest.main()
