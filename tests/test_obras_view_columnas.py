import pytest
from PyQt6.QtWidgets import QApplication
from modules.obras.view import ObrasView
import os
import json

def limpiar_config_columnas(path, usuario):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if usuario in data:
            del data[usuario]
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

@pytest.fixture(scope="module")
def app():
    import sys
    return QApplication.instance() or QApplication(sys.argv)

@pytest.mark.parametrize("usuario", ["testuser1", "testuser2"])
def test_personalizacion_columnas_obras(app, usuario):
    config_path = "config_obras_columns.json"
    limpiar_config_columnas(config_path, usuario)
    view = ObrasView(usuario_actual=usuario)
    # Por defecto todas las columnas visibles
    for idx, header in enumerate(view.obras_headers):
        assert not view.tabla_obras.isColumnHidden(idx)
    # Ocultar una columna
    view.toggle_columna(0, view.obras_headers[0], False)
    assert view.tabla_obras.isColumnHidden(0)
    # Mostrarla de nuevo
    view.toggle_columna(0, view.obras_headers[0], True)
    assert not view.tabla_obras.isColumnHidden(0)
    # Persistencia: simular reinicio
    view2 = ObrasView(usuario_actual=usuario)
    assert not view2.tabla_obras.isColumnHidden(0)
    # Ocultar varias y verificar
    for idx in range(3):
        view2.toggle_columna(idx, view2.obras_headers[idx], False)
    for idx in range(3):
        assert view2.tabla_obras.isColumnHidden(idx)
    # Persistencia tras ocultar
    view3 = ObrasView(usuario_actual=usuario)
    for idx in range(3):
        assert view3.tabla_obras.isColumnHidden(idx)
    # Limpiar config al final
    limpiar_config_columnas(config_path, usuario)
