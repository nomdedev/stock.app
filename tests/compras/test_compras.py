# --- TESTS DE AUDITORÍA: USO SEGURO Y AISLADO, SIN CREDENCIALES REALES ---
# Todos los tests usan MockDBConnection, nunca una base real ni credenciales.
# Si se detecta un test que intenta conectar a una base real, debe ser refactorizado o migrado a integración.
# Si necesitas integración real, usa variables de entorno y archivos de configuración fuera del repo.
# Ejemplo seguro (NO USAR EN TESTS UNITARIOS):
# import os
# db_user = os.environ.get('DB_USER')
# db_pass = os.environ.get('DB_PASS')
# ...
# --- FIN DE NOTA DE SEGURIDAD ---

import unittest
import sys
import os

# Agregar el directorio raíz del proyecto al PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.compras.model import ComprasModel  # Confirmar que la ruta es correcta

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
        """Probar creación de un pedido usando solo mocks, sin base real.
        
        Este test verifica que el método 'crear_pedido' de la clase 'ComprasModel'
        genere la consulta SQL correcta con los parámetros esperados. Se utiliza
        MockDBConnection para simular la interacción con la base de datos, asegurando
        que no se realicen conexiones reales ni se expongan credenciales.

        Asserts:
            - La consulta SQL generada es la esperada.
            - Los parámetros de la consulta coinciden con los valores proporcionados.
        """
        self.compras_model.crear_pedido(1, "alta", "Necesidad urgente de materiales")
        self.assertEqual(self.mock_db.last_query, "INSERT INTO pedidos_compra (solicitado_por, prioridad, observaciones) VALUES (?, ?, ?)")
        self.assertEqual(self.mock_db.last_params, (1, "alta", "Necesidad urgente de materiales"))

    def test_agregar_item_pedido(self):
        """Probar agregar ítem a un pedido usando solo mocks, sin base real.
        
        Este test verifica que el método 'agregar_item_pedido' de la clase 'ComprasModel'
        genere la consulta SQL correcta con los parámetros esperados. Se utiliza
        MockDBConnection para simular la interacción con la base de datos, asegurando
        que no se realicen conexiones reales ni se expongan credenciales.

        Asserts:
            - La consulta SQL generada es la esperada.
            - Los parámetros de la consulta coinciden con los valores proporcionados.
        """
        self.compras_model.agregar_item_pedido(1, 101, 50, "unidad")
        self.assertEqual(self.mock_db.last_query, "INSERT INTO detalle_pedido (id_pedido, id_item, cantidad_solicitada, unidad) VALUES (?, ?, ?, ?)")
        self.assertEqual(self.mock_db.last_params, (1, 101, 50, "unidad"))

    def test_aprobar_pedido(self):
        """Probar aprobación de un pedido usando solo mocks, sin base real.
        
        Este test verifica que el método 'aprobar_pedido' de la clase 'ComprasModel'
        genere la consulta SQL correcta con los parámetros esperados. Se utiliza
        MockDBConnection para simular la interacción con la base de datos, asegurando
        que no se realicen conexiones reales ni se expongan credenciales.

        Asserts:
            - La consulta SQL generada es la esperada.
            - Los parámetros de la consulta coinciden con los valores proporcionados.
        """
        self.compras_model.aprobar_pedido(1)
        self.assertEqual(self.mock_db.last_query, "UPDATE pedidos_compra SET estado = 'aprobado' WHERE id = ?")
        self.assertEqual(self.mock_db.last_params, (1,))

if __name__ == "__main__":
    unittest.main()
