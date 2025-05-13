import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest
from unittest.mock import Mock
from modules.vidrios.model import VidriosModel

class MockDBConnection:
    def __init__(self):
        self.vidrios = []
        self.vidrios_obras = []
        self.last_id = 1
    def ejecutar_query(self, query, params=None):
        if "INSERT INTO vidrios (" in query:
            # (tipo, ancho, alto, cantidad, proveedor, fecha_entrega)
            vidrio = (self.last_id,) + tuple(params)
            self.vidrios.append(vidrio)
            self.last_id += 1
            return None
        if "SELECT * FROM vidrios" in query:
            return list(self.vidrios)
        if "INSERT INTO vidrios_obras" in query:
            self.vidrios_obras.append(tuple(params))
            return None
        return []

class MockVidriosView:
    def __init__(self):
        self.tabla_data = []
        self.label = Mock()
    def actualizar_tabla(self, data):
        self.tabla_data = data

class TestVidriosIntegracion(unittest.TestCase):
    def setUp(self):
        self.mock_db = MockDBConnection()
        self.model = VidriosModel(self.mock_db)
        self.view = MockVidriosView()
    def tearDown(self):
        self.mock_db.vidrios.clear()
        self.mock_db.vidrios_obras.clear()
    def test_agregar_y_reflejar_vidrio(self):
        datos = ("Laminado", 2.5, 1.2, 10, "Proveedor X", "2025-06-01")
        self.model.agregar_vidrio(datos)
        vidrios = self.mock_db.ejecutar_query("SELECT * FROM vidrios")
        self.assertTrue(any(v[1] == "Laminado" for v in vidrios))
        self.view.actualizar_tabla(vidrios)
        self.assertEqual(self.view.tabla_data, vidrios)
    def test_asignar_a_obra(self):
        datos = ("Templado", 1.8, 1.0, 5, "Proveedor Y", "2025-06-10")
        self.model.agregar_vidrio(datos)
        vidrios = self.mock_db.ejecutar_query("SELECT * FROM vidrios")
        id_vidrio = vidrios[-1][0]
        self.model.asignar_a_obra(id_vidrio, 101)
        self.assertIn((id_vidrio, 101), self.mock_db.vidrios_obras)

if __name__ == "__main__":
    unittest.main()
