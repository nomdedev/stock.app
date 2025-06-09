import unittest
from PyQt6.QtWidgets import QApplication
from modules.obras.controller import ObrasController
from modules.obras.model import ObrasModel
from modules.vidrios.view import VidriosView
from core.event_bus import event_bus
from unittest.mock import Mock
import sys

app = QApplication.instance() or QApplication(sys.argv)

class MockDBConnection:
    def __init__(self):
        self.obras = []
        self.last_id = 1
    def ejecutar_query(self, query, params=None):
        if "INSERT INTO obras" in query and params:
            obra = (self.last_id,) + tuple(params)
            self.obras.append(obra)
            self.last_id += 1
            return []
        if "SELECT * FROM obras" in query:
            return list(self.obras)
        if "UPDATE obras SET estado" in query and params:
            # Simula cambio de estado
            for idx, o in enumerate(self.obras):
                if o[0] == params[1]:
                    self.obras[idx] = o[:3] + (params[0],) + o[4:]
            return []
        return []

class TestCierreObraIntegration(unittest.TestCase):
    def setUp(self):
        self.db = MockDBConnection()
        self.model = ObrasModel(self.db)
        self.view = Mock()
        self.usuarios_model = Mock()
        self.usuarios_model.tiene_permiso.return_value = True
        self.controller = ObrasController(self.model, self.view, self.db, self.usuarios_model, usuario_actual={"id": 1, "ip": "127.0.0.1"})
        self.vidrios_view = VidriosView(usuario_actual="testuser")
        self._feedback = []
        self.vidrios_view.mostrar_feedback = lambda msg, tipo="info": self._feedback.append((msg, tipo))
        self.vidrios_view.refrescar_por_obra = lambda datos: self._feedback.append(("refrescado", datos))
        event_bus.obra_agregada.connect(self.vidrios_view.actualizar_por_obra)

    def tearDown(self):
        try:
            event_bus.obra_agregada.disconnect(self.vidrios_view.actualizar_por_obra)
        except Exception:
            pass

    def test_cierre_obra_actualiza_vidrios(self):
        # Agregar obra
        datos_obra = ("Obra Cierre", "Cliente Final", "Medición", "2025-06-05", "2025-07-01")
        self.model.agregar_obra(datos_obra)
        obras = self.db.ejecutar_query("SELECT * FROM obras")
        id_obra = obras[-1][0]
        # Cambiar estado a 'finalizada'
        self.controller.cambiar_estado_obra(id_obra, "finalizada")
        # Emitir señal para simular integración cruzada
        event_bus.obra_agregada.emit({"id": id_obra, "nombre": "Obra Cierre", "cliente": "Cliente Final", "estado": "finalizada"})
        refrescos = [f for f in self._feedback if f[0] == "refrescado"]
        mensajes = [f for f in self._feedback if f and ("Obra Cierre" in str(f[0]) or "finalizada" in str(f[0]))]
        self.assertTrue(refrescos, "No se refrescó la vista de vidrios tras cierre de obra")
        self.assertTrue(mensajes, f"No se mostró feedback visual tras cierre de obra. Feedback: {self._feedback}")

if __name__ == "__main__":
    unittest.main()
