import unittest
from modules.inventario.model import InventarioModel
from core.database import DatabaseConnection

class TestInventarioIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = DatabaseConnection()
        cls.db.conectar_a_base("inventario")
        cls.model = InventarioModel(cls.db)

    def setUp(self):
        # Limpiar la tabla solo si existe
        try:
            self.db.ejecutar_query("DELETE FROM inventario_perfiles")
        except Exception as e:
            self.fail(f"No se pudo limpiar la tabla inventario_perfiles: {e}")

    def test_agregar_y_buscar_material(self):
        datos = ("C-001", "Material Test", "PVC", "unidad", 10, 2, "Depósito", "Perfil de prueba", "QR-C-001", "img1.jpg")
        try:
            self.model.agregar_item(datos)
        except Exception as e:
            self.fail(f"Error al agregar material: {e}")
        resultado = self.model.obtener_item_por_codigo("C-001")
        self.assertTrue(resultado, "No se encontró el material recién agregado")
        # Estructura moderna: id, codigo, nombre, tipo_material, unidad, stock_actual, stock_minimo, ubicacion, descripcion, qr, imagen_referencia
        self.assertEqual(resultado[0][1], "C-001")  # codigo
        self.assertEqual(resultado[0][2], "Material Test")  # nombre

    def test_stock_y_descripcion_correcta(self):
        datos = ("C-002", "Material Desc", "Aluminio", "kg", 5, 1, "Depósito", "Descripción especial", "QR-C-002", "img2.jpg")
        self.model.agregar_item(datos)
        resultado = self.model.obtener_item_por_codigo("C-002")
        self.assertEqual(resultado[0][2], "Material Desc")  # nombre
        self.assertEqual(resultado[0][3], "Aluminio")  # tipo_material
        self.assertEqual(resultado[0][4], "kg")  # unidad
        self.assertEqual(resultado[0][5], 5)  # stock_actual
        self.assertEqual(resultado[0][7], "Descripción especial")  # descripcion

    def test_no_error_columna_stock(self):
        datos = ("C-003", "Material Stock", "PVC", "unidad", 8, 2, "Depósito", "Desc", "QR-C-003", "img3.jpg")
        self.model.agregar_item(datos)
        resultado = self.model.obtener_item_por_codigo("C-003")
        self.assertEqual(resultado[0][5], 8)  # stock_actual

if __name__ == "__main__":
    unittest.main()
