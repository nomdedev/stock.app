# --- TESTS DE CONFIGURACIÓN: USO SEGURO Y AISLADO, SIN CREDENCIALES REALES ---
# Todos los tests usan MockDBConnection, nunca una base real ni credenciales.
# Si se detecta un test que intenta conectar a una base real, debe ser refactorizado o migrado a integración.
# Si necesitas integración real, usa variables de entorno y archivos de configuración fuera del repo.
# --- FIN DE NOTA DE SEGURIDAD ---

import unittest
from modules.configuracion.model import ConfiguracionModel
from modules.configuracion.view import ConfiguracionView
from PyQt6.QtWidgets import QApplication

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
        return self.query_result

class TestConfiguracionModel(unittest.TestCase):

    def setUp(self):
        # Simulación de conexión a base de datos
        self.mock_db = MockDBConnection()
        self.config_model = ConfiguracionModel(self.mock_db)

    def test_obtener_configuracion(self):
        # Simular datos de configuración
        self.mock_db.set_query_result([
            ("modo_offline", "False", "Modo offline activado/desactivado"),
            ("notificaciones_activas", "True", "Estado de notificaciones")
        ])
        configuracion = self.config_model.obtener_configuracion()
        self.assertEqual(len(configuracion), 2)
        self.assertEqual(configuracion[0][0], "modo_offline")

    def test_actualizar_configuracion(self):
        # Probar actualización de configuración
        self.config_model.actualizar_configuracion("modo_offline", "True")
        self.assertEqual(self.mock_db.last_query, "UPDATE configuracion_sistema SET valor = ? WHERE clave = ?")
        self.assertEqual(self.mock_db.last_params, ("True", "modo_offline"))

    def test_activar_modo_offline(self):
        self.config_model.activar_modo_offline()
        self.assertEqual(self.mock_db.last_query, "UPDATE configuracion_sistema SET valor = 'True' WHERE clave = 'modo_offline'")

    def test_desactivar_modo_offline(self):
        self.config_model.desactivar_modo_offline()
        self.assertEqual(self.mock_db.last_query, "UPDATE configuracion_sistema SET valor = 'False' WHERE clave = 'modo_offline'")

    def test_actualizar_estado_notificaciones(self):
        self.config_model.actualizar_estado_notificaciones(True)
        self.assertEqual(self.mock_db.last_query, "UPDATE configuracion_sistema SET valor = ? WHERE clave = 'notificaciones_activas'")
        self.assertEqual(self.mock_db.last_params, ("True",))

class TestConfiguracionView(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Inicializa QApplication solo una vez para todos los tests de la vista
        cls._app = QApplication.instance() or QApplication([])

    def test_boton_activar_offline_existe(self):
        view = ConfiguracionView()
        self.assertTrue(hasattr(view, "boton_activar_offline"), "El botón 'boton_activar_offline' no está definido.")

if __name__ == "__main__":
    unittest.main()
