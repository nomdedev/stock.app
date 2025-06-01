# --- TESTS DE USUARIOSMODEL INIT: USO SEGURO Y AISLADO, SIN CREDENCIALES REALES ---
# Este test no debe usar DatabaseConnection real. Se usa un mock para cumplir la política de aislamiento.
# --- FIN DE NOTA DE SEGURIDAD ---

import pytest
from modules.usuarios.model import UsuariosModel

class MockDBConnection:
    pass

def test_usuariosmodel_init_requires_db_connection():
    with pytest.raises(TypeError):
        UsuariosModel()  # Debe fallar si no se pasa db_connection
    # Debe funcionar si se pasa un mock de db_connection
    db = MockDBConnection()
    model = UsuariosModel(db_connection=db)
    assert model is not None
