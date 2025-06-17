import unittest
import sys
import os

# Agregar el directorio raíz del proyecto al PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.obras.produccion.model import ProduccionModel  # Importar desde el módulo correcto

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
        self.last_query = query
        self.last_params = params
        if "SELECT * FROM auditorias_sistema" in query:
            return [("2025-04-14 10:00:00", 1, "logistica", "inserción", "Entrega registrada", "192.168.1.1")]
        elif "SELECT * FROM configuracion_sistema" in query:
            return [("clave1", "valor1", "Descripción 1"), ("clave2", "valor2", "Descripción 2")]
        elif "SELECT * FROM movimientos_contables" in query:
            return [("2025-04-14", "ingreso", 1000.0, "Pago", "Ref1", "Observación 1"), ("2025-04-15", "egreso", 500.0, "Compra", "Ref2", "Observación 2")]
        elif "SELECT * FROM mantenimientos" in query:
            return [("herramienta", 1, "preventivo", "2025-04-14", "Técnico 1", "Revisión general"), ("vehículo", 2, "correctivo", "2025-04-15", "Técnico 2", "Cambio de aceite")]
        elif "SELECT etapa, estado FROM etapas_fabricacion" in query:
            return [("corte", "finalizada"), ("armado", "en proceso")]
        return []

class TestProduccionModel(unittest.TestCase):

    def setUp(self):
        # Simulación de conexión a base de datos
        self.mock_db = MockDBConnection()
        self.produccion_model = ProduccionModel(self.mock_db)

    def test_iniciar_etapa_fabricacion(self):
        # Probar inicio de una etapa de fabricación
        self.produccion_model.iniciar_etapa_fabricacion(1, "corte", "2025-04-14")
        self.assertEqual(self.mock_db.last_query, "UPDATE etapas_fabricacion SET estado = 'en proceso', fecha_inicio = ? WHERE id = ? AND etapa = ?")
        self.assertEqual(self.mock_db.last_params, ("2025-04-14", 1, "corte"))

    def test_finalizar_etapa_fabricacion(self):
        # Probar finalización de una etapa de fabricación
        self.produccion_model.finalizar_etapa_fabricacion(1, "corte", "2025-04-15")
        self.assertEqual(self.mock_db.last_query, "UPDATE etapas_fabricacion SET estado = 'finalizada', fecha_fin = ? WHERE id = ? AND etapa = ?")
        self.assertEqual(self.mock_db.last_params, ("2025-04-15", 1, "corte"))

    def test_obtener_estado_abertura(self):
        # Probar obtención del estado de una abertura
        self.mock_db.set_query_result([("corte", "finalizada"), ("armado", "en proceso")])
        estado = self.produccion_model.obtener_estado_abertura(1)
        self.assertEqual(len(estado), 2)
        self.assertEqual(estado[0][1], "finalizada")

if __name__ == "__main__":
    unittest.main()
