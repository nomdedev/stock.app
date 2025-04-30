import unittest
from modules.compras.model import ComprasModel

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

class TestComprasModel(unittest.TestCase):

    def setUp(self):
        # Simulación de conexión a base de datos
        self.mock_db = MockDBConnection()
        self.compras_model = ComprasModel(self.mock_db)

    def test_crear_pedido(self):
        # Probar creación de un pedido
        self.compras_model.crear_pedido(1, "alta", "Necesidad urgente de materiales")
        self.assertEqual(self.mock_db.last_query, "INSERT INTO pedidos_compra (solicitado_por, prioridad, observaciones) VALUES (?, ?, ?)")
        self.assertEqual(self.mock_db.last_params, (1, "alta", "Necesidad urgente de materiales"))

    def test_agregar_item_pedido(self):
        # Probar agregar ítem a un pedido
        self.compras_model.agregar_item_pedido(1, 101, 50, "unidad")
        self.assertEqual(self.mock_db.last_query, "INSERT INTO detalle_pedido (id_pedido, id_item, cantidad_solicitada, unidad) VALUES (?, ?, ?, ?)")
        self.assertEqual(self.mock_db.last_params, (1, 101, 50, "unidad"))

    def test_aprobar_pedido(self):
        # Probar aprobación de un pedido
        self.compras_model.aprobar_pedido(1)
        self.assertEqual(self.mock_db.last_query, "UPDATE pedidos_compra SET estado = 'aprobado' WHERE id = ?")
        self.assertEqual(self.mock_db.last_params, (1,))

if __name__ == "__main__":
    unittest.main()
