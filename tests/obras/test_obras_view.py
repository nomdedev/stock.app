from PyQt6.QtWidgets import QApplication
import sys
import os
import types
import pytest

print('DEBUG: test_obras_view.py cargado')
try:
    from modules.obras.view import ObrasView
    print('DEBUG: ObrasView importado correctamente')
except Exception as e:
    print(f'DEBUG: Error importando ObrasView: {e}')

# Ajustar path para importar el módulo correctamente
dir_actual = os.path.dirname(os.path.abspath(__file__))
modulo_path = os.path.abspath(os.path.join(dir_actual, '../modules/obras'))
sys.path.insert(0, modulo_path)

@pytest.fixture(scope="module")
def app():
    app = QApplication.instance()
    if not app:
        app = QApplication([])
    yield app

@pytest.fixture
def obras_view(app):
    return ObrasView(usuario_actual="testuser", db_connection=None)

def test_layout_and_headers(obras_view):
    # Verifica que el layout principal existe y es QVBoxLayout
    assert obras_view.layout() is not None
    assert obras_view.main_layout is not None
    # Verifica que los headers por defecto están presentes
    assert hasattr(obras_view, 'obras_headers')
    assert isinstance(obras_view.obras_headers, list)
    assert len(obras_view.obras_headers) > 0
    # Verifica que la tabla tiene el mismo número de columnas que headers
    assert obras_view.tabla_obras.columnCount() == len(obras_view.obras_headers)
    # Verifica que los headers de la tabla coinciden
    for i, header in enumerate(obras_view.obras_headers):
        assert obras_view.tabla_obras.horizontalHeaderItem(i).text() == header

def test_columnas_visibles_config(obras_view):
    # Simula ocultar una columna y verifica que se oculte
    header = obras_view.obras_headers[0]
    obras_view.toggle_columna(0, header, False)
    assert obras_view.tabla_obras.isColumnHidden(0)
    # Vuelve a mostrarla
    obras_view.toggle_columna(0, header, True)
    assert not obras_view.tabla_obras.isColumnHidden(0)

def test_menu_columnas_no_header(monkeypatch, obras_view):
    # Fuerza el header a None y verifica que no explote
    monkeypatch.setattr(obras_view.tabla_obras, "horizontalHeader", lambda: None)
    try:
        obras_view.mostrar_menu_columnas(pos=None)
    except Exception:
        pytest.fail("mostrar_menu_columnas lanza excepción si header es None")

def test_menu_columnas_header_excepciones(monkeypatch, obras_view):
    # Fuerza el header a None y verifica que no explote
    monkeypatch.setattr(obras_view.tabla_obras, "horizontalHeader", lambda: None)
    try:
        obras_view.mostrar_menu_columnas_header(0)
    except Exception:
        pytest.fail("mostrar_menu_columnas_header lanza excepción si header es None")

def test_feedback_visual(obras_view):
    # Verifica que el feedback visual cambia el texto y color
    obras_view.mostrar_mensaje("Mensaje de prueba", tipo="info")
    assert "Mensaje de prueba" in obras_view.label_feedback.text()
    obras_view.mostrar_mensaje("Error de prueba", tipo="error")
    assert "Error de prueba" in obras_view.label_feedback.text()
