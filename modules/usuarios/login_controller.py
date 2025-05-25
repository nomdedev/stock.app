from PyQt6.QtWidgets import QMessageBox
from modules.usuarios.model import UsuariosModel
from core.logger import log_error
import hashlib

class LoginController:
    def __init__(self, view, usuarios_model):
        self.view = view
        self.usuarios_model = usuarios_model
        self.view.boton_login.clicked.connect(self.login)
        self.usuario_autenticado = None

    def login(self):
        usuario = self.view.usuario_input.text().strip()
        password = self.view.password_input.text().strip()
        if not usuario or not password:
            self.view.mostrar_error("Ingrese usuario y contraseña.")
            return
        try:
            user = self.usuarios_model.obtener_usuario_por_nombre(usuario)
            if not user:
                self._registrar_login_fallido(usuario)
                self.view.mostrar_error("Usuario o contraseña incorrectos.")
                return
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if user['password_hash'] != password_hash:
                self._registrar_login_fallido(usuario)
                self.view.mostrar_error("Usuario o contraseña incorrectos.")
                return
            self.usuario_autenticado = user
            self.view.limpiar_error()
        except Exception as e:
            log_error(f"Error en login: {e}")
            self.view.mostrar_error("Error interno de autenticación.")

    def _registrar_login_fallido(self, usuario):
        # Registrar intento fallido en logs de auditoría, sin exponer datos sensibles
        try:
            ip = getattr(self.view, 'ip', 'desconocida')
            self.usuarios_model.registrar_login_fallido(ip, usuario)
        except Exception as e:
            log_error(f"Error registrando login fallido: {e}")
