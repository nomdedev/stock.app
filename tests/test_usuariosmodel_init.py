import pytest
from modules.usuarios.model import UsuariosModel
from core.database import DatabaseConnection

def test_usuariosmodel_init_requires_db_connection():
    with pytest.raises(TypeError):
        UsuariosModel()  # Debe fallar si no se pasa db_connection
    # Debe funcionar si se pasa db_connection
    db = DatabaseConnection()
    model = UsuariosModel(db_connection=db)
    assert model is not None
