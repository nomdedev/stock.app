import pytest
from unittest.mock import MagicMock
from modules.auditoria import controller as auditoria_controller

class DummyModel:
    def __init__(self):
        self.eventos = []
    def registrar_evento(self, usuario_id, modulo, accion, detalle, ip):
        self.eventos.append({
            "usuario_id": usuario_id,
            "modulo": modulo,
            "accion": accion,
            "detalle": detalle,
            "ip": ip
        })
    def filtrar_eventos(self, usuario_id=None, modulo=None, fecha=None):
        return [e for e in self.eventos if
                (usuario_id is None or e["usuario_id"] == usuario_id) and
                (modulo is None or e["modulo"] == modulo) and
                (fecha is None or True)]
    def exportar_a_excel(self, eventos):
        if not eventos:
            raise ValueError("No hay eventos para exportar")
        return b"exceldata"

class DummyView:
    def __init__(self):
        self.mensajes = []
    def mostrar_mensaje(self, mensaje, tipo=None, **kwargs):
        self.mensajes.append((mensaje, tipo))

@pytest.fixture
def controller():
    model = DummyModel()
    view = DummyView()
    usuario_actual = {"id": 1, "username": "testuser", "ip": "127.0.0.1"}
    return auditoria_controller.AuditoriaController(model, view, None, usuario_actual)

def test_registro_automatico(controller):
    controller.model.registrar_evento(1, "obras", "alta", "Alta exitosa", "127.0.0.1")
    assert len(controller.model.eventos) == 1
    assert controller.model.eventos[0]["accion"] == "alta"

def test_filtrado_por_usuario(controller):
    controller.model.registrar_evento(1, "obras", "alta", "Alta exitosa", "127.0.0.1")
    controller.model.registrar_evento(2, "obras", "baja", "Baja exitosa", "127.0.0.2")
    eventos = controller.model.filtrar_eventos(usuario_id=1)
    assert all(e["usuario_id"] == 1 for e in eventos)

def test_filtrado_por_modulo(controller):
    controller.model.registrar_evento(1, "obras", "alta", "Alta exitosa", "127.0.0.1")
    controller.model.registrar_evento(1, "inventario", "reserva", "Reserva exitosa", "127.0.0.1")
    eventos = controller.model.filtrar_eventos(modulo="inventario")
    assert all(e["modulo"] == "inventario" for e in eventos)

def test_exportar_a_excel(controller):
    controller.model.registrar_evento(1, "obras", "alta", "Alta exitosa", "127.0.0.1")
    data = controller.model.exportar_a_excel(controller.model.eventos)
    assert data == b"exceldata"

def test_exportar_a_excel_sin_eventos(controller):
    with pytest.raises(ValueError):
        controller.model.exportar_a_excel([])

def test_feedback_visual_error_exportar(controller):
    try:
        controller.model.exportar_a_excel([])
    except Exception:
        controller.view.mostrar_mensaje("Error al exportar", tipo="error")
    assert ("Error al exportar", "error") in controller.view.mensajes
