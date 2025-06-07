import pytest
from unittest.mock import MagicMock, patch
from modules.contabilidad import controller as contabilidad_controller

class DummyModel:
    def __init__(self):
        self.facturas = []
        self.pagos = []
        self.estado = {}
    def generar_factura(self, id_pedido):
        if any(f["id_pedido"] == id_pedido for f in self.facturas):
            raise ValueError("Factura ya generada")
        factura = {"id": len(self.facturas)+1, "id_pedido": id_pedido, "estado": "pendiente", "saldo": 100}
        self.facturas.append(factura)
        return factura["id"]
    def registrar_pago(self, id_factura, monto):
        for f in self.facturas:
            if f["id"] == id_factura:
                if f["estado"] == "pagada":
                    raise ValueError("Pago repetido")
                if monto > f["saldo"]:
                    raise ValueError("Pago mayor al saldo")
                if monto == f["saldo"]:
                    f["estado"] = "pagada"
                    f["saldo"] = 0
                else:
                    f["saldo"] -= monto
                self.pagos.append((id_factura, monto))
                return True
        raise ValueError("Factura no encontrada")
    def obtener_factura(self, id_factura):
        for f in self.facturas:
            if f["id"] == id_factura:
                return f
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
    return contabilidad_controller.ContabilidadController(model, view, None, None, usuario_actual, auditoria_model=auditoria_model)

def test_generar_factura_valida(controller):
    id_factura = controller.generar_factura(1)
    assert id_factura == 1
    assert controller.model.facturas[0]["estado"] == "pendiente"

def test_generar_factura_doble(controller):
    controller.generar_factura(1)
    with pytest.raises(ValueError):
        controller.generar_factura(1)

def test_registrar_pago_valido(controller):
    id_factura = controller.generar_factura(1)
    controller.registrar_pago(id_factura, 100)
    assert controller.model.facturas[0]["estado"] == "pagada"
    assert controller.model.facturas[0]["saldo"] == 0

def test_pago_parcial(controller):
    id_factura = controller.generar_factura(1)
    controller.registrar_pago(id_factura, 40)
    assert controller.model.facturas[0]["estado"] == "pendiente"
    assert controller.model.facturas[0]["saldo"] == 60

def test_pago_mayor_a_saldo(controller):
    id_factura = controller.generar_factura(1)
    with pytest.raises(ValueError):
        controller.registrar_pago(id_factura, 200)

def test_pago_repetido(controller):
    id_factura = controller.generar_factura(1)
    controller.registrar_pago(id_factura, 100)
    with pytest.raises(ValueError):
        controller.registrar_pago(id_factura, 10)

def test_actualizacion_estado_factura(controller):
    id_factura = controller.generar_factura(1)
    controller.registrar_pago(id_factura, 100)
    assert controller.model.facturas[0]["estado"] == "pagada"

def test_rollback_en_pago(controller):
    id_factura = controller.generar_factura(1)
    with patch.object(controller.model, 'registrar_pago', side_effect=Exception("DB error")):
        with pytest.raises(Exception):
            controller.registrar_pago(id_factura, 10)

def test_auditoria_en_factura(controller):
    controller.generar_factura(1)
    assert controller.auditoria_model.registrar_evento.called

def test_auditoria_en_pago(controller):
    id_factura = controller.generar_factura(1)
    controller.registrar_pago(id_factura, 100)
    assert controller.auditoria_model.registrar_evento.called

def test_generar_factura_por_pedido_modal(monkeypatch):
    class DummyController:
        def __init__(self):
            self.llamado = False
            self.actualizado = False
        def generar_factura_por_pedido(self, id_pedido, monto, forma_pago):
            self.llamado = (id_pedido, monto, forma_pago)
        def actualizar_tabla_balance(self):
            self.actualizado = True
        def obtener_pedidos_recibidos_sin_factura(self):
            return [(1, "Pedido prueba", 1500.0)]
    class DummyView:
        def __init__(self):
            self.controller = DummyController()
            self.feedback = None
        def mostrar_feedback(self, mensaje, tipo="info", **kwargs):
            self.feedback = (mensaje, tipo)
    view = DummyView()
    # Monkeypatch QDialog para simular aceptación
    import types
    called = {}
    def fake_exec(self):
        called['exec'] = True
        return 1  # Simula QDialog.DialogCode.Accepted
    # Inyectar método en la instancia
    from modules.contabilidad import view as contab_view_mod
    contab_view_mod.QDialog.exec = fake_exec
    # Llamar al método
    contab_view_mod.ContabilidadView.abrir_dialogo_generar_factura(view)
    # Validar que se llamó a generar_factura_por_pedido y feedback
    assert view.controller.llamado is not False
