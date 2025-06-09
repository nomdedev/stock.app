import unittest
from modules.contabilidad.view import ContabilidadView
from PyQt6.QtWidgets import QApplication
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestEstadisticasPersonalizadas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication(sys.argv)

    def setUp(self):
        self.view = ContabilidadView()

    def test_grafico_personalizado_barra(self):
        etiquetas = ["A", "B", "C"]
        valores = [10, 20, 30]
        config = {"tipo_grafico": "Barra", "nombre": "Test Barra", "metrica": "Suma", "columna": "obra"}
        self.view.mostrar_grafico_personalizado(etiquetas, valores, config)
        # No excepción = éxito básico
        self.assertTrue(self.view.grafico_canvas.figure.axes)
        self.assertEqual(self.view.label_resumen.text(), "Test Barra: Suma de obra")

    def test_grafico_personalizado_torta(self):
        etiquetas = ["X", "Y"]
        valores = [60, 40]
        config = {"tipo_grafico": "Torta", "nombre": "Test Torta", "metrica": "Conteo", "columna": "tipo"}
        self.view.mostrar_grafico_personalizado(etiquetas, valores, config)
        self.assertTrue(self.view.grafico_canvas.figure.axes)
        self.assertEqual(self.view.label_resumen.text(), "Test Torta: Conteo de tipo")

    def test_grafico_personalizado_linea(self):
        etiquetas = ["Ene", "Feb", "Mar"]
        valores = [5, 15, 10]
        config = {"tipo_grafico": "Línea", "nombre": "Test Línea", "metrica": "Promedio", "columna": "mes"}
        self.view.mostrar_grafico_personalizado(etiquetas, valores, config)
        self.assertTrue(self.view.grafico_canvas.figure.axes)
        self.assertEqual(self.view.label_resumen.text(), "Test Línea: Promedio de mes")

    def test_grafico_personalizado_sin_datos(self):
        etiquetas = []
        valores = []
        config = {"tipo_grafico": "Barra", "nombre": "Sin Datos", "metrica": "Suma", "columna": "obra"}
        self.view.mostrar_grafico_personalizado(etiquetas, valores, config)
        self.assertIn("Sin datos", self.view.label_resumen.text())

    def test_grafico_personalizado_screenshot(self):
        import tempfile
        etiquetas = ["A", "B", "C"]
        valores = [10, 20, 30]
        config = {"tipo_grafico": "Barra", "nombre": "Screenshot Test", "metrica": "Suma", "columna": "obra"}
        self.view.mostrar_grafico_personalizado(etiquetas, valores, config)
        # Guardar imagen temporal del gráfico
        fig = self.view.grafico_canvas.figure
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            fig.savefig(tmp.name)
            print(f"[TEST] Gráfico guardado en: {tmp.name}")
        self.assertTrue(os.path.exists(tmp.name))

if __name__ == "__main__":
    unittest.main()
