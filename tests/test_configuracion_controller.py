import unittest
from unittest.mock import Mock, MagicMock
from modules.configuracion.controller import ConfiguracionController

class MockModel:
    def obtener_configuracion(self):
        return [
            ("nombre_app", "StockApp", "Nombre de la app"),
            ("zona_horaria", "America/Argentina/Buenos_Aires", "Zona horaria"),
        ]
    def obtener_apariencia_usuario(self, user_id):
        return [("light", "es", True, "12")]
    def actualizar_configuracion(self, clave, valor):
        self.last_update = (clave, valor)
    def actualizar_apariencia_usuario(self, user_id, datos):
        self.last_apariencia = (user_id, datos)
    def activar_modo_offline(self):
        self.offline = True
    def desactivar_modo_offline(self):
        self.offline = False
    def obtener_estado_notificaciones(self):
        return False
    def actualizar_estado_notificaciones(self, estado):
        self.notificaciones = estado
    def guardar_configuracion_conexion(self, datos):
        self.last_conexion = datos

class MockView:
    def __init__(self):
        self.nombre_app_input = MagicMock()
        self.zona_horaria_input = MagicMock()
        self.modo_color_input = MagicMock()
        self.idioma_input = MagicMock()
        self.notificaciones_checkbox = MagicMock()
        self.tamaño_fuente_input = MagicMock()
        self.label = MagicMock()
        self.resultado_conexion_label = MagicMock()
    def mostrar_mensaje(self, mensaje, tipo="info", destino="label"):
        self.last_mensaje = (mensaje, tipo, destino)

class TestConfiguracionController(unittest.TestCase):
    def setUp(self):
        self.model = MockModel()
        self.view = MockView()
        self.db = Mock()
        self.usuarios_model = Mock()
        self.usuarios_model.tiene_permiso.return_value = True
        self.usuario_actual = {'rol': 'admin', 'nombre': 'test'}
        self.controller = ConfiguracionController(self.model, self.view, self.db, self.usuarios_model, self.usuario_actual)

    def test_cargar_configuracion(self):
        self.controller.cargar_configuracion()
        self.assertTrue(self.view.nombre_app_input.setText.called)
        self.assertTrue(self.view.zona_horaria_input.setCurrentText.called)

    def test_guardar_cambios(self):
        self.view.nombre_app_input.text.return_value = "StockApp"
        self.view.zona_horaria_input.currentText.return_value = "America/Argentina/Buenos_Aires"
        self.view.modo_color_input.currentText.return_value = "light"
        self.view.idioma_input.currentText.return_value = "es"
        self.view.notificaciones_checkbox.isChecked.return_value = True
        self.view.tamaño_fuente_input.currentText.return_value = "12"
        self.controller.guardar_cambios()
        self.assertEqual(self.model.last_update, ("nombre_app", "StockApp"))
        self.assertEqual(self.model.last_apariencia, (1, ("light", "es", True, "12")))
        self.assertIn("exito", self.view.label.setText.call_args[0][0])

    def test_activar_modo_offline(self):
        self.controller.activar_modo_offline()
        self.assertTrue(self.model.offline)
        self.assertIn("offline", self.view.label.setText.call_args[0][0].lower())

    def test_desactivar_modo_offline(self):
        self.model.offline = True
        self.controller.desactivar_modo_offline()
        self.assertFalse(self.model.offline)
        self.assertIn("offline", self.view.label.setText.call_args[0][0].lower())

    def test_cambiar_estado_notificaciones(self):
        self.model.notificaciones = False
        self.controller.cambiar_estado_notificaciones()
        self.assertTrue(self.model.notificaciones)
        self.assertIn("notificaciones", self.view.label.setText.call_args[0][0].lower())

if __name__ == "__main__":
    unittest.main()
