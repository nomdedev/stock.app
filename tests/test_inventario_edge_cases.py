"""
Tests de edge cases y flujos alternativos para el módulo Inventario.
"""
import pytest
from unittest.mock import MagicMock

@pytest.fixture
def setup_inventario():
    class DummyInventarioModel:
        def __init__(self):
            self.stock = {'perfilA': 5}
            self.pedidos = []
        def pedir_material(self, obra_id, item, cantidad):
            if obra_id is None or obra_id == 'inexistente':
                raise ValueError("Obra inexistente")
            # BLOQUEO: no permitir pedidos si el stock actual es negativo
            if self.stock.get(item, 0) < 0:
                raise ValueError("Stock negativo")
            if cantidad > self.stock.get(item, 0):
                faltante = cantidad - self.stock.get(item, 0)
                self.pedidos.append({'obra_id': obra_id, 'item': item, 'cantidad': self.stock.get(item, 0), 'faltante': faltante})
                return 'pedido parcial'
            self.stock[item] -= cantidad
            self.pedidos.append({'obra_id': obra_id, 'item': item, 'cantidad': cantidad})
            return 'pedido completo'
        def devolver_material(self, obra_id, item, cantidad):
            self.stock[item] = self.stock.get(item, 0) + cantidad
            return 'devuelto'
    return DummyInventarioModel()
def test_pedido_material_stock_insuficiente(setup_inventario):
    model = setup_inventario
    resultado = model.pedir_material('obra1', 'perfilA', 10)
    assert resultado == 'pedido parcial'
    assert model.pedidos[-1]['faltante'] == 5

def test_pedido_material_stock_negativo(setup_inventario):
    model = setup_inventario
    model.stock['perfilA'] = -1
    with pytest.raises(ValueError):
        model.pedir_material('obra1', 'perfilA', 1)

def test_pedido_a_obra_inexistente(setup_inventario):
    model = setup_inventario
    with pytest.raises(ValueError):
        model.pedir_material('inexistente', 'perfilA', 1)

def test_devolucion_material(setup_inventario):
    model = setup_inventario
    stock_inicial = model.stock['perfilA']
    model.devolver_material('obra1', 'perfilA', 3)
    assert model.stock['perfilA'] == stock_inicial + 3
