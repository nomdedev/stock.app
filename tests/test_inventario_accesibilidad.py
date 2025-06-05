import pytest
from PyQt6.QtWidgets import QApplication
from modules.inventario.view import InventarioView

@pytest.fixture(scope="module")
def app():
    import sys
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app

def test_inventario_accesibilidad(app):
    view = InventarioView()
    # Botón agregar
    assert view.boton_agregar.toolTip() == "Agregar item"
    assert view.boton_agregar.accessibleName() == "Botón agregar ítem de inventario"
    # Label feedback
    assert view.label_feedback.accessibleName() == "Feedback visual de Inventario"
    assert view.label_feedback.accessibleDescription() == "Mensaje de feedback visual y accesible para el usuario en Inventario"
    # Título
    assert view.label_titulo.accessibleDescription() == "Título principal de la vista de Inventario"
    # Botones de barra superior (excepto el primero, que es el mismo que boton_agregar)
    for btn, (_, tooltip, _, accesible) in zip(view.findChildren(type(view.boton_agregar))[1:], [
        ("excel_icon.svg", "Exportar a Excel", None, "Botón exportar inventario a Excel"),
        ("pdf_icon.svg", "Exportar a PDF", None, "Botón exportar inventario a PDF"),
        ("search_icon.svg", "Buscar ítem", None, "Botón buscar ítem de inventario"),
        ("qr_icon.svg", "Generar código QR", None, "Botón generar código QR de inventario"),
        ("viewdetails.svg", "", None, "Botón ver obras pendientes de material"),
        ("reserve-stock.svg", "", None, "Botón reservar lote de perfiles"),
    ]):
        if accesible:
            assert btn.accessibleName() == accesible
    # Tabla principal solo si existe
    if hasattr(view, 'tabla_inventario'):
        assert view.tabla_inventario.toolTip() == "Tabla principal de inventario"
        assert view.tabla_inventario.accessibleName() == "Tabla de inventario"
    # Todos los QLabel tienen accessibleDescription
    for widget in view.findChildren(type(view.label_feedback)):
        assert widget.accessibleDescription() != ""
