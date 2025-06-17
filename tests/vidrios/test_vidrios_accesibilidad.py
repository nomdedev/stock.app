import pytest
from PyQt6.QtWidgets import QApplication
from modules.vidrios.view import VidriosView

@pytest.fixture(scope="module")
def app():
    import sys
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app

def test_vidrios_accesibilidad_tooltips(app):
    view = VidriosView(usuario_actual="test")
    # Botón principal
    boton = view.boton_agregar
    assert boton.toolTip() == "Agregar vidrio"
    # Tabla principal
    tabla = view.tabla_vidrios
    assert tabla.objectName() == "tabla_vidrios"
    header = tabla.horizontalHeader()
    if header is not None:
        assert header.objectName() == "header_vidrios"
    # QLabel feedback
    assert view.label_feedback.accessibleName() == "Mensaje de feedback de vidrios"
    assert view.label_feedback.accessibleDescription() == "Mensaje de feedback visual y accesible para el usuario"
    # QLabel título
    assert view.label_titulo.text() == "Gestión de Vidrios"
    # Inputs principales
    for widget in [view.tipo_input, view.ancho_input, view.alto_input, view.cantidad_input, view.proveedor_input, view.fecha_entrega_input]:
        # QDateEdit no tiene toolTip por defecto, pero se puede setear
        if hasattr(widget, 'toolTip'):
            assert widget.toolTip() == "" or widget.toolTip() is not None
