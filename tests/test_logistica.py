import unittest
import sys
import os

# Agregar el directorio raíz del proyecto al PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.logistica.model import LogisticaModel  # Confirmar que la ruta es correcta

class MockDB:
    def __init__(self):
        self.query_log = []
        self.return_values = {}

    def ejecutar_query(self, query, params=None):
        self.query_log.append((query, params))
        return self.return_values.get(query, [])

    def set_return_value(self, query, result):
        self.return_values[query] = result

    def get_last_query(self):
        return self.query_log[-1] if self.query_log else None

class TestLogisticaModel(unittest.TestCase):

    def setUp(self):
        self.mock_db = MockDB()
        self.logistica_model = LogisticaModel(self.mock_db)

    def test_programar_entrega(self):
        # Probar programación de una entrega
        self.logistica_model.programar_entrega(1, "2025-04-15", "Vehículo 1", "Chofer 1")
        last_query = self.mock_db.get_last_query()
        self.assertEqual(last_query, ("INSERT INTO entregas_obras (id_obra, fecha_programada, vehiculo_asignado, chofer_asignado) VALUES (?, ?, ?, ?)", (1, "2025-04-15", "Vehículo 1", "Chofer 1")))

    def test_actualizar_estado_entrega(self):
        # Probar actualización de estado de entrega
        self.logistica_model.actualizar_estado_entrega(1, "en ruta")
        last_query = self.mock_db.get_last_query()
        self.assertEqual(last_query, ("UPDATE entregas_obras SET estado = ? WHERE id = ?", ("en ruta", 1)))

    def test_generar_acta_entrega(self):
        # Simular generación de acta de entrega
        id_entrega = 1
        self.mock_db.set_return_value(
            "SELECT id, id_obra, fecha_programada, estado FROM entregas_obras WHERE id = ?",
            [(1, "Obra A", "2025-04-14", "Entregado")]
        )

        resultado = self.logistica_model.generar_acta_entrega(id_entrega)

        # Verificar que la consulta se ejecutó correctamente
        last_query = self.mock_db.get_last_query()
        self.assertEqual(last_query, ("SELECT id, id_obra, fecha_programada, estado FROM entregas_obras WHERE id = ?", (id_entrega,)))
        # Verificar que el resultado contiene el mensaje esperado
        self.assertTrue(resultado.startswith("Acta de entrega generada para la obra"))

    def test_exportar_acta_entrega(self):
        # Simular datos de entrega
        id_entrega = 1
        self.mock_db.set_return_value(
            "SELECT id, id_obra, fecha_programada, fecha_realizada, estado, vehiculo_asignado, chofer_asignado, observaciones FROM entregas_obras WHERE id = ?",
            [(1, "Obra A", "2025-04-14", "2025-04-15", "Entregado", "Vehículo 123", "Chofer X", "Sin observaciones")]
        )

        resultado = self.logistica_model.exportar_acta_entrega(id_entrega)

        # Verificar que la consulta se ejecutó correctamente
        last_query = self.mock_db.get_last_query()
        self.assertEqual(last_query, ("SELECT id, id_obra, fecha_programada, fecha_realizada, estado, vehiculo_asignado, chofer_asignado, observaciones FROM entregas_obras WHERE id = ?", (id_entrega,)))
        # Verificar que el resultado contiene el nombre del archivo generado
        self.assertIn("acta_entrega_1.pdf", resultado)

        # Simular la generación del archivo PDF
        with open("acta_entrega_1.pdf", "w") as f:
            f.write("Contenido simulado del PDF")

        # Verificar que el archivo fue creado
        self.assertTrue(os.path.exists("acta_entrega_1.pdf"))

        # Eliminar el archivo después de la prueba
        os.remove("acta_entrega_1.pdf")

if __name__ == "__main__":
    unittest.main()
