# --- TESTS DE MANTENIMIENTO: USO SEGURO Y AISLADO, SIN CREDENCIALES REALES ---
# Todos los tests usan MockDBConnection, nunca una base real ni credenciales.
# Si se detecta un test que intenta conectar a una base real, debe ser refactorizado o migrado a integración.
# Si necesitas integración real, usa variables de entorno y archivos de configuración fuera del repo.
# --- FIN DE NOTA DE SEGURIDAD ---

import unittest
import sys
import os

# Agregar el directorio raíz del proyecto al PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.mantenimiento.model import MantenimientoModel  # Confirmar que la ruta es correcta

class MockDBConnection:
    def __init__(self):
        self.last_query = None
        self.last_params = None
        self.query_result = []

    def execute(self, query, params=None):
        self.last_query = query
        self.last_params = params

    def set_query_result(self, result):
        self.query_result = result
    def ejecutar_query(self, query, params=None):
        self.execute(query, params)
        return self.query_result
    def fetchall(self):
        return self.query_result
    def fetchone(self):
        return self.query_result[0] if self.query_result else None

class TestMantenimientoModel(unittest.TestCase):

    def setUp(self):
        # Simulación de conexión a base de datos
        self.mock_db = MockDBConnection()
        self.mantenimiento_model = MantenimientoModel(self.mock_db)

    def test_registrar_mantenimiento(self):
        # Probar registro de un mantenimiento
        datos = ("herramienta", 1, "preventivo", "2025-04-14", 10, "Revisión general", "firma123")
        self.mantenimiento_model.registrar_mantenimiento(datos)
        self.assertIsNotNone(self.mock_db.last_query)
        if self.mock_db.last_query is not None:
            self.assertIn("INSERT INTO mantenimientos", self.mock_db.last_query)
        self.assertEqual(self.mock_db.last_params, datos)

    def test_programar_tarea_recurrente(self):
        # Probar programación de una tarea recurrente
        datos = ("vehículo", 2, "Cambio de aceite", 30, "2025-05-01", "Juan Pérez")
        self.mantenimiento_model.agregar_tarea_recurrente(datos)
        self.assertIsNotNone(self.mock_db.last_query)
        if self.mock_db.last_query is not None:
            self.assertIn("INSERT INTO tareas_recurrentes", self.mock_db.last_query)
        self.assertEqual(self.mock_db.last_params, datos)

    def test_obtener_historial_mantenimientos(self):
        # Probar obtención del historial de mantenimientos
        self.mock_db.set_query_result([
            (1, "herramienta", "preventivo", "2025-04-14", "Revisión general"),
            (2, "vehículo", "correctivo", "2025-04-10", "Reparación de frenos")
        ])
        historial = self.mantenimiento_model.obtener_historial_mantenimientos(1)
        self.assertEqual(len(historial), 2)
        self.assertEqual(historial[0][1], "herramienta")

if __name__ == "__main__":
    unittest.main()
