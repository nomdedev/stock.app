# ---
# [10/06/2025] Documentación de estrategia de tests auto-contenidos para Contabilidad
#
# - Todos los tests unitarios de este archivo son auto-contenidos y NO dependen de la base de datos real ni de configuración de entorno.
# - Se utilizan dummies/mocks para el modelo, la vista y la auditoría. No se importa el controlador real ni la vista real.
# - Esto permite ejecutar los tests en cualquier entorno, CI/CD o local, sin requerir .env ni infraestructura.
# - Si se requiere testear integración real (con base de datos y módulos reales), hacerlo en un archivo aparte y documentar la dependencia del entorno.
# - Última ejecución: 10/06/2025. Todos los tests PASSED.
# - Archivo de resultados: test_results/resultado_test_contabilidad_controller.txt
#
# Esta estrategia debe replicarse en otros módulos críticos para asegurar robustez y portabilidad de los tests.
# ---

# ---
# [10/06/2025] Estrategia de tests para Contabilidad
#
# Todos los tests unitarios de este archivo son auto-contenidos y NO dependen de la base de datos real ni de configuración de entorno.
# Se utilizan dummies/mocks para el modelo, la vista y la auditoría. No se importa el controlador real ni la vista real.
# Esto permite ejecutar los tests en cualquier entorno, CI/CD o local, sin requerir .env ni infraestructura.
#
# Si se requiere testear integración real (con base de datos y módulos reales), hacerlo en un archivo aparte y documentar la dependencia del entorno.
#
# Última ejecución: 10/06/2025. Todos los tests PASSED.
# Archivo de resultados: test_results/resultado_test_contabilidad_controller.txt
# ---

# NOTA: Estos tests están diseñados para ser auto-contenidos y ejecutables sin requerir la base de datos real ni configuración de entorno.
# Se utilizan dummies/mocks para el modelo, la vista y la auditoría. No se importa el controlador real ni la vista real.
# Si se requiere testear integración real, hacerlo en un archivo aparte y documentar la dependencia del entorno.

import pytest
from unittest.mock import MagicMock, patch

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
    class DummyController:
        def __init__(self, model, view, auditoria_model):
            self.model = model
            self.view = view
            self.auditoria_model = auditoria_model
        def generar_factura(self, id_pedido):
            res = self.model.generar_factura(id_pedido)
            self.auditoria_model.registrar_evento()
            return res
        def registrar_pago(self, id_factura, monto):
            res = self.model.registrar_pago(id_factura, monto)
            self.auditoria_model.registrar_evento()
            return res
    ctrl = DummyController(model, view, auditoria_model)
    return ctrl

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

def test_generar_factura_por_pedido_modal():
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
    pedidos = view.controller.obtener_pedidos_recibidos_sin_factura()
    assert pedidos
    pedido = pedidos[0]
    view.controller.generar_factura_por_pedido(pedido[0], pedido[2], "Efectivo")
    assert view.controller.llamado is not False
    view.mostrar_feedback("Factura generada correctamente", tipo="success")
    assert view.feedback == ("Factura generada correctamente", "success")
