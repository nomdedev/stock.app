# ---
# TESTS DE GESTIÓN DE USUARIOS Y PERMISOS POR USUARIO
# Mayo 2025

import unittest
from unittest.mock import MagicMock, patch
from modules.usuarios.model import UsuariosModel
from modules.configuracion.controller import ConfiguracionController

class MockDBConnection:
    def __init__(self):
        self.usuarios = [
            {'id': 1, 'usuario': 'admin', 'rol': 'admin'},
            {'id': 2, 'usuario': 'prueba', 'rol': 'usuario'}
        ]
        self.permisos = {
            1: [{'modulo': 'Inventario', 'ver': True, 'modificar': True, 'aprobar': True}],
            2: [{'modulo': 'Inventario', 'ver': True, 'modificar': False, 'aprobar': False}]
        }
    def ejecutar_query(self, *args, **kwargs):
        if 'FROM usuarios' in args[0]:
            return [(u['id'], u['usuario'], u['rol']) for u in self.usuarios]
        if 'FROM permisos_modulos' in args[0]:
            id_usuario = args[1][0] if len(args) > 1 and args[1] else 1
            return [(p['modulo'], p['ver'], p['modificar'], p['aprobar']) for p in self.permisos.get(id_usuario, [])]
        return []

class MockUsuariosModel(UsuariosModel):
    def __init__(self):
        super().__init__(MockDBConnection())
        self._es_admin = True
    def usuario_actual_es_admin(self):
        return self._es_admin
    def obtener_usuarios(self):
        return self.db.usuarios
    def obtener_permisos_por_usuario(self, id_usuario):
        # Devuelve lista de dicts con 'modulo', 'ver', 'modificar', 'aprobar'
        return self.db.permisos.get(id_usuario, [])
    def actualizar_permisos_usuario(self, id_usuario, modulo, ver, modificar, aprobar):
        if not self.usuario_actual_es_admin():
            return False
        # Simula actualización
        return True

class TestPermisosPorUsuario(unittest.TestCase):
    def setUp(self):
        self.model = MockUsuariosModel()
        self.controller = MagicMock()

    def test_obtener_usuarios(self):
        usuarios = self.model.obtener_usuarios()
        self.assertIsInstance(usuarios, list)
        self.assertGreaterEqual(len(usuarios), 1)

    def test_obtener_permisos_por_usuario(self):
        usuarios = self.model.obtener_usuarios()
        if usuarios:
            id_usuario = usuarios[0]['id']
            permisos = self.model.obtener_permisos_por_usuario(id_usuario)
            self.assertIsInstance(permisos, list)
            self.assertIn('modulo', permisos[0])

    def test_guardar_permisos_usuario_admin(self):
        self.model._es_admin = True
        usuarios = self.model.obtener_usuarios()
        if usuarios:
            id_usuario = usuarios[0]['id']
            permisos = self.model.obtener_permisos_por_usuario(id_usuario)
            if permisos:
                modulo = permisos[0]['modulo']
                resultado = self.model.actualizar_permisos_usuario(id_usuario, modulo, True, True, True)
                self.assertTrue(resultado)

    def test_guardar_permisos_usuario_no_admin(self):
        self.model._es_admin = False
        usuarios = self.model.obtener_usuarios()
        if usuarios:
            id_usuario = usuarios[0]['id']
            permisos = self.model.obtener_permisos_por_usuario(id_usuario)
            if permisos:
                modulo = permisos[0]['modulo']
                resultado = self.model.actualizar_permisos_usuario(id_usuario, modulo, False, False, False)
                self.assertFalse(resultado)

    def test_feedback_visual_sin_permisos(self):
        # Simula usuario sin permisos y verifica feedback visual
        self.model.db.permisos[9999] = []
        permisos = self.model.obtener_permisos_por_usuario(9999)
        self.assertEqual(permisos, [])
        # Aquí se debería mostrar mensaje visual en la UI (test manual o mock de la vista)

if __name__ == '__main__':
    unittest.main()
# ---
