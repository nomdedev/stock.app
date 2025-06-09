import pytest
from PyQt6.QtWidgets import QApplication
from modules.mantenimiento.view import MantenimientoView

@pytest.fixture(scope="module")
def app():
    import sys
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app

def test_mantenimiento_accesibilidad_tooltips(app):
    view = MantenimientoView()
    # Botón principal
    boton = view.boton_agregar
    assert boton.toolTip() in ("Agregar mantenimiento", "Agregar tarea de mantenimiento")
    # El refuerzo puede poner el accessibleName en showEvent, forzamos manualmente
    if not boton.accessibleName():
        view._reforzar_accesibilidad()
    assert boton.accessibleName() == "Botón agregar tarea de mantenimiento"
    # Tabla principal
    tabla = view.tabla_tareas
    assert tabla.toolTip() == "Tabla de tareas de mantenimiento"
    assert tabla.accessibleName() == "Tabla principal de mantenimiento"
    header = tabla.horizontalHeader()
    if header is not None:
        assert header.objectName() == "header_tareas"
    # QLabel feedback
    assert view.label_feedback.accessibleName() == "Mensaje de feedback de mantenimiento"
    assert view.label_feedback.accessibleDescription() == "Mensaje de feedback visual y accesible para el usuario"
    # QLabel título
    assert view.label_titulo.text() == "Gestión de Mantenimiento"
