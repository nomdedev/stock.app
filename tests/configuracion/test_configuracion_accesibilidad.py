import pytest
from PyQt6.QtWidgets import QApplication
from modules.configuracion.view import ConfiguracionView

@pytest.fixture(scope="module")
def app():
    import sys
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app

def test_configuracion_accesibilidad(app):
    view = ConfiguracionView()
    # Botón agregar
    assert view.boton_agregar.toolTip() == "Agregar configuración"
    assert view.boton_agregar.accessibleName() == "Botón agregar configuración"
    # Label feedback
    assert view.label_feedback.accessibleName() == "Feedback visual de Configuración"
    assert view.label_feedback.accessibleDescription() == "Mensaje de feedback visual y accesible para el usuario en Configuración"
    # Título
    assert view.label_titulo.accessibleDescription() == "Título principal de la vista de Configuración"
    # Botones de acción
    assert view.boton_seleccionar_csv.accessibleName() == "Botón seleccionar archivo CSV/Excel para importar inventario"
    assert view.boton_importar_csv.accessibleName() == "Botón importar inventario a la base de datos"
    # Tabla de preview
    assert view.preview_table.toolTip() == "Tabla de previsualización de inventario"
    assert view.preview_table.accessibleName() == "Tabla de preview de configuración"
    # Todos los QLabel tienen accessibleDescription
    for widget in view.findChildren(type(view.label_feedback)):
        assert widget.accessibleDescription() != ""
