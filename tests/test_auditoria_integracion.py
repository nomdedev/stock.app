import unittest
from unittest.mock import Mock
from modules.auditoria.model import AuditoriaModel

class MockDBConnection:
    def __init__(self):
        self.auditorias = []
        self.last_id = 1
        self.last_query = None
        self.last_params = None
    def ejecutar_query(self, query, params=None):
        self.last_query = query
        self.last_params = params
        if "INSERT INTO auditorias_sistema" in query:
            # (modulo_afectado, tipo_evento, detalle, ip_origen)
            auditoria = (self.last_id,) + tuple(params)
            self.auditorias.append(auditoria)
            self.last_id += 1
            return None
        if "SELECT * FROM auditorias_sistema" in query:
            if params:
                # Filtrar por campo
                campo = query.split("WHERE ")[1].split(" = ")[0]
                valor = params[0]
                return [a for a in self.auditorias if a[1] == valor]
            return list(self.auditorias)
        return []

class MockAuditoriaView:
    def __init__(self):
        self.tabla_data = []
        self.label = Mock()
    def actualizar_tabla(self, data):
        self.tabla_data = data

class TestAuditoriaIntegracion(unittest.TestCase):
    def setUp(self):
        self.mock_db = MockDBConnection()
        self.model = AuditoriaModel(self.mock_db)
        self.view = MockAuditoriaView()
    def tearDown(self):
        self.mock_db.auditorias.clear()
    def test_registrar_y_reflejar_evento(self):
        self.model.db.ejecutar_query("INSERT INTO auditorias_sistema (modulo_afectado, tipo_evento, detalle, ip_origen) VALUES (?, ?, ?, ?)", ("usuarios", "inserción", "Usuario creado", "192.168.1.1"))
        auditorias = self.mock_db.ejecutar_query("SELECT * FROM auditorias_sistema")
        self.assertTrue(any(a[1] == "usuarios" for a in auditorias))
        self.view.actualizar_tabla(auditorias)
        self.assertEqual(self.view.tabla_data, auditorias)
    def test_filtrar_por_modulo(self):
        self.model.db.ejecutar_query("INSERT INTO auditorias_sistema (modulo_afectado, tipo_evento, detalle, ip_origen) VALUES (?, ?, ?, ?)", ("inventario", "modificación", "Stock ajustado", "192.168.1.2"))
        auditorias = self.mock_db.ejecutar_query("SELECT * FROM auditorias_sistema WHERE modulo_afectado = ?", ("inventario",))
        self.assertTrue(all(a[1] == "inventario" for a in auditorias))
        self.view.actualizar_tabla(auditorias)
        self.assertEqual(self.view.tabla_data, auditorias)

if __name__ == "__main__":
    unittest.main()
