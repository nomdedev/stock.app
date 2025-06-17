# --- TESTS DE AUDITORÍA: USO SEGURO Y AISLADO, SIN CREDENCIALES REALES ---
# Todos los tests usan MockDBConnection, nunca una base real ni credenciales.
# Si se detecta un test que intenta conectar a una base real, debe ser refactorizado o migrado a integración.
#
# Si necesitas integración real, usa variables de entorno y archivos de configuración fuera del repo.
# Ejemplo seguro (NO USAR EN TESTS UNITARIOS):
# import os
# db_user = os.environ.get('DB_USER')
# db_pass = os.environ.get('DB_PASS')
# ...
# --- FIN DE NOTA DE SEGURIDAD ---

import sys
import os
import unittest
from unittest.mock import MagicMock
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
        # Simulación de conexión a base de datos (no usa credenciales reales)
        self.mock_db = MockDBConnection()
        self.auditoria_model = AuditoriaModel(self.mock_db)

    def test_registrar_evento(self):
        """Probar registro de un evento de auditoría con usuario_id explícito."""
        usuario_id = 1
        modulo = "usuarios"
        tipo_evento = "inserción"
        detalle = "Usuario creado"
        ip_origen = "192.168.1.1"
        self.auditoria_model.registrar_evento(usuario_id, modulo, tipo_evento, detalle, ip_origen)
        self.assertIsNotNone(self.mock_db.last_query)
        if self.mock_db.last_query:
            self.assertIn("INSERT INTO auditorias_sistema", self.mock_db.last_query)
            self.assertIn("usuario_id", self.mock_db.last_query)

    def test_registrar_evento_faltan_argumentos(self):
        """Debe retornar False y loggear si falta usuario_id, modulo o tipo_evento."""
        usuario_id = None
        modulo = "usuarios"
        tipo_evento = "inserción"
        detalle = "Usuario creado"
        ip_origen = "192.168.1.1"
        resultado = self.auditoria_model.registrar_evento(usuario_id, modulo, tipo_evento, detalle, ip_origen)
        self.assertFalse(resultado)

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
        self.assertIn("Auditorías exportadas a Excel", resultado)

    def test_registrar_evento_error(self):
        """Debe retornar False si la base de datos falla."""
        class FailingDB(MockDBConnection):
            def ejecutar_query(self, query, params=None):
                raise Exception("DB error")
        auditoria_model = AuditoriaModel(FailingDB())
        resultado = auditoria_model.registrar_evento(1, "usuarios", "inserción", "Usuario creado", "192.168.1.1")
        self.assertFalse(resultado)

    def test_exportar_auditorias_pdf(self):
        self.mock_db.query_result = [
            ("2025-04-14 10:00:00", "admin", "inventario", "inserción", "Agregó un nuevo ítem", "192.168.1.1")
        ]
        resultado = self.auditoria_model.exportar_auditorias("pdf")
        self.assertIn("Auditorías exportadas a PDF", resultado)

    def test_exportar_auditorias_formato_no_soportado(self):
        self.mock_db.query_result = []
        resultado = self.auditoria_model.exportar_auditorias("otro")
        self.assertIn("Formato no soportado", resultado)

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
        """Registrar evento y luego obtenerlo (flujo completo)."""
        usuario_id = 1
        modulo = "usuarios"
        tipo_evento = "inserción"
        detalle = "Usuario creado"
        ip_origen = "192.168.1.1"
        self.mock_db.query_result = []
        self.auditoria_model.registrar_evento(usuario_id, modulo, tipo_evento, detalle, ip_origen)
        self.mock_db.set_query_result([
            (1, "2025-05-17 12:00:00", "usuarios", "inserción", "Usuario creado", "192.168.1.1")
        ])
        logs = self.auditoria_model.obtener_logs("usuarios")
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0][2], "usuarios")

    def test_registrar_evento_guarda_evento(self):
        """Probar que registrar_evento guarda correctamente el evento en la base mockeada.
        Se espera que los parámetros usuario, acción y descripción estén en last_params.
        """
        usuario_id = 1
        modulo = 'usuarios'
        tipo_evento = 'login'
        detalle = 'Inicio de sesión exitoso'
        ip_origen = '127.0.0.1'
        self.mock_db.query_result = []
        # Act
        self.auditoria_model.registrar_evento(usuario_id, modulo, tipo_evento, detalle, ip_origen)
        # Assert
        self.assertIsNotNone(self.mock_db.last_query)
        if self.mock_db.last_query:
            self.assertIn('INSERT', self.mock_db.last_query.upper())
        self.assertIsNotNone(self.mock_db.last_params)
        if self.mock_db.last_params:
            self.assertIn(usuario_id, self.mock_db.last_params)
            self.assertIn(modulo, self.mock_db.last_params)
            self.assertIn(tipo_evento, self.mock_db.last_params)
            self.assertIn(detalle, self.mock_db.last_params)
            self.assertIn(ip_origen, self.mock_db.last_params)

    def test_obtener_eventos_retorna_lista(self):
        """Probar que obtener_logs retorna la lista de eventos simulada en la base mockeada."""
        eventos = [
            (1, '2025-05-23 10:00:00', 'usuarios', 'login', 'Inicio de sesión exitoso', '127.0.0.1'),
            (2, '2025-05-23 11:00:00', 'usuarios', 'logout', 'Cierre de sesión', '127.0.0.1')
        ]
        self.mock_db.set_query_result(eventos)
        # Act
        resultado = self.auditoria_model.obtener_logs('usuarios')
        # Assert
        self.assertEqual(resultado, eventos)

    def test_no_conexion_real(self):
        """Verifica que la base de datos usada es un mock y no una conexión real."""
        self.assertIsInstance(self.auditoria_model.db, MockDBConnection)

if __name__ == "__main__":
    unittest.main()
