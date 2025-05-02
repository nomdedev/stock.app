import pytest
import sys
import os
from PyQt6.QtWidgets import QApplication

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from modules.produccion.view import ProduccionView

@pytest.fixture
def app():
    return QApplication([])

@pytest.fixture
def produccion_view(app):
    return ProduccionView()

def test_botones_existen(produccion_view):
    assert produccion_view.boton_agregar is not None, "El botón 'Agregar Etapa' no existe."
    assert produccion_view.boton_ver_detalles is not None, "El botón 'Ver Detalles de Abertura' no existe."
    assert produccion_view.boton_finalizar_etapa is not None, "El botón 'Finalizar Etapa' no existe."

def test_botones_accion_placeholder(produccion_view):
    try:
        produccion_view.boton_agregar.click()
        produccion_view.boton_ver_detalles.click()
        produccion_view.boton_finalizar_etapa.click()
    except Exception as e:
        pytest.fail(f"Un botón lanzó una excepción: {e}")
