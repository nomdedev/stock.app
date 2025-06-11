import unittest
import pandas as pd
import pytest

qt = pytest.importorskip("PyQt6")
try:
    from PyQt6.QtWidgets import QApplication
except Exception as exc:  # pragma: no cover - skip if Qt libs missing
    pytest.skip(f"PyQt6 unusable: {exc}", allow_module_level=True)
from modules.configuracion.view import ConfiguracionView

class TestConfiguracionViewFeedback(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if QApplication is None:
            pytest.skip("PyQt6 not available")
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.view = ConfiguracionView()

    def test_mostrar_mensaje_sets_text_and_description(self):
        self.view.mostrar_mensaje('ok', tipo='exito')
        self.assertIn('ok', self.view.mensaje_label.text())
        self.assertIn('exito', self.view.mensaje_label.accessibleDescription())

    def test_mostrar_preview_handles_empty(self):
        df = pd.DataFrame()
        self.view.mostrar_preview(df)
        self.assertEqual(self.view.preview_table.rowCount(), 0)
        self.assertIn('vacío', self.view.mensaje_label.text().lower())

    def test_mostrar_preview_populates_table(self):
        df = pd.DataFrame({'a':[1,2], 'b':[3,4]})
        self.view.mostrar_preview(df)
        self.assertEqual(self.view.preview_table.rowCount(), 2)
        self.assertTrue(self.view.boton_importar_csv.isEnabled())
