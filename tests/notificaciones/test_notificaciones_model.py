import unittest
from modules.notificaciones.model import NotificacionesModel

class MockDB:
    def __init__(self):
        self.last_query = None
        self.last_params = None
        self.result = []

    def ejecutar_query(self, query, params=None):
        self.last_query = query
        self.last_params = params
        return self.result

class TestNotificacionesModel(unittest.TestCase):
    def setUp(self):
        self.db = MockDB()
        self.model = NotificacionesModel(self.db)

    def test_obtener_notificaciones(self):
        self.db.result = [(1, 'hola', '2025-06-09', 'info')]
        result = self.model.obtener_notificaciones()
        self.assertEqual(result, self.db.result)
        self.assertIn('FROM notificaciones', self.db.last_query)
        self.assertIsNone(self.db.last_params)

    def test_agregar_notificacion(self):
        datos = ('mensaje', '2025-06-10', 'info')
        self.model.agregar_notificacion(datos)
        self.assertIn('INSERT INTO notificaciones', self.db.last_query)
        self.assertEqual(self.db.last_params, datos)
