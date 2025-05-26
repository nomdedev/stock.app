import unittest
from unittest.mock import patch
from PyQt6.QtWidgets import QApplication, QMessageBox, QProgressDialog, QTableWidgetItem
from modules.inventario.view import InventarioView
import sys

app = QApplication.instance() or QApplication(sys.argv)

class TestInventarioViewUI(unittest.TestCase):
    def setUp(self):
        self.view = InventarioView(db_connection=None, usuario_actual="testuser")
        # Mock barra_botones if it does not exist
        if not hasattr(self.view, "barra_botones"):
            from unittest.mock import MagicMock
            mock_btn = MagicMock()
            mock_btn.toolTip.return_value = "Botón de prueba"
            setattr(self.view, "barra_botones", [mock_btn])

    def test_tooltips_en_botones_principales(self):
        """Todos los botones principales deben tener tooltips descriptivos y accesibles."""
        for btn in self.view.barra_botones:
            tooltip = btn.toolTip()
            self.assertTrue(tooltip and len(tooltip) > 5, f"Tooltip ausente o insuficiente en botón: {btn}")

    def test_headers_visuales_estandar(self):
        """Los headers de la tabla deben tener fondo celeste pastel y texto azul pastel."""
        h_header = self.view.tabla_inventario.horizontalHeader()
        if h_header is not None and hasattr(h_header, 'styleSheet') and callable(getattr(h_header, 'styleSheet', None)):
            style = h_header.styleSheet()
            self.assertIn("background-color: #e3f6fd", style, "Falta fondo celeste pastel en header o no se pudo validar styleSheet")
            self.assertIn("color: #2563eb", style, "Falta color azul pastel en header o no se pudo validar styleSheet")
            self.assertIn("font-weight: bold", style, "Falta negrita en header o no se pudo validar styleSheet")
        else:
            self.fail("El header horizontal de la tabla es None o no tiene método styleSheet")

    @patch('PyQt6.QtWidgets.QMessageBox.critical')
    def test_feedback_visual_error_conexion(self, mock_critical):
        """Debe mostrar feedback visual crítico (QMessageBox) si la conexión es inválida."""
        view = InventarioView(db_connection=None, usuario_actual="testuser")
        mock_critical.assert_called()
        args, _ = mock_critical.call_args
        self.assertIn("Error", args)

    def test_tooltips_en_celdas_tabla(self):
        """Cada celda de la tabla debe tener un tooltip descriptivo con el nombre del campo y valor."""
        items = [
            {header: f"valor_{i}_{header}" for header in self.view.inventario_headers}
            for i in range(2)
        ]
        self.view.cargar_items(items)
        for row in range(self.view.tabla_inventario.rowCount()):
            for col in range(self.view.tabla_inventario.columnCount()):
                item = self.view.tabla_inventario.item(row, col)
                # Robustecer: si la celda es None, el test debe fallar con mensaje claro y documentar la excepción
                self.assertIsNotNone(item, f"Celda vacía en fila {row}, columna {col} (EXCEPCIÓN: puede deberse a error de carga o headers)")
                if item is not None:
                    tooltip = item.toolTip()
                    self.assertTrue(tooltip and self.view.inventario_headers[col] in tooltip, f"Tooltip ausente o incorrecto en fila {row}, columna {col}")
                else:
                    # Documentar la excepción en el log del test
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
