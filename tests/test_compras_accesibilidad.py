import pytest
from PyQt6.QtWidgets import QApplication
from modules.compras.view import ComprasView

@pytest.fixture(scope="module")
def app():
    import sys
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app

def test_compras_accesibilidad(app):
    view = ComprasView()
    # Botón nuevo
    assert view.boton_nuevo.toolTip() == "Nuevo pedido"
    assert view.boton_nuevo.accessibleName() == "Botón nuevo pedido de compras"
    # Label feedback
    assert view.label_feedback.accessibleName() == "Feedback visual de Compras"
    assert view.label_feedback.accessibleDescription() == "Mensaje de feedback visual y accesible para el usuario en Compras"
    # Todos los QLabel tienen accessibleDescription
    for widget in view.findChildren(type(view.label_feedback)):
        assert widget.accessibleDescription() != ""
    # Si existe tabla_comparacion, tiene toolTip y accessibleName
    if hasattr(view, 'tabla_comparacion'):
        assert view.tabla_comparacion.toolTip() == "Tabla de comparación de presupuestos"
        assert view.tabla_comparacion.accessibleName() == "Tabla de comparación de presupuestos de compras"
    # Si existe tab_pedidos y tiene tabla_pedidos, verificar accesibilidad básica
    if hasattr(view.tab_pedidos, 'tabla_pedidos'):
        tabla = view.tab_pedidos.tabla_pedidos
        assert tabla.toolTip() != ""
        assert tabla.accessibleName() != ""
