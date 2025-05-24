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
                self.view.mostrar_error("Usuario o contraseña incorrectos.")
                return
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if user['password'] != password_hash:
                self.view.mostrar_error("Usuario o contraseña incorrectos.")
                return
            self.usuario_autenticado = user
            self.view.limpiar_error()
        except Exception as e:
            log_error(f"Error en login: {e}")
            self.view.mostrar_error("Error interno de autenticación.")
