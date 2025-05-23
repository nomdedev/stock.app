import unittest
from unittest.mock import Mock
from modules.usuarios.model import UsuariosModel

class MockDBConnection:
    def __init__(self):
        self.usuarios = []
        self.last_id = 0
    def ejecutar_query(self, query, params=None):
        if query.startswith("SELECT"):
            return self.usuarios.copy() if self.usuarios else []
        elif query.startswith("INSERT") and params:
            self.last_id += 1
            # params: (nombre, apellido, email, username, hash, rol)
            nuevo = (self.last_id,) + tuple(params)
            self.usuarios.append(nuevo)
            return []
        elif query.startswith("UPDATE") and "estado" in query and params:
            # params: (nuevo_estado, id_usuario)
            for idx, u in enumerate(self.usuarios):
                if u[0] == params[1]:
                    actualizado = list(u)
                    if len(actualizado) < 7:
                        actualizado += [None] * (7 - len(actualizado))
                    actualizado[6] = params[0]
                    self.usuarios[idx] = tuple(actualizado)
            return []
        return []

class MockUsuariosView:
    def __init__(self):
        self.tabla_data = []
        self.label = Mock()
    def actualizar_tabla(self, data):
        self.tabla_data = data if data else []

class TestUsuariosIntegracion(unittest.TestCase):
    def setUp(self):
        self.mock_db = MockDBConnection()
        self.model = UsuariosModel(self.mock_db)
        self.view = MockUsuariosView()
    def tearDown(self):
        self.mock_db.usuarios.clear()
    def test_agregar_y_reflejar_usuario(self):
        datos = ("Juan", "Pérez", "juan.perez@example.com", "juan", "hash", "admin")
        self.model.agregar_usuario(datos)
        usuarios = self.mock_db.ejecutar_query("SELECT * FROM usuarios")
        if not usuarios: usuarios = []
        self.assertTrue(any(u and len(u) > 3 and u[3] == "juan.perez@example.com" for u in usuarios))
        self.view.actualizar_tabla(usuarios)
        self.assertEqual(self.view.tabla_data, usuarios)
    def test_actualizar_estado_usuario(self):
        datos = ("Ana", "Gómez", "ana.gomez@example.com", "ana", "hash2", "usuario")
        self.model.agregar_usuario(datos)
        usuarios = self.mock_db.ejecutar_query("SELECT * FROM usuarios")
        if not usuarios: usuarios = []
        id_usuario = usuarios[-1][0]
        self.model.actualizar_estado_usuario(id_usuario, "suspendido")
        usuarios = self.mock_db.ejecutar_query("SELECT * FROM usuarios")
        if not usuarios: usuarios = []
        self.assertTrue(any(u and len(u) > 6 and u[6] == "suspendido" for u in usuarios))
        self.view.actualizar_tabla(usuarios)
        self.assertEqual(self.view.tabla_data, usuarios)

if __name__ == "__main__":
    unittest.main()
