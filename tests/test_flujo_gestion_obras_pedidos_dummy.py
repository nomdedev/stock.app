"""
Test de integración aislado: flujo completo de gestión de obras y pedidos usando dummies,
sin dependencias de base de datos ni configuración real.
"""
import pytest

class DummyObra:
    def __init__(self, nombre, cliente):
        self.nombre = nombre
        self.cliente = cliente
        self.id = f"obra_{nombre}"

class DummyInventario:
    def __init__(self): self.stock = {'perfilA': 10, 'vidrioA': 5, 'herrajeA': 5}
    def pedir_material(self, obra_id, item, cantidad):
        if self.stock.get(item, 0) < cantidad:
            return 'pedido parcial'
        self.stock[item] -= cantidad
        return 'pedido completo'
class DummyVidrios:
    def reservar_vidrio(self, obra_id, tipo, cantidad):
        if cantidad > 5: raise ValueError('Stock insuficiente vidrio')
        return True
class DummyHerrajes:
    def reservar_herraje(self, obra_id, tipo, cantidad):
        if cantidad > 5: raise ValueError('Stock insuficiente herraje')
        return True
class DummyContabilidad:
    def registrar_pago(self, obra_id, monto):
        if monto <= 0: raise ValueError('Monto inválido')
        return True
class DummyLogistica:
    def generar_envio(self, obra_id, datos_envio):
        if not datos_envio.get('direccion'): raise ValueError('Datos incompletos')
        return True

@pytest.mark.integration
def test_flujo_completo_gestion_obras_y_pedidos_dummy():
    """
    Test de integración aislado: flujo completo de gestión de obras y pedidos para 3 obras,
    cubriendo materiales, vidrios, herrajes, pagos y logística, con feedback y edge cases.
    """
    # 1. Crear 3 obras dummy
    obras = [DummyObra(f"ObraFlow{i+1}", f"Cliente{i+1}") for i in range(3)]
    inventario = DummyInventario()
    vidrios = DummyVidrios()
    herrajes = DummyHerrajes()
    contabilidad = DummyContabilidad()
    logistica = DummyLogistica()
    for idx, obra in enumerate(obras):
        # 2. Solicitud de materiales
        res_mat = inventario.pedir_material(obra.id, 'perfilA', 3)
        assert res_mat in ('pedido completo', 'pedido parcial')
        # 3. Asociación de pedido a obra (dummy)
        pedido = {'obra_id': obra.id, 'items': [{'item': 'perfilA', 'cantidad': 3}]}
        # 4. Reflejo en vidrios y herrajes
        assert vidrios.reservar_vidrio(obra.id, 'vidrioA', 1)
        assert herrajes.reservar_herraje(obra.id, 'herrajeA', 1)
        # 5. Registro de pago
        assert contabilidad.registrar_pago(obra.id, 1000)
        # 6. Generación de envío/logística
        assert logistica.generar_envio(obra.id, {'direccion': f'Calle {idx+1}'})
        # 7. Edge case: stock insuficiente
        inventario.stock['perfilA'] = 0
        res_mat2 = inventario.pedir_material(obra.id, 'perfilA', 2)
        assert res_mat2 == 'pedido parcial'
        # 8. Edge case: vidrio/herraje insuficiente
        with pytest.raises(ValueError):
            vidrios.reservar_vidrio(obra.id, 'vidrioA', 10)
        with pytest.raises(ValueError):
            herrajes.reservar_herraje(obra.id, 'herrajeA', 10)
        # 9. Edge case: pago inválido
        with pytest.raises(ValueError):
            contabilidad.registrar_pago(obra.id, 0)
        # 10. Edge case: datos logísticos incompletos
        with pytest.raises(ValueError):
            logistica.generar_envio(obra.id, {'direccion': ''})
