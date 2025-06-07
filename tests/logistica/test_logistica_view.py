import unittest
from unittest.mock import MagicMock, patch
from PyQt6.QtWidgets import QApplication
import sys

# Importar la vista a testear
from modules.logistica.view import LogisticaView

app = QApplication.instance() or QApplication(sys.argv)

class DummyController:
    def __init__(self):
        self.edit_called = False
        self.delete_called = False
        self.last_args = None
        self.raise_on_edit = False
        self.raise_on_delete = False
    def editar_envio(self, datos):
        self.edit_called = True
        self.last_args = datos
        if self.raise_on_edit:
            raise Exception("Error de edición")
    def eliminar_envio(self, id_envio):
        self.delete_called = True
        self.last_args = id_envio
        if self.raise_on_delete:
            raise Exception("Error de eliminación")

class DummyTable:
    def __init__(self, data):
        self._data = data
    def columnCount(self):
        return len(self._data[0])
    def rowCount(self):
        return len(self._data)
    def item(self, row, col):
        class Item:
            def __init__(self, text):
                self._text = text
            def text(self):
                return self._text
        return Item(self._data[row][col])
    def setCellWidget(self, fila, col, widget):
        pass
    def setColumnCount(self, n):
        pass
    def setHorizontalHeaderItem(self, col, item):
        pass

class LogisticaViewTestCase(unittest.TestCase):
    def setUp(self):
        self.view = LogisticaView()
        self.controller = DummyController()
        self.view.controller = self.controller
        # Simular tabla con datos
        self.view.tabla_envios = DummyTable([
            ["1", "Obra X", "Material Y", "10", "Pendiente", "Juan", "Camioneta"],
            ["2", "Obra Z", "Material W", "5", "Entregado", "Ana", "Furgón"]
        ])
        self.view._get_header_text = lambda i: ["ID", "Obra", "Material", "Cantidad", "Estado", "Quién lo llevó", "Vehículo"][i]
        self.view._get_item_text = lambda row, col: self.view.tabla_envios._data[row][col]
        self.view.mostrar_feedback = MagicMock()
        self.view.refrescar_tabla_envios = MagicMock()

    @patch("modules.logistica.view.QDialog.exec", return_value=1)
    def test_editar_envio_exito(self, mock_exec):
        # Simula edición exitosa
        self.controller.raise_on_edit = False
        self.view.abrir_formulario_editar_envio(0)
        self.assertTrue(self.view.mostrar_feedback.called)
        self.assertTrue(self.view.refrescar_tabla_envios.called)

    @patch("modules.logistica.view.QDialog.exec", return_value=1)
    def test_editar_envio_error(self, mock_exec):
        # Simula error en edición
        self.controller.raise_on_edit = True
        self.view.abrir_formulario_editar_envio(0)
        self.assertTrue(self.view.mostrar_feedback.called)
        self.assertFalse(self.view.refrescar_tabla_envios.called)

    @patch("modules.logistica.view.QMessageBox.question", return_value=16384)  # Yes
    def test_eliminar_envio_exito(self, mock_question):
        self.controller.raise_on_delete = False
        self.view.eliminar_envio(0)
        self.assertTrue(self.view.mostrar_feedback.called)
        self.assertTrue(self.view.refrescar_tabla_envios.called)

    @patch("modules.logistica.view.QMessageBox.question", return_value=16384)  # Yes
    def test_eliminar_envio_error(self, mock_question):
        self.controller.raise_on_delete = True
        self.view.eliminar_envio(0)
        self.assertTrue(self.view.mostrar_feedback.called)
        self.assertFalse(self.view.refrescar_tabla_envios.called)

    @patch("modules.logistica.view.QMessageBox.question", return_value=65536)  # No
    def test_eliminar_envio_cancelado(self, mock_question):
        self.view.eliminar_envio(0)
        self.assertTrue(self.view.mostrar_feedback.called)
        self.assertFalse(self.view.refrescar_tabla_envios.called)

if __name__ == "__main__":
    unittest.main()
