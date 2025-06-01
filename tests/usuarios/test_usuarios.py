# --- TESTS DE USUARIOS: USO SEGURO Y AISLADO, SIN CREDENCIALES REALES ---
# Todos los tests usan MockDBConnection, nunca una base real ni credenciales.
# Si se detecta un test que intenta conectar a una base real, debe ser refactorizado o migrado a integración.
# Si necesitas integración real, usa variables de entorno y archivos de configuración fuera del repo.
# --- FIN DE NOTA DE SEGURIDAD ---

import unittest
import sys
import os

# Agregar el directorio raíz del proyecto al PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

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
        # Simular respuesta para obtener_modulos_permitidos (admin/supervisor)
        if "SELECT DISTINCT modulo FROM permisos_modulos" in query:
            return self.query_result
        # Simular respuesta para obtener_modulos_permitidos (usuario normal)
        if "SELECT modulo FROM permisos_modulos WHERE id_usuario = ? AND puede_ver = 1" in query:
            return self.query_result
        # Simular usuarios activos
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
        datos = ("Juan", "Pérez", "juan.perez@example.com", "juan", "hash", "admin")
        self.usuarios_model.agregar_usuario(datos)
        if self.mock_db.last_query is None:
            self.fail("last_query es None, posible error en el método agregar_usuario o en el mock.")
        self.assertIn("INSERT INTO usuarios (nombre, apellido, email, usuario, password_hash, rol, estado)", self.mock_db.last_query)
        self.assertEqual(self.mock_db.last_params, datos)

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

    def test_obtener_modulos_permitidos(self):
        # Caso admin: debe devolver todos los módulos
        usuario_admin = {'username': 'admin', 'rol': 'admin', 'id': 1}
        self.mock_db.query_result = [('Obras',), ('Inventario',), ('Producción',), ('Compras / Pedidos',)]
        modulos = self.usuarios_model.obtener_modulos_permitidos(usuario_admin)
        self.assertIn('Obras', modulos)
        self.assertIn('Inventario', modulos)
        self.assertIn('Producción', modulos)
        self.assertIn('Compras / Pedidos', modulos)

        # Caso usuario normal: solo módulos permitidos
        usuario_normal = {'username': 'ana', 'rol': 'usuario', 'id': 2}
        self.mock_db.query_result = [('Inventario',), ('Herrajes',)]
        modulos = self.usuarios_model.obtener_modulos_permitidos(usuario_normal)
        self.assertEqual(modulos, ['Inventario', 'Herrajes'])

        # Caso usuario sin permisos: lista vacía
        usuario_sin_permisos = {'username': 'sinmodulos', 'rol': 'usuario', 'id': 3}
        self.mock_db.query_result = []
        modulos = self.usuarios_model.obtener_modulos_permitidos(usuario_sin_permisos)
        self.assertEqual(modulos, [])

if __name__ == "__main__":
    # Evitar que SystemExit detenga el script
    unittest.main(exit=False)
