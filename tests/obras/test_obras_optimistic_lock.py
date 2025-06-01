# TEST OPTIMISTIC LOCK: Test unitario simulado solo con mocks (sin base de datos real)
import pytest
from unittest.mock import MagicMock

class MockDB:
    def __init__(self):
        self.rowversion_actual = b"abc123"
        self.estado = "En curso"
    def get_rowversion(self, id_obra):
        return self.rowversion_actual
    def update_obra(self, id_obra, datos, rowversion):
        # Simula conflicto de rowversion
        if rowversion != self.rowversion_actual:
            raise OptimisticLockError("Conflicto de rowversion")
        self.estado = datos["estado"]

class OptimisticLockError(Exception):
    pass

class ObrasModel:
    def __init__(self, db):
        self.db = db
    def editar_obra(self, id_obra, datos, rowversion):
        self.db.update_obra(id_obra, datos, rowversion)


def test_editar_obra_conflicto_rowversion():
    db = MockDB()
    model = ObrasModel(db)
    id_obra = 1
    rowversion_vieja = b"vieja"
    datos = {"estado": "Cancelada"}
    with pytest.raises(OptimisticLockError):
        model.editar_obra(id_obra, datos, rowversion_vieja)
