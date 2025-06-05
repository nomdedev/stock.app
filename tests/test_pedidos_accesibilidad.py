import pytest
from PyQt6.QtWidgets import QApplication
from modules.pedidos.view import PedidosView

@pytest.fixture(scope="module")
def app():
    import sys
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app

def test_pedidos_accesibilidad_tooltips(app):
    view = PedidosView(usuario_actual="test")
    # Botón principal
    boton = view.boton_agregar
    assert boton.toolTip() == "Agregar pedido"
    # Tabla principal
    tabla = view.tabla_pedidos
    assert tabla.toolTip() == "Tabla de pedidos"
    assert tabla.accessibleName() == "Tabla principal de pedidos"
    header = tabla.horizontalHeader()
    if header is not None:
        assert header.objectName() == "header_pedidos"
    # QLabel feedback
    assert view.label_feedback.accessibleName() == "Mensaje de feedback de pedidos"
    assert view.label_feedback.accessibleDescription() == "Mensaje de feedback visual y accesible para el usuario"
    # QLabel título
    assert view.label_titulo.text() == "Gestión de Pedidos"
    # Inputs principales
    for widget in [view.obra_combo, view.fecha_pedido, view.materiales_input, view.observaciones_input]:
        assert widget.toolTip() == "Campo de texto"
        assert widget.accessibleName() == "Campo de texto de pedidos"
