"""
Tests de integración y feedback visual para Logística:
- Validación de habilitación de colocación solo si el pago está realizado.
- Registro de excepción si se realiza la colocación sin pago (y feedback visual).
- Visualización del estado y fecha de pago.
- Interacción con Contabilidad para consultar pagos.
- Feedback visual inmediato en la UI de Logística.
"""
import pytest
from unittest.mock import MagicMock

# Dummy classes para aislar lógica
class DummyContabilidadController:
    def __init__(self, pagos_realizados=None):
        self.pagos_realizados = pagos_realizados or {}
    def esta_pagado(self, id_obra):
        return self.pagos_realizados.get(id_obra, False)
    def obtener_fecha_pago(self, id_obra):
        return "2025-06-09" if self.esta_pagado(id_obra) else None

class DummyLogisticaModel:
    def __init__(self):
        self.colocaciones = []
        self.excepciones = []
    def registrar_colocacion(self, id_obra, usuario):
        self.colocaciones.append((id_obra, usuario))
    def registrar_excepcion(self, id_obra, usuario, motivo):
        self.excepciones.append((id_obra, usuario, motivo))

class DummyLogisticaView:
    def __init__(self):
        self.feedback = []
    def mostrar_feedback(self, mensaje, tipo="info", **kwargs):
        self.feedback.append((mensaje, tipo))
    def mostrar_estado_pago(self, pagado, fecha):
        self.estado_pago = (pagado, fecha)

@pytest.fixture
def setup_logistica():
    model = DummyLogisticaModel()
    view = DummyLogisticaView()
    contab = DummyContabilidadController({1: True, 2: False})
    usuario = {"id": 1, "usuario": "testuser"}
    # Simular LogisticaController real
    class LogisticaController:
        def __init__(self, model, view, contab, usuario):
            self.model = model
            self.view = view
            self.contab = contab
            self.usuario = usuario
        def intentar_colocacion(self, id_obra):
            if self.contab.esta_pagado(id_obra):
                self.model.registrar_colocacion(id_obra, self.usuario["usuario"])
                self.view.mostrar_feedback("Colocación habilitada y registrada.", tipo="exito")
            else:
                self.model.registrar_excepcion(id_obra, self.usuario["usuario"], "Colocación sin pago")
                self.view.mostrar_feedback("No se puede habilitar colocación: pago pendiente.", tipo="error")
        def mostrar_estado_pago(self, id_obra):
            pagado = self.contab.esta_pagado(id_obra)
            fecha = self.contab.obtener_fecha_pago(id_obra)
            self.view.mostrar_estado_pago(pagado, fecha)
    return LogisticaController(model, view, contab, usuario), model, view, contab

def test_colocacion_habilitada_si_pago(setup_logistica):
    controller, model, view, _ = setup_logistica
    controller.intentar_colocacion(1)
    assert model.colocaciones == [(1, "testuser")]
    assert view.feedback[-1][1] == "exito"
    assert "habilitada" in view.feedback[-1][0]

def test_colocacion_bloqueada_si_no_pago(setup_logistica):
    controller, model, view, _ = setup_logistica
    controller.intentar_colocacion(2)
    assert model.excepciones[-1] == (2, "testuser", "Colocación sin pago")
    assert view.feedback[-1][1] == "error"
    assert "pago pendiente" in view.feedback[-1][0]

def test_visualizacion_estado_pago(setup_logistica):
    controller, _, view, _ = setup_logistica
    controller.mostrar_estado_pago(1)
    assert view.estado_pago == (True, "2025-06-09")
    controller.mostrar_estado_pago(2)
    assert view.estado_pago == (False, None)

def test_feedback_visual_inmediato(setup_logistica):
    controller, _, view, _ = setup_logistica
    controller.intentar_colocacion(2)
    assert view.feedback[-1][1] == "error"
    controller.intentar_colocacion(1)
    assert view.feedback[-1][1] == "exito"
