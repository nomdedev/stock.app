import unittest
from unittest.mock import Mock
from modules.logistica.model import LogisticaModel

class MockDBConnection:
    def __init__(self):
        self.entregas_obras = []
        self.checklist_entrega = []
        self.last_id = 1
        self.query_log = []
    def ejecutar_query(self, query, params=None):
        self.query_log.append((query, params))
        if "INSERT INTO entregas_obras" in query:
            # Aceptar cualquier variante de inserción y mapear a la estructura estándar
            # Estructura: id, id_obra, fecha_programada, fecha_realizada, estado, vehiculo_asignado, chofer_asignado, observaciones
            valores = list(params) if params else []
            # Rellenar hasta 9 campos
            while len(valores) < 9:
                valores.append(None)
            id_obra = valores[0]
            fecha_programada = valores[1]
            fecha_realizada = valores[2]
            estado = valores[3] if valores[3] is not None else "pendiente"
            vehiculo_asignado = valores[4]
            chofer_asignado = valores[5]
            observaciones = valores[8] if valores[8] is not None else "Sin observaciones"
            # Asignar id_entrega igual a id_obra si es un entero positivo, si no usar last_id
            try:
                id_entrega = int(id_obra)
                if id_entrega > 0:
                    pass
                else:
                    id_entrega = self.last_id
            except Exception:
                id_entrega = self.last_id
            entrega = (
                int(id_entrega), id_obra, fecha_programada, fecha_realizada, estado, vehiculo_asignado, chofer_asignado, observaciones
            )
            print(f"[MOCK] INSERT entrega: id_entrega={id_entrega}, id_obra={id_obra}, entrega={entrega}")
            self.entregas_obras.append(entrega)
            self.last_id += 1
            return None
        if "SELECT id, id_obra, fecha_programada, fecha_realizada, estado, vehiculo_asignado, chofer_asignado, observaciones FROM entregas_obras WHERE id = ?" in query:
            if params is None:
                return []
            id_entrega = int(params[0])
            print(f"[MOCK] SELECT EXPORT busca id_entrega={id_entrega}, entregas={self.entregas_obras}")
            for e in self.entregas_obras:
                print(f"[MOCK] Comparando e[0]={e[0]} con id_entrega={id_entrega}")
                if int(e[0]) == id_entrega:
                    print(f"[MOCK] EXPORT found: {e}")
                    return [e]
            print("[MOCK] EXPORT not found")
            return []
        if "SELECT id, id_obra, fecha_programada, estado FROM entregas_obras WHERE id = ?" in query:
            if params is None:
                return []
            id_entrega = int(params[0])
            print(f"[MOCK] SELECT ACTA busca id_entrega={id_entrega}, entregas={self.entregas_obras}")
            for e in self.entregas_obras:
                print(f"[MOCK] Comparando e[0]={e[0]} con id_entrega={id_entrega}")
                if int(e[0]) == id_entrega:
                    return [(e[0], e[1], e[2], e[4])]
            print("[MOCK] ACTA not found")
            return []
        if "SELECT * FROM checklist_entrega WHERE id_entrega = ?" in query:
            return [ ("Item 1", "OK", "Ninguna"), ("Item 2", "OK", "Ninguna") ]
        if "SELECT * FROM entregas_obras" in query:
            return list(self.entregas_obras)
        if "UPDATE entregas_obras SET estado = ? WHERE id = ?" in query:
            if params is None:
                return None
            for i, e in enumerate(self.entregas_obras):
                if int(e[0]) == int(params[1]):
                    self.entregas_obras[i] = e[:4] + (params[0],) + e[5:]
            return None
        return []

class MockLogisticaView:
    def __init__(self):
        self.tabla_data = []
    def actualizar_tabla(self, data):
        self.tabla_data = data

class TestLogisticaIntegracion(unittest.TestCase):
    def setUp(self):
        self.mock_db = MockDBConnection()
        self.model = LogisticaModel(self.mock_db)
        self.view = MockLogisticaView()
    def tearDown(self):
        self.mock_db.entregas_obras.clear()
        # No reiniciar last_id para mantener ids únicos
    def test_programar_y_reflejar_entrega(self):
        # 1. Programar entrega
        self.model.programar_entrega(1, "2025-05-20", "Vehículo 1", "Chofer 1", None, None)
        entregas = self.mock_db.ejecutar_query("SELECT * FROM entregas_obras") or []
        self.assertTrue(any(e[1] == 1 for e in entregas))
        # 2. Simular actualización de tabla en la vista
        self.view.actualizar_tabla(entregas)
        self.assertEqual(self.view.tabla_data, entregas)
    def test_actualizar_estado_entrega(self):
        # 1. Programar entrega
        self.model.programar_entrega(2, "2025-05-21", "Vehículo 2", "Chofer 2", None, None)
        entregas = self.mock_db.ejecutar_query("SELECT * FROM entregas_obras") or []
        if not entregas:
            self.fail("No se encontró la entrega recién creada")
        id_entrega = entregas[0][0]
        # 2. Actualizar estado
        self.model.actualizar_estado_entrega(id_entrega, "en ruta")
        entregas = self.mock_db.ejecutar_query("SELECT * FROM entregas_obras") or []
        self.assertTrue(any(len(e) > 4 and e[4] == "en ruta" for e in entregas))
        # 3. Simular actualización de tabla en la vista
        self.view.actualizar_tabla(entregas)
        self.assertEqual(self.view.tabla_data, entregas)
    def test_generar_y_exportar_acta(self):
        # 1. Programar entrega
        self.model.programar_entrega(3, "2025-05-13", "Vehículo 3", "Chofer 3", None, None)
        entregas = self.mock_db.ejecutar_query("SELECT * FROM entregas_obras") or []
        if not entregas:
            self.fail("No se encontró la entrega recién creada")
        id_entrega = entregas[-1][0]
        # 2. Generar acta
        resultado = self.model.generar_acta_entrega(id_entrega)
        self.assertIn("Acta de entrega generada", resultado)
        # 3. Exportar acta
        resultado_export = self.model.exportar_acta_entrega(id_entrega)
        print(f"DEBUG id_entrega: {id_entrega}, resultado_export: {resultado_export}")
        self.assertIn(f"acta_entrega_{id_entrega}.pdf", resultado_export)

if __name__ == "__main__":
    unittest.main()
