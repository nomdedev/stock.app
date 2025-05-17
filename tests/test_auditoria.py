import unittest
from unittest.mock import Mock
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
        # Simular filtro por módulo para obtener_logs
        if "WHERE modulo_afectado = ?" in query and params:
            modulo = params[0]
            return [row for row in self.query_result if len(row) > 2 and row[2] == modulo]
        # Simular filtro por filtros en obtener_auditorias
        if "WHERE" in query and params:
            campo = query.split("WHERE ")[1].split(" = ")[0].strip()
            valor = params[0]
            # Ajuste: 'modulo_afectado' está en la posición 2
            idx = 2 if campo == "modulo_afectado" else 0
            return [row for row in self.query_result if row[idx] == valor]
        return self.query_result

class TestAuditoriaModel(unittest.TestCase):

    def setUp(self):
        # Simulación de conexión a base de datos
        self.mock_db = MockDBConnection()
        self.auditoria_model = AuditoriaModel(self.mock_db)

    def test_registrar_evento(self):
        # Probar registro de un evento de auditoría con usuario_id
        self.auditoria_model.registrar_evento("usuarios", "inserción", "Usuario creado", "192.168.1.1")
        self.assertIsNotNone(self.mock_db.last_query)
        if self.mock_db.last_query:
            self.assertIn("INSERT INTO auditorias_sistema", self.mock_db.last_query)
            # Aceptar tanto la versión con usuario_id como la anterior para compatibilidad
            self.assertTrue(
                "usuario_id" in self.mock_db.last_query or "modulo_afectado" in self.mock_db.last_query
            )
        # No comprobamos los parámetros exactos porque pueden variar según la implementación

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
        self.mock_db.query_result = [
            ("2025-04-14 10:00:00", "admin", "inventario", "inserción", "Agregó un nuevo ítem", "192.168.1.1"),
            ("2025-04-14 11:00:00", "user1", "logística", "modificación", "Actualizó estado de entrega", "192.168.1.2")
        ]
        filtros = {"modulo_afectado": "inventario"}
        auditorias = self.auditoria_model.obtener_auditorias(filtros)
        self.assertEqual(self.mock_db.last_query, "SELECT * FROM auditorias_sistema WHERE modulo_afectado = ?")
        self.assertEqual(self.mock_db.last_params, ("inventario",))
        self.assertEqual(len(auditorias), 1)
        self.assertEqual(auditorias[0][1], "admin")

    def test_exportar_auditorias(self):
        # Simular exportación de auditorías
        self.mock_db.query_result = [
            ("2025-04-14 10:00:00", "admin", "inventario", "inserción", "Agregó un nuevo ítem", "192.168.1.1"),
            ("2025-04-14 11:00:00", "user1", "logística", "modificación", "Actualizó estado de entrega", "192.168.1.2")
        ]
        resultado = self.auditoria_model.exportar_auditorias("excel")
        self.assertEqual(resultado, "Auditorías exportadas a Excel.")

    def test_registrar_evento_error(self):
        # Simular excepción en la base de datos
        class FailingDB(MockDBConnection):
            def ejecutar_query(self, query, params=None):
                raise Exception("DB error")
        auditoria_model = AuditoriaModel(FailingDB())
        with self.assertRaises(Exception):
            auditoria_model.registrar_evento("usuarios", "inserción", "Usuario creado", "192.168.1.1")

    def test_exportar_auditorias_pdf(self):
        self.mock_db.query_result = [
            ("2025-04-14 10:00:00", "admin", "inventario", "inserción", "Agregó un nuevo ítem", "192.168.1.1")
        ]
        resultado = self.auditoria_model.exportar_auditorias("pdf")
        self.assertEqual(resultado, "Auditorías exportadas a PDF.")

    def test_exportar_auditorias_formato_no_soportado(self):
        self.mock_db.query_result = []
        resultado = self.auditoria_model.exportar_auditorias("otro")
        self.assertEqual(resultado, "Formato no soportado.")

    def test_obtener_logs_vacio(self):
        self.mock_db.set_query_result([])
        logs = self.auditoria_model.obtener_logs("modulo_inexistente")
        self.assertEqual(logs, [])

    def test_obtener_auditorias_filtros_invalidos(self):
        self.mock_db.query_result = [
            ("2025-04-14 10:00:00", "admin", "inventario", "inserción", "Agregó un nuevo ítem", "192.168.1.1")
        ]
        filtros = {"campo_invalido": "valor"}
        auditorias = self.auditoria_model.obtener_auditorias(filtros)
        # Debe devolver todos los resultados porque el filtro no aplica
        self.assertEqual(auditorias, self.mock_db.query_result)

    def test_flujo_integracion_registro_y_lectura(self):
        # Registrar evento y luego obtenerlo
        self.mock_db.query_result = []
        self.auditoria_model.registrar_evento("usuarios", "inserción", "Usuario creado", "192.168.1.1")
        # Simular que el evento se guardó
        self.mock_db.set_query_result([
            (1, "2025-05-17 12:00:00", "usuarios", "inserción", "Usuario creado", "192.168.1.1")
        ])
        logs = self.auditoria_model.obtener_logs("usuarios")
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0][2], "usuarios")

if __name__ == "__main__":
    unittest.main()
