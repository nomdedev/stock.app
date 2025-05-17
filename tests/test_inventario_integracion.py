import unittest
from unittest.mock import Mock
from modules.inventario.model import InventarioModel
from modules.inventario.view import InventarioView

class MockDBConnection:
    def __init__(self):
        self.reset()
    def reset(self):
        self.inventario_perfiles = []
        self.movimientos_stock = []
        self.reservas_materiales = []
        self.last_id = 1
    def ejecutar_query(self, query, params=None):
        if "INSERT INTO inventario_perfiles" in query:
            item = (self.last_id,) + tuple(params)
            self.inventario_perfiles.append(item)
            self.last_id += 1
            return None
        if "SELECT * FROM inventario_perfiles" in query:
            return list(self.inventario_perfiles)
        if "INSERT INTO movimientos_stock" in query:
            self.movimientos_stock.append(tuple(params))
            return None
        if "SELECT * FROM movimientos_stock" in query:
            return list(self.movimientos_stock)
        if "INSERT INTO reservas_materiales" in query:
            self.reservas_materiales.append(tuple(params))
            return None
        if "SELECT * FROM reservas_materiales" in query:
            return list(self.reservas_materiales)
        return []

class MockInventarioView:
    def __init__(self):
        self.tabla_data = []
        self.label = Mock()
    def actualizar_tabla(self, data):
        self.tabla_data = data

class TestInventarioIntegracion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mock_db = MockDBConnection()
    def setUp(self):
        self.mock_db.reset()
        self.model = InventarioModel(self.mock_db)
        self.view = MockInventarioView()
    def test_agregar_y_reflejar_item(self):
        datos = ("C-001", "Material Demo", "PVC", "unidad", 20, 5, "Almacén Central", "Descripción demo", "QR-C-001", "img_demo.jpg")
        self.model.agregar_item(datos)
        items = self.mock_db.ejecutar_query("SELECT * FROM inventario_perfiles")
        print('DEBUG items after insert:', items)
        self.assertTrue(any(i[1] == "C-001" for i in items))
        self.view.actualizar_tabla(items)
        self.assertEqual(self.view.tabla_data, items)
    def test_movimiento_y_reserva(self):
        datos = ("C-002", "Material Mov", "Aluminio", "kg", 50, 10, "Depósito", "Desc mov", "QR-C-002", "img2.jpg")
        self.model.agregar_item(datos)
        items = self.mock_db.ejecutar_query("SELECT * FROM inventario_perfiles")
        print('DEBUG items before movimiento:', items)
        id_item = items[-1][0] if items else None
        self.assertIsNotNone(id_item)
        mov = (id_item, "entrada", 10, "admin", "Ingreso inicial", "ref-001")
        self.model.registrar_movimiento(mov)
        movimientos = self.mock_db.ejecutar_query("SELECT * FROM movimientos_stock")
        print('DEBUG movimientos:', movimientos)
        self.assertTrue(any(m[0] == id_item for m in movimientos))
        reserva = (id_item, 5, "ObraX", "activa")
        self.model.registrar_reserva(reserva)
        reservas = self.mock_db.ejecutar_query("SELECT * FROM reservas_materiales")
        print('DEBUG reservas:', reservas)
        self.assertTrue(any(r[0] == id_item for r in reservas))
        self.view.actualizar_tabla(items)
        self.assertEqual(self.view.tabla_data, items)
    def test_reserva_stock_insuficiente(self):
        # Agregar un item con poco stock
        datos = ("C-003", "Material Poco Stock", "PVC", "unidad", 2, 1, "Depósito", "Desc", "QR-C-003", "img3.jpg")
        self.model.agregar_item(datos)
        items = self.mock_db.ejecutar_query("SELECT * FROM inventario_perfiles")
        items = items or []
        items = [i for i in items if i is not None]
        id_item = items[-1][0]
        stock_antes = items[-1][4] if len(items[-1]) > 4 else 0
        # Intentar reservar más de lo disponible
        with self.assertRaises(Exception) as cm:
            self.model.reservar_stock(id_item, 5, id_obra="ObraTest")
        self.assertIn("Stock insuficiente", str(cm.exception))
        # Verificar que el stock no cambió
        items_despues = self.mock_db.ejecutar_query("SELECT * FROM inventario_perfiles")
        items_despues = items_despues or []
        items_despues = [i for i in items_despues if i is not None]
        stock_despues = items_despues[-1][4] if len(items_despues[-1]) > 4 else 0
        self.assertEqual(stock_antes, stock_despues, "El stock no debe cambiar si la reserva falla")

if __name__ == "__main__":
    unittest.main()
