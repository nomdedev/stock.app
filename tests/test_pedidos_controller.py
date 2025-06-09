import pytest
from unittest.mock import MagicMock, patch
from modules.pedidos import controller as pedidos_controller

class DummyModel:
    def __init__(self):
        self.pedidos = []
        self.faltantes = {1: 5}  # id_material: cantidad
        self.estado = {}
    def generar_pedido(self, id_obra):
        if not self.faltantes:
            raise ValueError("No hay faltantes")
        if any(p["id_obra"] == id_obra and p["estado"] == "pendiente" for p in self.pedidos):
            raise ValueError("Ya existe un pedido pendiente")
        pedido = {"id": len(self.pedidos)+1, "id_obra": id_obra, "estado": "pendiente"}
        self.pedidos.append(pedido)
        return pedido["id"]
    def recibir_pedido(self, id_pedido):
        for p in self.pedidos:
            if p["id"] == id_pedido:
                if p["estado"] != "pendiente":
                    raise ValueError("Estado inválido")
                p["estado"] = "recibido"
                return True
        raise ValueError("Pedido no encontrado")
    def obtener_pedido(self, id_pedido):
        for p in self.pedidos:
            if p["id"] == id_pedido:
                return p
        return None

class DummyView:
    def __init__(self):
        self.mensajes = []
    def mostrar_mensaje(self, mensaje, tipo=None, **kwargs):
        self.mensajes.append((mensaje, tipo))

@pytest.fixture
def controller():
    model = DummyModel()
    view = DummyView()
    auditoria_model = MagicMock()
    usuario_actual = {"id": 1, "username": "testuser", "ip": "127.0.0.1"}
    return pedidos_controller.PedidosController(model, view, None, None, usuario_actual, auditoria_model=auditoria_model)

def test_generar_pedido_con_faltantes(controller):
    id_pedido = controller.generar_pedido(1)
    assert id_pedido == 1
    assert controller.model.pedidos[0]["estado"] == "pendiente"

def test_generar_pedido_sin_faltantes(controller):
    controller.model.faltantes = {}
    with pytest.raises(ValueError):
        controller.generar_pedido(2)

def test_generar_pedido_existente(controller):
    controller.generar_pedido(1)
    with pytest.raises(ValueError):
        controller.generar_pedido(1)

def test_recibir_pedido_correcto(controller):
    id_pedido = controller.generar_pedido(1)
    controller.recibir_pedido(id_pedido)
    assert controller.model.pedidos[0]["estado"] == "recibido"

def test_recibir_pedido_repetido(controller):
    id_pedido = controller.generar_pedido(1)
    controller.recibir_pedido(id_pedido)
    with pytest.raises(ValueError):
        controller.recibir_pedido(id_pedido)

def test_recibir_pedido_estado_invalido(controller):
    id_pedido = controller.generar_pedido(1)
    controller.model.pedidos[0]["estado"] = "cancelado"
    with pytest.raises(ValueError):
        controller.recibir_pedido(id_pedido)

def test_rollback_en_recepcion(controller):
    id_pedido = controller.generar_pedido(1)
    with patch.object(controller.model, 'recibir_pedido', side_effect=Exception("DB error")):
        with pytest.raises(Exception):
            controller.recibir_pedido(id_pedido)

def test_auditoria_en_generar_pedido(controller):
    controller.generar_pedido(1)
    assert controller.auditoria_model.registrar_evento.called

def test_auditoria_en_recepcion(controller):
    id_pedido = controller.generar_pedido(1)
    controller.recibir_pedido(id_pedido)
    assert controller.auditoria_model.registrar_evento.called
