import pytest
from modules.usuarios.model import UsuariosModel

@pytest.mark.parametrize("rol,modulo,esperado", [
    ("admin", "inventario", {"ver": True, "modificar": True, "aprobar": True}),
    ("operador", "inventario", {"ver": True, "modificar": False, "aprobar": False}),
])
def test_permisos_por_rol_y_usuario(mocker, rol, modulo, esperado):
    mock_db = mocker.Mock()
    # Simular respuesta de la base según el rol
    if rol == "admin":
        mock_db.ejecutar_query.side_effect = [
            [(modulo, 1, 1, 1)],  # obtener_permisos_por_rol
            [(1, 1, 1)]           # obtener_permisos_por_usuario
        ]
    else:
        mock_db.ejecutar_query.side_effect = [
            [(modulo, 1, 0, 0)],
            [(1, 0, 0)]
        ]
    model = UsuariosModel(mock_db)
    permisos_rol = model.obtener_permisos_por_rol(rol)
    assert permisos_rol[0][0] == rol
    permisos_usuario = model.obtener_permisos_por_usuario(1, modulo)
    assert permisos_usuario == esperado
