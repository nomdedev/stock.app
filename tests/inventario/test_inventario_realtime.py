import unittest
from PyQt6.QtWidgets import QApplication
from modules.inventario.view import InventarioView
from core.event_bus import event_bus
import sys

app = QApplication.instance() or QApplication(sys.argv)

class TestIntegracionRealTimeInventario(unittest.TestCase):
    def setUp(self):
        self.view = InventarioView(usuario_actual="testuser")
        self._feedback = []
        # Mock feedback visual
        self.view.mostrar_feedback_visual = lambda msg, tipo="info": self._feedback.append((msg, tipo))
        # Mock refresco
        self.view.refrescar_stock_por_obra = lambda datos: self._feedback.append(("refrescado", datos))
        # Conectar la señal manualmente (en la app real esto es automático)
        event_bus.obra_agregada.connect(self.view.actualizar_por_obra)

    def tearDown(self):
        try:
            event_bus.obra_agregada.disconnect(self.view.actualizar_por_obra)
        except Exception:
            pass

    def test_inventario_actualiza_en_tiempo_real_por_obra(self):
        datos_obra = {"id": 456, "nombre": "Obra Inventario Test", "cliente": "Cliente Y"}
        event_bus.obra_agregada.emit(datos_obra)
        refrescos = [f for f in self._feedback if f and f[0] == "refrescado"]
        mensajes = [f for f in self._feedback if f and "Obra Inventario Test" in str(f[0])]
        self.assertTrue(refrescos, "No se refrescó la vista de inventario en tiempo real")
        self.assertTrue(mensajes, f"No se mostró feedback visual tras agregar obra. Feedback: {self._feedback}")

if __name__ == "__main__":
    unittest.main()
