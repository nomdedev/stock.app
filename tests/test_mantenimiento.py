import unittest
from modules.mantenimiento.model import MantenimientoModel

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

class TestMantenimientoModel(unittest.TestCase):

    def setUp(self):
        # Simulación de conexión a base de datos
        self.mock_db = MockDBConnection()
        self.mantenimiento_model = MantenimientoModel(self.mock_db)

    def test_registrar_mantenimiento(self):
        # Probar registro de un mantenimiento
        self.mantenimiento_model.registrar_mantenimiento("herramienta", 1, "preventivo", "2025-04-14", "Revisión general")
        self.assertEqual(self.mock_db.last_query, "INSERT INTO mantenimientos (tipo_objeto, id_objeto, tipo_mantenimiento, fecha_realizacion, observaciones) VALUES (?, ?, ?, ?, ?)")
        self.assertEqual(self.mock_db.last_params, ("herramienta", 1, "preventivo", "2025-04-14", "Revisión general"))

    def test_programar_tarea_recurrente(self):
        # Probar programación de una tarea recurrente
        self.mantenimiento_model.programar_tarea_recurrente("vehículo", 2, "Cambio de aceite", 30, "2025-05-01")
        self.assertEqual(self.mock_db.last_query, "INSERT INTO tareas_recurrentes (tipo_objeto, id_objeto, descripcion, frecuencia_dias, proxima_fecha) VALUES (?, ?, ?, ?, ?)")
        self.assertEqual(self.mock_db.last_params, ("vehículo", 2, "Cambio de aceite", 30, "2025-05-01"))

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
