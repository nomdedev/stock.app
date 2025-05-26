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
        # Agrego los widgets críticos para los tests de configuración de conexión
        self.server_input = MagicMock()
        self.username_input = MagicMock()
        self.password_input = MagicMock()
        self.default_db_input = MagicMock()
        self.port_input = MagicMock()
        self.timeout_input = MagicMock()
    def mostrar_mensaje(self, mensaje, tipo="info", destino="label"):
        self.last_mensaje = (mensaje, tipo, destino)

class TestConfiguracionController(unittest.TestCase):
    def setUp(self):
        self.model = MockModel()
        self.view = MockView()
        # Agrego los widgets críticos que faltan para los tests de configuración
        self.view.server_input = MagicMock()
        self.view.username_input = MagicMock()
        self.view.password_input = MagicMock()
        self.view.default_db_input = MagicMock()
        self.view.port_input = MagicMock()
        self.view.timeout_input = MagicMock()
        self.db = Mock()
        self.usuarios_model = Mock()
        self.controller = ConfiguracionController(self.model, self.view, self.db, self.usuarios_model)

    def test_cargar_configuracion(self):
        """Carga la configuración y verifica que los widgets reciban los valores correctos."""
        self.controller.cargar_configuracion()
        self.view.nombre_app_input.setText.assert_called_with("StockApp")
        self.view.zona_horaria_input.setText.assert_called_with("America/Argentina/Buenos_Aires")

    def test_guardar_cambios(self):
        """Guarda cambios y verifica que se actualice el modelo correctamente."""
        self.view.nombre_app_input.text.return_value = "StockApp2"
        self.view.zona_horaria_input.text.return_value = "America/Argentina/Cordoba"
        self.controller.guardar_cambios()
        self.assertEqual(self.model.last_update, ("nombre_app", "StockApp2"))

    def test_activar_modo_offline(self):
        """Activa el modo offline y verifica el estado en el modelo."""
        self.controller.activar_modo_offline()
        self.assertTrue(self.model.offline)

    def test_desactivar_modo_offline(self):
        """Desactiva el modo offline y verifica el estado en el modelo."""
        self.model.offline = True
        self.controller.desactivar_modo_offline()
        self.assertFalse(self.model.offline)

    def test_cambiar_estado_notificaciones(self):
        """Cambia el estado de notificaciones y verifica el cambio en el modelo."""
        # Estado inicial: False
        self.model.notificaciones = False
        self.controller.cambiar_estado_notificaciones()
        self.assertTrue(self.model.notificaciones)
        self.controller.cambiar_estado_notificaciones()
        self.assertFalse(self.model.notificaciones)

    def test_guardar_configuracion_conexion_campos_obligatorios(self):
        """Verifica que se muestre error si faltan campos obligatorios en la conexión."""
        # Simula campos vacíos y verifica feedback visual de error
        self.view.server_input = MagicMock()
        self.view.server_input.text.return_value = ''
        self.view.username_input = MagicMock()
        self.view.username_input.text.return_value = ''
        self.view.password_input = MagicMock()
        self.view.password_input.text.return_value = ''
        self.view.default_db_input = MagicMock()
        self.view.default_db_input.text.return_value = ''
        self.controller.guardar_configuracion_conexion()
        self.assertIn("obligatorio", self.view.last_mensaje[0])
        self.assertEqual(self.view.last_mensaje[1], "error")

    def test_guardar_cambios_nombre_vacio(self):
        """Verifica que se muestre error si el nombre de la app está vacío."""
        self.view.nombre_app_input.text.return_value = ''
        self.controller.guardar_cambios()
        self.assertIn("no puede estar vacío", self.view.last_mensaje[0])
        self.assertEqual(self.view.last_mensaje[1], "error")

    def test_feedback_visual_exito(self):
        """El feedback visual de éxito usa color y emoji correctos."""
        self.controller.mostrar_mensaje("Prueba exitosa", tipo="exito")
        self.assertIn("Prueba exitosa", self.view.label.setText.call_args[0][0])
        self.assertIn("#22c55e", self.view.label.setText.call_args[0][0])

    def test_feedback_visual_error(self):
        """El feedback visual de error usa color y emoji correctos."""
        self.controller.mostrar_mensaje("Error crítico", tipo="error")
        self.assertIn("Error crítico", self.view.label.setText.call_args[0][0])
        self.assertIn("#ef4444", self.view.label.setText.call_args[0][0])

    def test_guardar_configuracion_conexion_tipo_invalido(self):
        """Debe mostrar error si el puerto o timeout no son numéricos."""
        self.view.server_input.text.return_value = '192.168.1.100'
        self.view.username_input.text.return_value = 'admin'
        self.view.password_input.text.return_value = '1234'
        self.view.default_db_input.text.return_value = 'inventario'
        self.view.port_input.text.return_value = 'no-num'
        self.view.timeout_input.text.return_value = 'abc'
        self.controller.guardar_configuracion_conexion()
        self.assertIn("error", self.view.last_mensaje[1])

    def test_guardar_configuracion_conexion_widget_faltante(self):
        """Debe mostrar advertencia si falta un widget crítico."""
        del self.view.server_input
        self.controller.guardar_configuracion_conexion()
        self.assertIn("obligatorio", self.view.last_mensaje[0])
        self.assertEqual(self.view.last_mensaje[1], "error")

    def test_feedback_visual_advertencia(self):
        """El feedback visual de advertencia usa color y emoji correctos."""
        self.controller.mostrar_mensaje("Advertencia de prueba", tipo="advertencia")
        self.assertIn("Advertencia de prueba", self.view.label.setText.call_args[0][0])
        self.assertIn("#f59e42", self.view.label.setText.call_args[0][0])
        self.assertIn("⚠️", self.view.label.setText.call_args[0][0])

    def test_guardar_cambios_tipo_incorrecto(self):
        """Debe mostrar error si un campo tiene tipo incorrecto (ej: notificaciones no bool)."""
        self.view.nombre_app_input.text.return_value = "StockApp"
        self.view.zona_horaria_input.text.return_value = "America/Argentina/Buenos_Aires"
        self.view.notificaciones_checkbox.isChecked.return_value = "no-bool"
        self.controller.guardar_cambios()
        self.assertIn("error", self.view.last_mensaje[1])

    def test_guardar_cambios_widget_faltante(self):
        """Debe mostrar advertencia si falta un widget crítico al guardar cambios."""
        del self.view.nombre_app_input
        self.controller.guardar_cambios()
        self.assertIn("no se encontró", self.view.last_mensaje[0].lower())
        self.assertIn("advertencia", self.view.last_mensaje[1])

    def test_probar_conexion_bd_error(self):
        """Debe mostrar error visual si la conexión falla (simulación de excepción)."""
        self.view.server_input.text.return_value = '192.168.1.100'
        self.view.username_input.text.return_value = 'admin'
        self.view.password_input.text.return_value = '1234'
        self.view.default_db_input.text.return_value = 'inventario'
        self.view.port_input.text.return_value = '1433'
        self.view.timeout_input.text.return_value = '5'
        # Forzar excepción en pyodbc.connect
        import modules.configuracion.controller as config_controller
        original_connect = getattr(config_controller, 'pyodbc', None)
        class DummyPyodbc:
            def connect(*args, **kwargs):
                raise Exception("Fallo de conexión simulado")
        config_controller.pyodbc = DummyPyodbc
        self.controller.probar_conexion_bd()
        self.assertIn("error", self.view.last_mensaje[1])
        # Restaurar
        if original_connect:
            config_controller.pyodbc = original_connect

if __name__ == "__main__":
    unittest.main()
