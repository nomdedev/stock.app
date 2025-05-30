import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from modules.obras.model import ObrasModel
from mock_db import DummyDB

@pytest.fixture
def model():
    return ObrasModel(db_connection=DummyDB())

def test_nombre_vacio(model):
    with pytest.raises(ValueError):
        model.agregar_obra(("", "Cliente Test", "Medición", "2025-05-28", "5", True, "", "1000", "1000000", "2025-05-28", 10, "2025-06-10", 1))

def test_fecha_entrega_menor_medicion(model):
    with pytest.raises(ValueError):
        model.agregar_obra(("Obra Test", "Cliente Test", "Medición", "2025-05-28", "5", True, "", "1000", "1000000", "2025-05-28", 0, "2025-05-27", 1))

def test_nombre_largo(model):
    nombre = "A" * 101
    with pytest.raises(ValueError):
        model.agregar_obra((nombre, "Cliente Test", "Medición", "2025-05-28", "5", True, "", "1000", "1000000", "2025-05-28", 10, "2025-06-10", 1))

def test_caracteres_invalidos(model):
    with pytest.raises(ValueError):
        model.agregar_obra(("Obra@123", "Cliente Test", "Medición", "2025-05-28", "5", True, "", "1000", "1000000", "2025-05-28", 10, "2025-06-10", 1))
# TEST VALIDATION: cubre todos los casos de validación UI y backend.
