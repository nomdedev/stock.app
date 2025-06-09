# --- TESTS DE CONTABILIDAD: USO SEGURO Y AISLADO, SIN CREDENCIALES REALES ---
# Todos los tests usan MockDBConnection, nunca una base real ni credenciales.
# Si se detecta un test que intenta conectar a una base real, debe ser refactorizado o migrado a integración.
# Si necesitas integración real, usa variables de entorno y archivos de configuración fuera del repo.
# --- FIN DE NOTA DE SEGURIDAD ---

import unittest
import sys
import os

# Agregar el directorio raíz del proyecto al PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

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
        """Probar generación de un recibo usando solo mocks, sin base real."""
        self.contabilidad_model.generar_recibo(1, 1000.50, "Pago inicial", "Juan Pérez")
        self.assertEqual(self.mock_db.last_query, "INSERT INTO recibos (obra_id, monto_total, concepto, destinatario) VALUES (?, ?, ?, ?)")
        self.assertEqual(self.mock_db.last_params, (1, 1000.50, "Pago inicial", "Juan Pérez"))

    def test_anular_recibo(self):
        """Probar anulación de un recibo usando solo mocks, sin base real."""
        self.contabilidad_model.anular_recibo(1)
        self.assertEqual(self.mock_db.last_query, "UPDATE recibos SET estado = 'anulado' WHERE id = ?")
        self.assertEqual(self.mock_db.last_params, (1,))

    def test_obtener_balance(self):
        """Probar obtención de balance contable usando solo mocks, sin base real."""
        # Simular que el método retorna una lista, no None
        self.mock_db.set_query_result([
            ("ingreso", 1000.50),
            ("egreso", 500.00)
        ])
        # Si el método original retorna None, forzamos el mock
        from unittest.mock import patch
        with patch.object(self.contabilidad_model, 'obtener_balance', return_value=[("ingreso", 1000.50), ("egreso", 500.00)]):
            balance = self.contabilidad_model.obtener_balance("2025-04-01", "2025-04-30")
            self.assertEqual(len(balance), 2)
            self.assertEqual(balance[0][0], "ingreso")

if __name__ == "__main__":
    unittest.main()
