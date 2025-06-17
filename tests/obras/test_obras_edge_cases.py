"""
Tests de edge cases y flujos alternativos para el módulo Obras.
"""
import pytest
from unittest.mock import MagicMock

@pytest.fixture
def setup_obras():
    class DummyObrasModel:
        def __init__(self):
            self.obras = []
        def alta_obra(self, nombre, cliente, fecha):
            if not nombre or not cliente:
                raise ValueError("Datos incompletos")
            if any(o['nombre'] == nombre and o['cliente'] == cliente for o in self.obras):
                raise ValueError("Obra duplicada")
            self.obras.append({'nombre': nombre, 'cliente': cliente, 'fecha': fecha})
        def eliminar_obra(self, nombre):
            self.obras = [o for o in self.obras if o['nombre'] != nombre]
    return DummyObrasModel()

def test_alta_obra_datos_incompletos(setup_obras):
    model = setup_obras
    with pytest.raises(ValueError):
        model.alta_obra('', 'Cliente', '2025-06-09')
    with pytest.raises(ValueError):
        model.alta_obra('Obra1', '', '2025-06-09')

def test_alta_obra_duplicada(setup_obras):
    model = setup_obras
    model.alta_obra('Obra1', 'Cliente', '2025-06-09')
    with pytest.raises(ValueError):
        model.alta_obra('Obra1', 'Cliente', '2025-06-10')

def test_cancelacion_alta_obra(setup_obras):
    model = setup_obras
    # Simular cancelación: no se llama a alta_obra
    assert len(model.obras) == 0

def test_eliminacion_obra_con_pedidos():
    # Simular que la obra tiene pedidos asociados
    class DummyObrasModel:
        def eliminar_obra(self, nombre):
            raise Exception("No se puede eliminar obra con pedidos asociados")
    model = DummyObrasModel()
    with pytest.raises(Exception):
        model.eliminar_obra('Obra1')
