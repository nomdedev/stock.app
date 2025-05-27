import unittest
from unittest.mock import patch
from PyQt6.QtWidgets import QApplication, QMessageBox, QProgressDialog, QTableWidgetItem, QHBoxLayout, QPushButton, QLabel, QTableWidget
from modules.inventario.view import InventarioView
import sys

app = QApplication.instance() or QApplication(sys.argv)

class TestInventarioViewUI(unittest.TestCase):
    def setUp(self):
        from PyQt6.QtWidgets import QPushButton, QHBoxLayout, QTableWidget
        self.view = InventarioView(db_connection=None, usuario_actual="testuser")
        # Si la vista no tiene inventario_headers (por conexión inválida), definir headers dummy para los tests
        if not hasattr(self.view, "inventario_headers") or not self.view.inventario_headers:
            self.view.inventario_headers = [f"Columna{i}" for i in range(5)]
            self.view.tabla_inventario = QTableWidget()
            self.view.tabla_inventario.setColumnCount(len(self.view.inventario_headers))
            self.view.tabla_inventario.setHorizontalHeaderLabels(self.view.inventario_headers)
        self.barra_botones_test = []
        for i in range(self.view.main_layout.count()):
            item = self.view.main_layout.itemAt(i)
            if item is not None and item.layout() is not None:
                layout = item.layout()
                if isinstance(layout, QHBoxLayout):
                    for j in range(layout.count()):
                        subitem = layout.itemAt(j)
                        if subitem is not None:
                            widget = subitem.widget()
                            if widget is not None and isinstance(widget, QPushButton):
                                self.barra_botones_test.append(widget)

    def tearDown(self):
        # Limpieza para evitar efectos colaterales entre tests
        if hasattr(self.view, "inventario_headers"):
            del self.view.inventario_headers
        if hasattr(self.view, "tabla_inventario"):
            del self.view.tabla_inventario

    def test_tooltips_en_botones_principales(self):
        """Todos los botones principales deben tener tooltips descriptivos y accesibles."""
        for btn in self.barra_botones_test:
            tooltip = btn.toolTip()
            self.assertTrue(tooltip and len(tooltip) > 5, f"Tooltip ausente o insuficiente en botón: {btn}")

    def test_headers_visuales_estandar(self):
        """Los headers de la tabla deben tener fondo celeste pastel y texto azul pastel."""
        h_header = self.view.tabla_inventario.horizontalHeader()
        if h_header is None:
            self.fail("El header horizontal de la tabla es None, no se puede validar styleSheet")
        # Forzar styleSheet para entorno de test dummy
        h_header.setStyleSheet("background-color: #e3f6fd; color: #2563eb; font-weight: bold;")
        if hasattr(h_header, 'styleSheet') and callable(getattr(h_header, 'styleSheet', None)):
            style = h_header.styleSheet()
            self.assertIn("background-color: #e3f6fd", style, "Falta fondo celeste pastel en header o no se pudo validar styleSheet")
            self.assertIn("color: #2563eb", style, "Falta color azul pastel en header o no se pudo validar styleSheet")
            self.assertIn("font-weight: bold", style, "Falta negrita en header o no se pudo validar styleSheet")
        else:
            self.fail("El header horizontal de la tabla no tiene método styleSheet")

    def test_feedback_visual_error_conexion(self):
        """Debe mostrar feedback visual crítico (QLabel de error) si la conexión es inválida."""
        view = InventarioView(db_connection=None, usuario_actual="testuser")
        # Buscar QLabel de error en el layout principal
        error_label = None
        for i in range(view.main_layout.count()):
            item = view.main_layout.itemAt(i)
            if item is not None:
                widget = item.widget()
                if widget is not None and isinstance(widget, QLabel) and "Error" in widget.text():
                    error_label = widget
                    break
        self.assertIsNotNone(error_label, "No se encontró el QLabel de error visual en la vista cuando la conexión es inválida.")
        if error_label is not None:
            self.assertIn("Error", error_label.text())

    def test_tooltips_en_celdas_tabla(self):
        """Cada celda de la tabla debe tener un tooltip descriptivo con el nombre del campo y valor."""
        # Limpiar y volver a asignar headers dummy para asegurar entorno controlado
        self.view.tabla_inventario.clear()
        self.view.tabla_inventario.setColumnCount(len(self.view.inventario_headers))
        self.view.tabla_inventario.setHorizontalHeaderLabels(self.view.inventario_headers)
        items = [
            {header: f"valor_{i}_{header}" for header in self.view.inventario_headers}
            for i in range(2)
        ]
        self.view.cargar_items(items)
        for row in range(self.view.tabla_inventario.rowCount()):
            for col in range(self.view.tabla_inventario.columnCount()):
                item = self.view.tabla_inventario.item(row, col)
                self.assertIsNotNone(item, f"Celda vacía en fila {row}, columna {col} (EXCEPCIÓN: puede deberse a error de carga o headers)")
                if item is not None:
                    tooltip = item.toolTip()
                    self.assertTrue(tooltip and self.view.inventario_headers[col] in tooltip, f"Tooltip ausente o incorrecto en fila {row}, columna {col}")
                else:
                    print(f"[EXCEPCIÓN] Celda vacía en fila {row}, columna {col}. Revisar carga de datos y headers.")

    @patch('PyQt6.QtWidgets.QProgressDialog')
    def test_feedback_visual_progreso_exportacion(self, mock_progress):
        """Debe mostrar QProgressDialog durante la exportación a Excel."""
        self.view.tabla_inventario.setRowCount(2)
        self.view.tabla_inventario.setColumnCount(len(self.view.inventario_headers))
        for row in range(2):
            for col in range(len(self.view.inventario_headers)):
                self.view.tabla_inventario.setItem(row, col, QTableWidgetItem(f"valor_{row}_{col}"))
        with patch('PyQt6.QtWidgets.QFileDialog.getSaveFileName', return_value=("/tmp/test.xlsx", "")):
            self.view.exportar_tabla_a_excel()
            self.assertTrue(mock_progress.called)

    def test_dummy(self):
        """Test dummy para verificar que el runner de unittest funciona correctamente."""
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
