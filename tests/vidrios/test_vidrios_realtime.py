import unittest
from PyQt6.QtWidgets import QApplication
from modules.vidrios.view import VidriosView
from core.event_bus import event_bus
import sys

app = QApplication.instance() or QApplication(sys.argv)

class TestIntegracionRealTimeVidrios(unittest.TestCase):
    def setUp(self):
        self.view = VidriosView(usuario_actual="testuser")
        self._feedback = []
        self.view.mostrar_feedback = lambda msg, tipo="info": self._feedback.append((msg, tipo))
        self.view.refrescar_por_obra = lambda datos: self._feedback.append(("refrescado", datos))

    def test_vidrios_actualiza_en_tiempo_real_por_obra(self):
        datos_obra = {"id": 123, "nombre": "Obra Test", "cliente": "Cliente X"}
        event_bus.obra_agregada.emit(datos_obra)
        # Debe haber feedback visual y refresco
        refrescos = [f for f in self._feedback if f[0] == "refrescado"]
        mensajes = [f for f in self._feedback if "Obra Test" in f[0]]
        self.assertTrue(refrescos, "No se refrescó la vista de vidrios en tiempo real")
        self.assertTrue(mensajes, "No se mostró feedback visual tras agregar obra")

if __name__ == "__main__":
    unittest.main()
