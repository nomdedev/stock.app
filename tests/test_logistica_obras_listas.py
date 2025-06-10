"""
Test de integración para Logística: consulta de obras listas para fabricar/entregar y asignación de colocador.
Cubre integración con Inventario, Vidrios, Herrajes y Contabilidad.
"""
import pytest
from unittest.mock import MagicMock

@pytest.fixture
def setup_modelos():
    # Dummies para simular modelos
    class DummyObrasModel:
        def obtener_todas_las_obras(self):
            return [
                {'id': 1, 'nombre': 'Obra 1'},
                {'id': 2, 'nombre': 'Obra 2'},
                {'id': 3, 'nombre': 'Obra 3'}
            ]
    class DummyInventarioModel:
        def obtener_estado_pedidos_por_obra(self, id_obra):
            return 'entregado' if id_obra != 2 else 'pendiente'
    class DummyVidriosModel:
        def obtener_estado_pedidos_por_obra(self, id_obra):
            return 'entregado'
    class DummyHerrajesModel:
        def obtener_estado_pedido_por_obra(self, id_obra):
            return 'entregado'
    class DummyContabilidadModel:
        def obtener_estado_pago_pedido_por_obra(self, id_obra, modulo):
            if id_obra == 1:
                return 'pagado'
            return 'pendiente'
    return DummyObrasModel(), DummyInventarioModel(), DummyVidriosModel(), DummyHerrajesModel(), DummyContabilidadModel()

def test_obras_listas_para_entrega(setup_modelos):
    from modules.logistica.model import LogisticaModel
    model = LogisticaModel()  # No pasar db_connection
    obras_model, inventario_model, vidrios_model, herrajes_model, contabilidad_model = setup_modelos
    obras_listas = model.obtener_obras_listas_para_entrega(
        obras_model, inventario_model, vidrios_model, herrajes_model, contabilidad_model
    )
    # Solo la obra 1 cumple todos los requisitos
    assert len(obras_listas) == 1
    assert obras_listas[0]['id'] == 1

def test_obras_no_listas_si_falta_pago_o_estado(setup_modelos):
    from modules.logistica.model import LogisticaModel
    model = LogisticaModel()  # No pasar db_connection
    obras_model, inventario_model, vidrios_model, herrajes_model, contabilidad_model = setup_modelos
    # Cambiar estado de inventario para obra 3
    inventario_model.obtener_estado_pedidos_por_obra = lambda id_obra: 'pendiente' if id_obra == 3 else 'entregado'
    obras_listas = model.obtener_obras_listas_para_entrega(
        obras_model, inventario_model, vidrios_model, herrajes_model, contabilidad_model
    )
    # Solo la obra 1 sigue cumpliendo
    assert len(obras_listas) == 1
    assert obras_listas[0]['id'] == 1
