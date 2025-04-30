import os
import unittest
from unittest.mock import Mock
from modules.inventario.model import InventarioModel

class MockDB:
    def ejecutar_query(self, query, params=None):
        if "SELECT * FROM inventario_items" in query:
            return [
                (1, "123456.789", "Material A", "PVC", "unidad", 100, 10, "Almacén 1", "Descripción A", "QR123", "imagen_a.jpg"),
                (2, "987654.321", "Material B", "Aluminio", "kg", 50, 5, "Almacén 2", "Descripción B", "QR987", "imagen_b.jpg")
            ]
        return []

class TestInventarioModel(unittest.TestCase):

    def setUp(self):
        self.mock_db = Mock()
        self.inventario_model = InventarioModel(self.mock_db)

    def test_generar_qr(self):
        # Simular generación de QR
        id_item = 1
        self.mock_db.ejecutar_query.side_effect = [
            [("123456.789",)],  # Resultado de la primera consulta (SELECT)
            None  # Resultado de la segunda consulta (UPDATE)
        ]

        qr_code = self.inventario_model.generar_qr(id_item)

        # Verificar que ambas consultas se realizaron correctamente
        self.mock_db.ejecutar_query.assert_any_call("SELECT codigo FROM inventario_items WHERE id = ?", (id_item,))
        self.mock_db.ejecutar_query.assert_any_call("UPDATE inventario_items SET qr_code = ? WHERE id = ?", ("QR-123456.789", id_item))
        self.assertEqual(qr_code, "QR-123456.789")

    def test_exportar_inventario_excel(self):
        # Simular exportación a Excel
        self.mock_db.ejecutar_query.return_value = [
            (1, "123456.789", "Material A", "PVC", "unidad", 100, 10, "Almacén 1", "Descripción A", "QR123", "imagen_a.jpg"),
            (2, "987654.321", "Material B", "Aluminio", "kg", 50, 5, "Almacén 2", "Descripción B", "QR987", "imagen_b.jpg")
        ]

        resultado = self.inventario_model.exportar_inventario("excel")

        self.assertEqual(resultado, "Inventario exportado a Excel.")

    def test_exportar_inventario_pdf(self):
        # Simular exportación a PDF
        self.mock_db.ejecutar_query.return_value = [
            (1, "123456.789", "Material A", "PVC", "unidad", 100, 10, "Almacén 1", "Descripción A", "QR123", "imagen_a.jpg"),
            (2, "987654.321", "Material B", "Aluminio", "kg", 50, 5, "Almacén 2", "Descripción B", "QR987", "imagen_b.jpg")
        ]

        resultado = self.inventario_model.exportar_inventario("pdf")

        self.assertEqual(resultado, "Inventario exportado a PDF.")

def test_exportar_inventario():
    db = MockDB()
    model = InventarioModel()
    model.db = db

    # Caso 1: Exportar a Excel
    resultado_excel = model.exportar_inventario("excel")
    assert resultado_excel == "Inventario exportado a Excel.", f"Error: {resultado_excel}"
    assert os.path.exists("inventario.xlsx"), "El archivo Excel no fue generado."
    os.remove("inventario.xlsx")

    # Caso 2: Exportar a PDF
    resultado_pdf = model.exportar_inventario("pdf")
    assert resultado_pdf == "Inventario exportado a PDF.", f"Error: {resultado_pdf}"
    assert os.path.exists("inventario.pdf"), "El archivo PDF no fue generado."
    os.remove("inventario.pdf")

    # Caso 3: Formato no soportado
    resultado_invalido = model.exportar_inventario("csv")
    assert resultado_invalido == "Formato no soportado.", f"Error: {resultado_invalido}"

if __name__ == "__main__":
    try:
        test_exportar_inventario()
        print("Pruebas del módulo de inventario pasaron correctamente.")
    except AssertionError as e:
        print(f"Test fallido: {e}")
    unittest.main()
