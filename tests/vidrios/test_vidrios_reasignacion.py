import unittest
from PyQt6.QtWidgets import QApplication
from modules.vidrios.view import VidriosView
from modules.vidrios.model import VidriosModel
from core.event_bus import event_bus
import sys

app = QApplication.instance() or QApplication(sys.argv)

class MockDBConnection:
    def __init__(self):
        self.vidrios = []
        self.vidrios_obras = []
        self.last_id = 1
    def ejecutar_query(self, query, params=None):
        if "INSERT INTO vidrios (" in query and params:
            vidrio = (self.last_id,) + tuple(params)
            self.vidrios.append(vidrio)
            self.last_id += 1
            return []
        if "SELECT * FROM vidrios" in query:
            return list(self.vidrios) if self.vidrios else []
        if "INSERT INTO vidrios_obras" in query and params:
            self.vidrios_obras.append(tuple(params))
            return []
        if "DELETE FROM vidrios_obras" in query and params:
            self.vidrios_obras = [v for v in self.vidrios_obras if not (v[0] == params[0] and v[1] == params[1])]
            return []
        return []

class TestReasignacionVidrios(unittest.TestCase):
    def setUp(self):
        self.db = MockDBConnection()
        self.model = VidriosModel(self.db)
        self.view = VidriosView(usuario_actual="testuser")
        self._feedback = []
        self.view.mostrar_feedback = lambda msg, tipo="info": self._feedback.append((msg, tipo))
        self.view.refrescar_por_obra = lambda datos: self._feedback.append(("refrescado", datos))
        event_bus.obra_agregada.connect(self.view.actualizar_por_obra)

    def tearDown(self):
        try:
            event_bus.obra_agregada.disconnect(self.view.actualizar_por_obra)
        except Exception:
            pass

    def test_reasignar_vidrio_entre_obras(self):
        # Agregar vidrio y asignar a obra 1
        datos_vidrio = ("Laminado", 2.5, 1.2, 10, "Proveedor X", "2025-06-01")
        self.model.agregar_vidrio(datos_vidrio)
        vidrios = self.db.ejecutar_query("SELECT * FROM vidrios")
        id_vidrio = vidrios[-1][0]
        self.model.asignar_a_obra(id_vidrio, 101)
        self.assertIn((id_vidrio, 101), self.db.vidrios_obras)
        # Reasignar a obra 202 (eliminar de 101 y asignar a 202)
        self.db.ejecutar_query("DELETE FROM vidrios_obras WHERE id_vidrio=? AND id_obra=?", (id_vidrio, 101))
        self.model.asignar_a_obra(id_vidrio, 202)
        self.assertNotIn((id_vidrio, 101), self.db.vidrios_obras)
        self.assertIn((id_vidrio, 202), self.db.vidrios_obras)
        # Emitir señal de obra agregada para simular refresco
        datos_obra = {"id": 202, "nombre": "Obra Nueva", "cliente": "Cliente Z"}
        event_bus.obra_agregada.emit(datos_obra)
        refrescos = [f for f in self._feedback if f[0] == "refrescado"]
        mensajes = [f for f in self._feedback if "Obra Nueva" in str(f[0])]
        self.assertTrue(refrescos, "No se refrescó la vista de vidrios tras reasignación")
        self.assertTrue(mensajes, "No se mostró feedback visual tras reasignación de vidrio")

if __name__ == "__main__":
    unittest.main()
