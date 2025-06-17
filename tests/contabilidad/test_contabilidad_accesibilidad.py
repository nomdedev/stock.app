import pytest
from PyQt6.QtWidgets import QApplication
from modules.contabilidad.view import ContabilidadView

@pytest.fixture(scope="module")
def app():
    import sys
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app

def test_contabilidad_accesibilidad(app):
    view = ContabilidadView()
    # Botón agregar
    assert view.boton_agregar.toolTip() == "Agregar registro"
    assert view.boton_agregar.accessibleName() == "Botón agregar registro de contabilidad"
    # Label feedback
    assert view.label_feedback.accessibleName() == "Feedback visual de Contabilidad"
    assert view.label_feedback.accessibleDescription() == "Mensaje de feedback visual y accesible para el usuario en Contabilidad"
    # Título
    assert view.label_titulo.accessibleDescription() == "Título principal de la vista de Contabilidad"
    # Botones de acción
    assert view.boton_agregar_balance.accessibleName() == "Botón agregar movimiento contable"
    assert view.boton_agregar_recibo.accessibleName() == "Botón agregar recibo de contabilidad"
    assert view.boton_actualizar_grafico.accessibleName() == "Botón actualizar gráfico de estadísticas"
    assert view.boton_estadistica_personalizada.accessibleName() == "Botón estadística personalizada de contabilidad"
    # Tablas principales
    assert view.tabla_balance.toolTip() == "Tabla de balance contable"
    assert view.tabla_balance.accessibleName() == "Tabla de balance contable"
    assert view.tabla_pagos.toolTip() == "Tabla de pagos contables"
    assert view.tabla_pagos.accessibleName() == "Tabla de pagos contables"
    assert view.tabla_recibos.toolTip() == "Tabla de recibos contables"
    assert view.tabla_recibos.accessibleName() == "Tabla de recibos contables"
    # Todos los QLabel tienen accessibleDescription
    for widget in view.findChildren(type(view.label_feedback)):
        assert widget.accessibleDescription() != ""
