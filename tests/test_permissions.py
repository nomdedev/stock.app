import unittest
from unittest.mock import MagicMock

# Suponemos que existe Sidebar y UsuariosController en el entorno real
# Aquí se usan mocks para simular la lógica de permisos

class MockSidebar:
    def __init__(self, permisos):
        self.permisos = permisos
        self.modulos = [m for m, p in permisos.items() if p.get('ver', False)]
    def get_modulos_visibles(self):
        return self.modulos

class MockController:
    def __init__(self, permisos, modulo):
        self.permisos = permisos
        self.modulo = modulo
        self.usuario_actual = {'id': 2, 'rol': 'usuario'}
        self.usuarios_model = MagicMock()
        self.usuarios_model.tiene_permiso = lambda u, m, a: self.permisos.get(m, {}).get(a, False)
        self.view = MagicMock()
        self.view.label = MagicMock()
        self.auditoria_model = MagicMock()
    def accion_modificar(self):
        # Simula decorador de permisos
        if not self.usuarios_model.tiene_permiso(self.usuario_actual, self.modulo, 'modificar'):
            self.view.label.setText('No tiene permiso para realizar la acción: modificar')
            return False
        return True

class TestPermisosUI(unittest.TestCase):
    def test_sidebar_no_muestra_modulos_sin_permiso_ver(self):
        permisos = {
            'Obras': {'ver': True},
            'Inventario': {'ver': False},
            'Vidrios': {'ver': True}
        }
        sidebar = MockSidebar(permisos)
        visibles = sidebar.get_modulos_visibles()
        self.assertIn('Obras', visibles)
        self.assertIn('Vidrios', visibles)
        self.assertNotIn('Inventario', visibles)

    def test_controlador_rechaza_accion_sin_permiso(self):
        permisos = {'Obras': {'ver': True, 'modificar': False}}
        controller = MockController(permisos, 'Obras')
        resultado = controller.accion_modificar()
        self.assertFalse(resultado)
        controller.view.label.setText.assert_called_with('No tiene permiso para realizar la acción: modificar')

    def test_controlador_permite_accion_con_permiso(self):
        permisos = {'Obras': {'ver': True, 'modificar': True}}
        controller = MockController(permisos, 'Obras')
        resultado = controller.accion_modificar()
        self.assertTrue(resultado)
        controller.view.label.setText.assert_not_called()

if __name__ == '__main__':
    unittest.main()
