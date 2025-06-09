import unittest
import os
from modules.contabilidad.model import ContabilidadModel  # Confirmar que la ruta es correcta

class MockDB:
    def ejecutar_query(self, query, params):
        # Simula una base de datos con un recibo existente
        if params[0] == 1:
            return [("2023-10-01", 101, 5000.0, "Pago de servicios", "Cliente XYZ", "firma_hash_123")]
        return []  # Simula que no se encuentra el recibo

class TestGenerarReciboPDF(unittest.TestCase):
    def setUp(self):
        self.db = MockDB()
        self.model = ContabilidadModel(self.db)

    def tearDown(self):
        if os.path.exists("recibo_1.pdf"):
            os.remove("recibo_1.pdf")

    def test_generar_recibo_existente(self):
        resultado = self.model.generar_recibo_pdf(1)
        self.assertEqual(resultado, "Recibo exportado como recibo_1.pdf.")
        self.assertTrue(os.path.exists("recibo_1.pdf"))

    def test_generar_recibo_inexistente(self):
        resultado = self.model.generar_recibo_pdf(999)
        self.assertEqual(resultado, "Recibo no encontrado.")

if __name__ == "__main__":
    unittest.main()
