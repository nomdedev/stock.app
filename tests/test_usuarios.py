import unittest
from modules.usuarios.model import UsuariosModel

class MockDBConnection:
    def __init__(self):
        self.last_query = None
        self.last_params = None
        self.query_result = []

    def execute(self, query, params=None):
        self.last_query = query
        self.last_params = params

    def fetchall(self):
        return self.query_result

    def set_query_result(self, result):
        self.query_result = result

    def ejecutar_query(self, query, params=None):
        self.last_query = query
        self.last_params = params
        if "SELECT * FROM usuarios WHERE estado = 'activo'" in query:
            return [
                (1, "Juan", "Pérez", "juan.perez@example.com", "admin", "activo"),
                (2, "Ana", "Gómez", "ana.gomez@example.com", "compras", "activo")
            ]
        return []

class TestUsuariosModel(unittest.TestCase):

    def setUp(self):
        # Simulación de conexión a base de datos
        self.mock_db = MockDBConnection()
        self.usuarios_model = UsuariosModel(self.mock_db)

    def test_crear_usuario(self):
        # Probar creación de un usuario utilizando el método correcto
        self.usuarios_model.agregar_usuario(("Juan", "juan.perez@example.com", "admin"))
        self.assertEqual(self.mock_db.last_query, "INSERT INTO usuarios (nombre, email, rol) VALUES (?, ?, ?)")
        self.assertEqual(self.mock_db.last_params, ("Juan", "juan.perez@example.com", "admin"))

    def test_actualizar_estado_usuario(self):
        # Probar actualización del estado de un usuario
        self.usuarios_model.actualizar_estado_usuario(1, "suspendido")
        self.assertEqual(self.mock_db.last_query, "UPDATE usuarios SET estado = ? WHERE id = ?")
        self.assertEqual(self.mock_db.last_params, ("suspendido", 1))

    def test_obtener_usuarios_activos(self):
        # Probar obtención de usuarios activos
        self.mock_db.set_query_result([
            (1, "Juan", "Pérez", "juan.perez@example.com", "admin", "activo"),
            (2, "Ana", "Gómez", "ana.gomez@example.com", "compras", "activo")
        ])
        usuarios = self.usuarios_model.obtener_usuarios_activos()
        self.assertEqual(len(usuarios), 2)
        self.assertEqual(usuarios[0][1], "Juan")

if __name__ == "__main__":
    unittest.main()
