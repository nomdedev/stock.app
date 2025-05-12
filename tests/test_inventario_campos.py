import unittest
from modules.inventario.model import InventarioModel
from core.database import DatabaseConnection

class TestInventarioCampos(unittest.TestCase):
    def setUp(self):
        self.db = DatabaseConnection()
        self.model = InventarioModel(self.db)

    def test_campos_tipo_acabado_longitud(self):
        # Obtener todos los productos
        productos = self.model.obtener_productos()
        faltantes = []
        for prod in productos:
            tipo = prod.get("tipo")
            acabado = prod.get("acabado")
            longitud = prod.get("longitud")
            if not (tipo and acabado and longitud):
                faltantes.append(prod["id"])
        print(f"Faltan completar: {len(faltantes)} registros.")
        # Si hay faltantes, corregir
        if faltantes:
            self.model.actualizar_qr_y_campos_por_descripcion()
            # Volver a chequear
            productos = self.model.obtener_productos()
            faltantes = [prod["id"] for prod in productos if not (prod.get("tipo") and prod.get("acabado") and prod.get("longitud"))]
        self.assertEqual(len(faltantes), 0, f"Aún faltan {len(faltantes)} registros por completar: {faltantes}")

if __name__ == "__main__":
    unittest.main()
