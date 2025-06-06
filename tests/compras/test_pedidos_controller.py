import pytest
from modules.pedidos.model import PedidosModel
from modules.pedidos.controller import PedidosController

class DummyUsuarios:
    def __init__(self, permisos):
        self.permisos = permisos
    def tiene_permiso(self, usuario, modulo, accion):
        return self.permisos.get((modulo, accion), False)

class DummyAuditoria:
    def registrar_evento(self, *a, **k): pass

@pytest.fixture
def model():
    class DummyDB:
        def __init__(self):
            self.pedidos = []
            self.pedidos_por_obra = []
            self.movimientos_stock = []
            self.auditorias = []
            self.estado = {}
        def ejecutar_query(self, q, p=()):
            if q.startswith("INSERT INTO pedidos "):
                id_pedido = len(self.pedidos) + 1
                self.pedidos.append({'id_pedido': id_pedido, 'id_obra': p[0], 'estado': p[2], 'total': p[3]})
                return [(id_pedido,)]
            if q.startswith("SELECT last_insert_rowid") or q.startswith("SELECT SCOPE_IDENTITY"):
                return [(len(self.pedidos),)]
            if q.startswith("INSERT INTO pedidos_por_obra"):
                self.pedidos_por_obra.append({'id_pedido': p[0], 'id_item': p[2], 'tipo': p[3], 'cantidad': p[4]})
            if q.startswith("INSERT INTO auditorias_sistema"):
                self.auditorias.append({'usuario': p[0], 'accion': p[2]})
            if q.startswith("UPDATE pedidos SET estado='Recibido'"):
                for ped in self.pedidos:
                    if ped['id_pedido'] == p[0]:
                        ped['estado'] = 'Recibido'
            return []
        def transaction(self, timeout=30, retries=2):
            class Tx:
                def __enter__(self_): return self
                def __exit__(self_, exc_type, exc_val, exc_tb): pass
            return Tx()
    return PedidosModel(DummyDB())

@pytest.fixture
def controller(model):
    usuario = {'id': 1, 'username': 'admin'}
    usuarios_model = DummyUsuarios({('Pedidos', 'crear'): True, ('Pedidos', 'editar'): True})
    auditoria_model = DummyAuditoria()
    return PedidosController(model, None, None, usuarios_model, usuario, auditoria_model)

def test_crear_pedido_con_permisos(controller, model):
    id_pedido = controller.crear_pedido(obra_id=1)
    assert id_pedido > 0
    assert any(a['accion'].startswith('Generó pedido') for a in model.db.auditorias)

def test_crear_pedido_sin_permisos(model):
    usuario = {'id': 2, 'username': 'operario'}
    usuarios_model = DummyUsuarios({('Pedidos', 'crear'): False})
    auditoria_model = DummyAuditoria()
    controller = PedidosController(model, None, None, usuarios_model, usuario, auditoria_model)
    with pytest.raises(ValueError):
        controller.crear_pedido(obra_id=1)

def test_recibir_pedido_con_permisos(controller, model):
    # Simula pedido pendiente
    model.db.pedidos.append({'id_pedido': 1, 'id_obra': 1, 'estado': 'Pendiente', 'total': 100})
    model.db.pedidos_por_obra.append({'id_pedido': 1, 'id_item': 1, 'tipo': 'perfil', 'cantidad': 5})
    ok = controller.recibir_pedido(1)
    assert ok is True
    assert any(a['accion'].startswith('Recibió pedido') for a in model.db.auditorias)

def test_recibir_pedido_sin_permisos(model):
    usuario = {'id': 2, 'username': 'operario'}
    usuarios_model = DummyUsuarios({('Pedidos', 'editar'): False})
    auditoria_model = DummyAuditoria()
    controller = PedidosController(model, None, None, usuarios_model, usuario, auditoria_model)
    with pytest.raises(ValueError):
        controller.recibir_pedido(1)
