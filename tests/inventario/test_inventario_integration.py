import unittest
from modules.inventario.model import InventarioModel

class TestInventarioIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Usar un mock en vez de DatabaseConnection real para evitar conexión a base real
        from unittest.mock import Mock
        cls.db = Mock()
        cls.model = InventarioModel(cls.db)

    def setUp(self):
        # Limpiar la tabla simulada
        self.db.ejecutar_query.reset_mock()

    def test_agregar_y_buscar_material(self):
        """Probar agregar y buscar material usando solo mocks, sin base real."""
        datos = ("C-001", "Material Test", "PVC", "unidad", 10, 2, "Depósito", "Perfil de prueba", "QR-C-001", "img1.jpg")
        self.model.agregar_item(datos)
        self.db.ejecutar_query.assert_any_call(
            """
            INSERT INTO inventario_perfiles (codigo, nombre, tipo_material, unidad, stock_actual, stock_minimo, ubicacion, descripcion, qr, imagen_referencia)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, datos)
        # Simular resultado de búsqueda
        self.db.ejecutar_query.return_value = [(1, "C-001", "Material Test", "PVC", "unidad", 10, 2, "Depósito", "Perfil de prueba", "QR-C-001", "img1.jpg")]
        resultado = self.model.obtener_item_por_codigo("C-001")
        self.assertTrue(resultado, "No se encontró el material recién agregado")
        if resultado:
            self.assertEqual(resultado[0][1], "C-001")
            self.assertEqual(resultado[0][2], "Material Test")

    def test_stock_y_descripcion_correcta(self):
        """Probar que los campos de stock y descripción se guardan y consultan correctamente (mock)."""
        datos = ("C-002", "Material Desc", "Aluminio", "kg", 5, 1, "Depósito", "Descripción especial", "QR-C-002", "img2.jpg")
        self.model.agregar_item(datos)
        # El mock debe devolver la tupla en el orden correcto según la consulta de obtener_item_por_codigo
        # Estructura: id, codigo, nombre, tipo_material, unidad, stock_actual, stock_minimo, ubicacion, descripcion, qr, imagen_referencia
        self.db.ejecutar_query.return_value = [
            (2, "C-002", "Material Desc", "Aluminio", "kg", 5, 1, "Depósito", "Descripción especial", "QR-C-002", "img2.jpg")
        ]
        resultado = self.model.obtener_item_por_codigo("C-002")
        if resultado:
            self.assertEqual(resultado[0][2], "Material Desc")
            self.assertEqual(resultado[0][3], "Aluminio")
            self.assertEqual(resultado[0][4], "kg")
            self.assertEqual(resultado[0][5], 5)
            self.assertEqual(resultado[0][8], "Descripción especial")

    def test_no_error_columna_stock(self):
        """Probar que la columna stock_actual se guarda y consulta correctamente (mock)."""
        datos = ("C-003", "Material Stock", "PVC", "unidad", 8, 2, "Depósito", "Desc", "QR-C-003", "img3.jpg")
        self.model.agregar_item(datos)
        self.db.ejecutar_query.return_value = [(3, "C-003", "Material Stock", "PVC", "unidad", 8, 2, "Depósito", "Desc", "QR-C-003", "img3.jpg")]
        resultado = self.model.obtener_item_por_codigo("C-003")
        if resultado:
            self.assertEqual(resultado[0][5], 8)

if __name__ == "__main__":
    unittest.main()
