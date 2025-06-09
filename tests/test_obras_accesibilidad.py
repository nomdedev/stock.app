import pytest
from PyQt6.QtWidgets import QApplication
from modules.obras.view import ObrasView

@pytest.fixture(scope="module")
def app():
    import sys
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app

def test_obras_accesibilidad_tooltips(app):
    view = ObrasView(usuario_actual="test")
    # Botón principal
    boton = view.boton_agregar
    assert boton.toolTip() == "Agregar nueva obra"
    assert boton.accessibleName() == "Botón agregar obra"
    assert boton.accessibleDescription() == "Botón principal para agregar una nueva obra"
    # Botón verificar obra
    boton_verificar = view.boton_verificar_obra
    assert boton_verificar.toolTip() == "Verificar existencia de obra en la base de datos SQL"
    assert boton_verificar.accessibleName() == "Botón verificar obra en SQL"
    assert boton_verificar.accessibleDescription() == "Botón para verificar si la obra existe en la base de datos SQL"
    # Tabla principal
    tabla = view.tabla_obras
    assert tabla.toolTip() == "Tabla principal de obras"
    assert tabla.accessibleName() == "Tabla de obras"
    assert tabla.accessibleDescription() == "Tabla que muestra todas las obras registradas"
    header = tabla.horizontalHeader()
    if header is not None:
        # No se fuerza objectName en header, solo robustez visual
        pass
    # QLabel feedback
    assert view.label_feedback.accessibleName() == "Mensaje de feedback de obras"
    assert view.label_feedback.accessibleDescription() == "Mensaje de feedback visual y accesible para el usuario"
    # QLabel título
    assert view.label.text() == "Gestión de Obras"
    assert view.label.accessibleName() == "Título de módulo Obras"
    assert view.label.accessibleDescription() == "Encabezado principal de la vista de obras"
