import unittest
from modules.contabilidad.model import ContabilidadModel

class MockDBConnection:
    def __init__(self):
        self.last_query = None
        self.last_params = None
        self.query_result = []

    def execute(self, query, params=None):
        self.last_query = query
        self.last_params = params

    def fetchall(self):
        return self.query_result

    def set_query_result(self, result):
        self.query_result = result

    def ejecutar_query(self, query, params=None):
        self.execute(query, params)

class TestContabilidadModel(unittest.TestCase):

    def setUp(self):
        # Simulación de conexión a base de datos
        self.mock_db = MockDBConnection()
        self.contabilidad_model = ContabilidadModel(self.mock_db)

    def test_generar_recibo(self):
        # Probar generación de un recibo
        self.contabilidad_model.generar_recibo(1, 1000.50, "Pago inicial", "Juan Pérez")
        self.assertEqual(self.mock_db.last_query, "INSERT INTO recibos (obra_id, monto_total, concepto, destinatario) VALUES (?, ?, ?, ?)")
        self.assertEqual(self.mock_db.last_params, (1, 1000.50, "Pago inicial", "Juan Pérez"))

    def test_anular_recibo(self):
        # Probar anulación de un recibo
        self.contabilidad_model.anular_recibo(1)
        self.assertEqual(self.mock_db.last_query, "UPDATE recibos SET estado = 'anulado' WHERE id = ?")
        self.assertEqual(self.mock_db.last_params, (1,))

    def test_obtener_balance(self):
        # Probar obtención de balance contable
        self.mock_db.set_query_result([
            ("ingreso", 1000.50),
            ("egreso", 500.00)
        ])
        balance = self.contabilidad_model.obtener_balance("2025-04-01", "2025-04-30")
        self.assertEqual(len(balance), 2)
        self.assertEqual(balance[0][0], "ingreso")

if __name__ == "__main__":
    unittest.main()
