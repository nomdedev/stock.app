import unittest
import sys
import os

# Agregar el directorio raíz del proyecto al PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.auditoria.model import AuditoriaModel

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

class TestAuditoriaModel(unittest.TestCase):

    def setUp(self):
        # Simulación de conexión a base de datos
        self.mock_db = Mock()
        self.auditoria_model = AuditoriaModel(self.mock_db)

    def test_registrar_evento(self):
        # Probar registro de un evento de auditoría
        self.auditoria_model.registrar_evento("usuarios", "inserción", "Usuario creado", "192.168.1.1")
        self.assertEqual(self.mock_db.last_query, "INSERT INTO auditorias_sistema (modulo_afectado, tipo_evento, detalle, ip_origen) VALUES (?, ?, ?, ?)")
        self.assertEqual(self.mock_db.last_params, ("usuarios", "inserción", "Usuario creado", "192.168.1.1"))

    def test_obtener_logs(self):
        # Probar obtención de logs de auditoría
        self.mock_db.set_query_result([
            (1, "2025-04-14 10:00:00", "usuarios", "inserción", "Usuario creado", "192.168.1.1"),
            (2, "2025-04-14 11:00:00", "inventario", "modificación", "Stock ajustado", "192.168.1.2")
        ])
        logs = self.auditoria_model.obtener_logs("usuarios")
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0][3], "inserción")

    def test_obtener_auditorias(self):
        # Simular datos de auditoría
        self.mock_db.ejecutar_query.return_value = [
            ("admin", "inventario", "inserción", "Agregó un nuevo ítem", "2025-04-14 10:00:00"),
            ("user1", "logística", "modificación", "Actualizó estado de entrega", "2025-04-14 11:00:00")
        ]

        filtros = {"modulo": "inventario"}
        auditorias = self.auditoria_model.obtener_auditorias(filtros)

        self.mock_db.ejecutar_query.assert_called_once_with(
            "SELECT * FROM auditorias_sistema WHERE modulo = ?", ("inventario",)
        )
        self.assertEqual(len(auditorias), 2)
        self.assertEqual(auditorias[0][0], "admin")

    def test_exportar_auditorias(self):
        # Simular exportación de auditorías
        self.mock_db.ejecutar_query.return_value = [
            ("admin", "inventario", "inserción", "Agregó un nuevo ítem", "2025-04-14 10:00:00"),
            ("user1", "logística", "modificación", "Actualizó estado de entrega", "2025-04-14 11:00:00")
        ]

        resultado = self.auditoria_model.exportar_auditorias("excel")

        self.assertEqual(resultado, "Auditorías exportadas a Excel.")

if __name__ == "__main__":
    unittest.main()
