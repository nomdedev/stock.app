import pytest
from PyQt6.QtWidgets import QApplication
from modules.logistica.view import LogisticaView

@pytest.fixture(scope="module")
def app():
    import sys
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app

def test_logistica_accesibilidad_tooltips(app):
    view = LogisticaView(usuario_actual="test")
    # Botón principal
    boton = view.boton_agregar
    assert boton.toolTip() == "Agregar envío" or boton.toolTip() == "Agregar registro"
    assert boton.accessibleName() == "Botón agregar envío"
    # Tablas principales
    for tabla in [view.tabla_obras, view.tabla_envios, view.tabla_servicios]:
        assert tabla.toolTip() == "Tabla de datos"
        assert tabla.accessibleName() == "Tabla principal de logística"
        header = tabla.horizontalHeader()
        if header is not None:
            assert header.objectName() == "header_logistica"
    # QLineEdit principales
    for input_widget in [view.buscar_input, view.id_item_input]:
        assert input_widget.toolTip() in ("Campo de búsqueda o ID", "Campo de texto")
        assert input_widget.accessibleName() == "Campo de búsqueda o ID de logística"
    # QLabel feedback
    assert view.label_feedback.accessibleName() == "Mensaje de feedback de logística"
    assert view.label_feedback.accessibleDescription() == "Mensaje de feedback visual y accesible para el usuario"
    # QLabel título
    assert view.label_titulo.text() == "Gestión de Logística"
    # Icono y título en header
    header_layout = view.main_layout.itemAt(0).layout()
    icon_label = header_layout.itemAt(0).widget()
    titulo_label = header_layout.itemAt(1).widget()
    assert icon_label.toolTip() == "Icono de Logística"
    assert icon_label.accessibleName() == "Icono de Logística"
    assert "Logística" in titulo_label.text()
    assert "Logística" in titulo_label.accessibleName()
