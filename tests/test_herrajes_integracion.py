from unittest.mock import Mock
from modules.herrajes.model import HerrajesModel

class MockDBConnection:
    def __init__(self):
        self.materiales = []
        self.last_id = 1
    def ejecutar_query(self, query, params=None):
        if "INSERT INTO materiales" in query:
            # (codigo, descripcion, cantidad, ubicacion, observaciones)
            material = (self.last_id,) + tuple(params)
            self.materiales.append(material)
            self.last_id += 1
            return None
        if "SELECT * FROM materiales" in query:
            return list(self.materiales)
        if "UPDATE materiales" in query:
            for i, m in enumerate(self.materiales):
                if m[0] == params[5]:
                    self.materiales[i] = (m[0], params[0], params[1], params[2], params[3], params[4])
            return None
        if "DELETE FROM materiales" in query:
            self.materiales = [m for m in self.materiales if m[0] != params[0]]
            return None
        return []

class MockHerrajesView:
    def __init__(self):
        self.tabla_data = []
        self.label = Mock()
    def actualizar_tabla(self, data):
        self.tabla_data = data

class TestHerrajesIntegracion:
    def setUp(self):
        self.mock_db = MockDBConnection()
        self.model = HerrajesModel(self.mock_db)
        self.view = MockHerrajesView()
    def tearDown(self):
        self.mock_db.materiales.clear()
    def test_agregar_y_reflejar_material(self):
        self.model.agregar_material("C-001", "Herraje demo", 10, "Depósito", "Ninguna")
        materiales = self.mock_db.ejecutar_query("SELECT * FROM materiales")
        self.assertTrue(any(m[1] == "C-001" for m in materiales))
        self.view.actualizar_tabla(materiales)
        self.assertEqual(self.view.tabla_data, materiales)
    def test_actualizar_material(self):
        self.model.agregar_material("C-002", "Herraje X", 5, "Almacén", "Obs")
        materiales = self.mock_db.ejecutar_query("SELECT * FROM materiales")
        id_material = materiales[-1][0]
        self.model.actualizar_material(id_material, "C-002", "Herraje X mod", 7, "Almacén 2", "Obs mod")
        materiales = self.mock_db.ejecutar_query("SELECT * FROM materiales")
        self.assertTrue(any(m[2] == "Herraje X mod" for m in materiales))
        self.view.actualizar_tabla(materiales)
        self.assertEqual(self.view.tabla_data, materiales)
    def test_eliminar_material(self):
        self.model.agregar_material("C-003", "Herraje Y", 3, "Depósito", "-")
        materiales = self.mock_db.ejecutar_query("SELECT * FROM materiales")
        id_material = materiales[-1][0]
        self.model.eliminar_material(id_material)
        materiales = self.mock_db.ejecutar_query("SELECT * FROM materiales")
        self.assertFalse(any(m[0] == id_material for m in materiales))
        self.view.actualizar_tabla(materiales)
        self.assertEqual(self.view.tabla_data, materiales)
