import pytest
from PyQt6.QtWidgets import QApplication
from modules.auditoria.view import AuditoriaView

@pytest.fixture(scope="module")
def app():
    import sys
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app

def test_auditoria_accesibilidad(app):
    view = AuditoriaView()
    # Botón agregar
    assert view.boton_agregar.toolTip() == "Agregar registro"
    assert view.boton_agregar.accessibleName() == "Botón agregar registro de auditoría"
    # Botón ver logs
    assert view.boton_ver_logs.toolTip() == "Ver logs de auditoría"
    assert view.boton_ver_logs.accessibleName() == "Botón ver logs de auditoría"
    # Tabla principal
    assert view.tabla_logs.toolTip() == "Tabla de logs de auditoría"
    assert view.tabla_logs.accessibleName() == "Tabla principal de auditoría"
    # Label feedback
    assert view.label_feedback.accessibleName() == "Feedback visual de Auditoría"
    assert view.label_feedback.accessibleDescription() == "Mensaje de feedback visual y accesible para el usuario en Auditoría"
    # Título
    assert view.label_titulo.accessibleDescription() == "Título principal de la vista de Auditoría"
    # Todos los QLabel tienen accessibleDescription
    for widget in view.findChildren(type(view.label_feedback)):
        assert widget.accessibleDescription() != ""
