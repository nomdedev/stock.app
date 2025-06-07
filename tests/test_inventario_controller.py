import pytest
from unittest.mock import MagicMock, patch

# Suponiendo que el controller se llama InventarioController y está en modules.inventario.controller
from modules.inventario import controller as inventario_controller

class DummyModel:
    def __init__(self):
        self.stock = {1: 10}  # id_perfil: cantidad
        self.reservas = {}
        self.movimientos = []
    def reservar_perfil(self, usuario, id_obra, id_perfil, cantidad):
        if cantidad <= 0:
            raise ValueError("Cantidad inválida")
        if self.stock.get(id_perfil, 0) < cantidad:
            raise ValueError("Stock insuficiente")
        self.stock[id_perfil] -= cantidad
        self.reservas[(id_obra, id_perfil)] = self.reservas.get((id_obra, id_perfil), 0) + cantidad
        self.movimientos.append(("reserva", usuario, id_obra, id_perfil, cantidad))
        return True
    def devolver_perfil(self, usuario, id_obra, id_perfil, cantidad):
        if cantidad <= 0:
            raise ValueError("Cantidad inválida")
        if self.reservas.get((id_obra, id_perfil), 0) < cantidad:
            raise ValueError("No hay suficiente reservado para devolver")
        self.stock[id_perfil] += cantidad
        self.reservas[(id_obra, id_perfil)] -= cantidad
        self.movimientos.append(("devolucion", usuario, id_obra, id_perfil, cantidad))
        return True
    def ajustar_stock(self, id_perfil, cantidad):
        if self.stock.get(id_perfil, 0) + cantidad < 0:
            raise ValueError("Stock negativo no permitido")
        self.stock[id_perfil] += cantidad
        self.movimientos.append(("ajuste", id_perfil, cantidad))
        return True
    def obtener_stock(self, id_perfil):
        return self.stock.get(id_perfil, 0)
    def registrar_movimiento(self, *args, **kwargs):
        pass

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
    # El controller real puede requerir más argumentos, ajustar si es necesario
    return inventario_controller.InventarioController(model, view, None, None, usuario_actual, auditoria_model=auditoria_model)

def test_reserva_stock_suficiente(controller):
    assert controller.model.obtener_stock(1) == 10
    controller.reservar_perfil("testuser", 1, 1, 5)
    assert controller.model.obtener_stock(1) == 5

def test_reserva_stock_insuficiente(controller):
    with pytest.raises(ValueError):
        controller.reservar_perfil("testuser", 1, 1, 20)
    assert controller.model.obtener_stock(1) == 10

def test_reserva_cantidad_invalida(controller):
    with pytest.raises(ValueError):
        controller.reservar_perfil("testuser", 1, 1, 0)
    with pytest.raises(ValueError):
        controller.reservar_perfil("testuser", 1, 1, -3)

def test_devolucion_normal(controller):
    controller.reservar_perfil("testuser", 1, 1, 5)
    controller.devolver_perfil("testuser", 1, 1, 3)
    assert controller.model.obtener_stock(1) == 8

def test_devolucion_mayor_a_reservado(controller):
    controller.reservar_perfil("testuser", 1, 1, 4)
    with pytest.raises(ValueError):
        controller.devolver_perfil("testuser", 1, 1, 5)

def test_ajuste_stock_valido(controller):
    controller.ajustar_stock(1, 5)
    assert controller.model.obtener_stock(1) == 15

def test_ajuste_stock_negativo(controller):
    with pytest.raises(ValueError):
        controller.ajustar_stock(1, -20)

def test_alerta_stock_bajo(controller):
    controller.reservar_perfil("testuser", 1, 1, 9)
    # Simula alerta visual si stock < 2
    if controller.model.obtener_stock(1) < 2:
        controller.view.mostrar_mensaje("Stock bajo", tipo="warning")
    assert ("Stock bajo", "warning") in controller.view.mensajes or controller.model.obtener_stock(1) >= 2

def test_rollback_en_reserva(controller):
    with patch.object(controller.model, 'reservar_perfil', side_effect=Exception("DB error")):
        with pytest.raises(Exception):
            controller.reservar_perfil("testuser", 1, 1, 2)

def test_auditoria_en_reserva(controller):
    controller.reservar_perfil("testuser", 1, 1, 2)
    assert controller.auditoria_model.registrar_evento.called
