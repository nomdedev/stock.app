import pytest
from unittest.mock import MagicMock
from modules.usuarios.login_controller import LoginController
from modules.usuarios.login_view import LoginView
from modules.usuarios.model import UsuariosModel

class MockUsuariosModel(UsuariosModel):
    def __init__(self):
        self.usuarios = {
            'admin': {'usuario': 'admin', 'password_hash': '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 'rol': 'admin', 'id': 1},
            'prueba': {'usuario': 'prueba', 'password_hash': 'c4ca4238a0b923820dcc509a6f75849b', 'rol': 'usuario', 'id': 2}
        }
    def obtener_usuario_por_nombre(self, nombre_usuario):
        return self.usuarios.get(nombre_usuario)
    def validar_password(self, usuario, password):
        import hashlib
        return usuario['password_hash'] == hashlib.sha256(password.encode()).hexdigest()
    def obtener_modulos_permitidos(self, usuario):
        if usuario['rol'] == 'admin':
            return ['Inventario', 'Obras', 'Usuarios', 'Configuración']
        return ['Inventario']

@pytest.fixture
def login_view():
    return LoginView()

@pytest.fixture
def usuarios_model():
    return MockUsuariosModel()

@pytest.fixture
def login_controller(login_view, usuarios_model):
    return LoginController(login_view, usuarios_model)

def test_login_exitoso(login_controller, login_view):
    login_view.usuario_input.setText('admin')
    login_view.password_input.setText('password')
    login_controller.login()
    assert login_controller.usuario_autenticado is not None
    assert login_controller.usuario_autenticado['usuario'] == 'admin'

def test_login_fallido_usuario_incorrecto(login_controller, login_view):
    login_view.usuario_input.setText('noexiste')
    login_view.password_input.setText('password')
    login_controller.login()
    assert login_controller.usuario_autenticado is None
    assert 'incorrectos' in login_view.label_error.text().lower()

def test_login_fallido_password_incorrecta(login_controller, login_view):
    login_view.usuario_input.setText('admin')
    login_view.password_input.setText('mala')
    login_controller.login()
    assert login_controller.usuario_autenticado is None
    assert 'incorrectos' in login_view.label_error.text().lower()

def test_feedback_visual_error(login_controller, login_view):
    login_view.mostrar_error('Error de prueba')
    assert '❌' in login_view.label_error.text()
    assert '#ef4444' in login_view.label_error.styleSheet()

def test_tooltips_y_accesibilidad(login_view):
    assert login_view.usuario_input.toolTip() != ''
    assert login_view.password_input.toolTip() != ''
    assert login_view.boton_login.toolTip() != ''
    assert login_view.usuario_input.accessibleName() != ''
    assert login_view.password_input.accessibleName() != ''
    assert login_view.boton_login.accessibleName() != ''
    assert login_view.usuario_input.accessibleDescription() != ''
    assert login_view.password_input.accessibleDescription() != ''
    assert login_view.boton_login.accessibleDescription() != ''

def test_login_usuario_vacio(login_controller, login_view):
    """Debe mostrar error visual si el usuario está vacío."""
    login_view.usuario_input.setText('')
    login_view.password_input.setText('password')
    login_controller.login()
    assert login_controller.usuario_autenticado is None
    assert 'usuario' in login_view.label_error.text().lower()

def test_login_password_vacia(login_controller, login_view):
    """Debe mostrar error visual si la contraseña está vacía."""
    login_view.usuario_input.setText('admin')
    login_view.password_input.setText('')
    login_controller.login()
    assert login_controller.usuario_autenticado is None
    assert 'contraseña' in login_view.label_error.text().lower()

def test_login_usuario_inactivo(login_controller, login_view, usuarios_model):
    """Debe mostrar error visual si el usuario está inactivo."""
    usuarios_model.usuarios['admin']['estado'] = 'inactivo'
    login_view.usuario_input.setText('admin')
    login_view.password_input.setText('password')
    login_controller.login()
    assert login_controller.usuario_autenticado is None
    assert 'inactivo' in login_view.label_error.text().lower()
    usuarios_model.usuarios['admin']['estado'] = 'activo'  # restaurar

def test_login_usuario_sin_permisos(login_controller, login_view, usuarios_model):
    """Debe mostrar error visual si el usuario no tiene permisos para ningún módulo."""
    usuarios_model.obtener_modulos_permitidos = lambda u: []
    login_view.usuario_input.setText('prueba')
    login_view.password_input.setText('1')  # hash de '1' para prueba
    login_controller.login()
    assert login_controller.usuario_autenticado is not None
    assert 'permiso' in login_view.label_error.text().lower() or 'acceso' in login_view.label_error.text().lower()

def test_feedback_visual_todos_estados(login_view):
    """Debe mostrar feedback visual correcto para éxito, error, advertencia e info."""
    login_view.mostrar_feedback('Éxito', tipo='exito')
    assert '✅' in login_view.label_feedback.text()
    login_view.mostrar_feedback('Error', tipo='error')
    assert '❌' in login_view.label_feedback.text()
    login_view.mostrar_feedback('Advertencia', tipo='advertencia')
    assert '⚠️' in login_view.label_feedback.text()
    login_view.mostrar_feedback('Info', tipo='info')
    assert 'ℹ️' in login_view.label_feedback.text()

def test_login_error_conexion(monkeypatch, login_controller, login_view):
    """Debe mostrar feedback visual de error si ocurre excepción inesperada (simular error de conexión)."""
    monkeypatch.setattr(login_controller.usuarios_model, 'obtener_usuario_por_nombre', lambda u: 1/0)
    login_view.usuario_input.setText('admin')
    login_view.password_input.setText('password')
    login_controller.login()
    assert 'error' in login_view.label_error.text().lower() or 'excepción' in login_view.label_error.text().lower()

def test_accesibilidad_foco_visible(login_view):
    """Todos los widgets críticos deben tener foco visible y accesibilidad activada."""
    for widget in [login_view.usuario_input, login_view.password_input, login_view.boton_login]:
        assert widget.focusPolicy() is not None
        assert widget.accessibleName() != ''
        assert widget.accessibleDescription() != ''
