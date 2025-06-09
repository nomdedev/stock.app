import pytest
from PyQt6.QtWidgets import QApplication
from modules.herrajes.view import HerrajesView

@pytest.fixture(scope="module")
def app():
    import sys
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app

def test_herrajes_accesibilidad(app):
    view = HerrajesView()
    # Botón agregar
    assert view.boton_agregar.toolTip() == "Agregar herraje"
    assert view.boton_agregar.accessibleName() == "Botón para agregar un nuevo herraje"
    # Label feedback
    assert view.label_feedback.accessibleName() == "Feedback visual de Herrajes"
    assert view.label_feedback.accessibleDescription() == "Mensaje de feedback visual y accesible para el usuario en Herrajes"
    # Título
    assert view.label_titulo.accessibleDescription() == "Título principal de la vista de Herrajes"
    # Botones de barra
    for btn, (_, tooltip, accesible) in zip(view.barra_botones, [
        ("add-material.svg", "Agregar herraje", "Botón para agregar un nuevo herraje"),
        ("excel_icon.svg", "Exportar a Excel", "Botón para exportar la tabla de herrajes a Excel"),
        ("search_icon.svg", "Buscar herraje", "Botón para buscar herrajes en la tabla")
    ]):
        assert btn.toolTip() == tooltip
        assert btn.accessibleName() == accesible
    # Tabla principal
    assert view.tabla_herrajes.toolTip() == "Tabla principal de herrajes"
    assert view.tabla_herrajes.accessibleName() == "Tabla de herrajes"
    # Todos los QLabel tienen accessibleDescription
    for widget in view.findChildren(type(view.label_feedback)):
        assert widget.accessibleDescription() != ""
