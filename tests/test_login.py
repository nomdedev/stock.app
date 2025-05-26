import unittest
from PyQt6.QtWidgets import QApplication
from modules.usuarios.login_view import LoginView
from modules.usuarios.login_controller import LoginController
from modules.usuarios.model import UsuariosModel
from core.database import DatabaseConnection
import sys

app = QApplication.instance() or QApplication(sys.argv)

class TestLogin(unittest.TestCase):
    def setUp(self):
        self.db_connection = DatabaseConnection()
        self.db_connection.conectar_a_base("users")
        # Crear tabla permisos_modulos si no existe (SQL Server compatible)
        self.db_connection.ejecutar_query('''
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='permisos_modulos' AND xtype='U')
            CREATE TABLE permisos_modulos (
                id INT IDENTITY(1,1) PRIMARY KEY,
                id_usuario INT NOT NULL,
                modulo NVARCHAR(64) NOT NULL,
                puede_ver BIT NOT NULL DEFAULT 0,
                puede_modificar BIT NOT NULL DEFAULT 0,
                puede_aprobar BIT NOT NULL DEFAULT 0,
                creado_por INT,
                fecha_creacion DATETIME DEFAULT GETDATE()
            )
        ''')
        self.usuarios_model = UsuariosModel(db_connection=self.db_connection)
        self.usuarios_model.crear_usuarios_iniciales()
        self.login_view = LoginView()
        self.login_controller = LoginController(self.login_view, self.usuarios_model)

    def test_login_admin(self):
        self.login_view.usuario_input.setText("admin")
        self.login_view.password_input.setText("admin")
        self.login_controller.login()
        user = self.login_controller.usuario_autenticado
        self.assertIsNotNone(user, f"No se autenticó admin. Mensaje: {self.login_view.label_error.text()}")
        if user is not None:
            self.assertEqual(user["usuario"], "admin")
            self.assertEqual(user["rol"], "admin")

    def test_login_prueba(self):
        self.login_view.usuario_input.setText("prueba")
        self.login_view.password_input.setText("1")
        self.login_controller.login()
        user = self.login_controller.usuario_autenticado
        self.assertIsNotNone(user, f"No se autenticó prueba. Mensaje: {self.login_view.label_error.text()}")
        if user is not None:
            self.assertEqual(user["usuario"], "prueba")
            self.assertEqual(user["rol"], "usuario")

    def test_login_incorrecto(self):
        self.login_view.usuario_input.setText("admin")
        self.login_view.password_input.setText("incorrecta")
        self.login_controller.login()
        user = self.login_controller.usuario_autenticado
        self.assertIsNone(user)
        self.assertEqual(self.login_view.label_error.text(), "Usuario o contraseña incorrectos.")

if __name__ == "__main__":
    unittest.main()
