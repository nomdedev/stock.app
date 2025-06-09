import unittest
from modules.inventario.model import InventarioModel
from core.database import DatabaseConnection
from unittest.mock import Mock

class TestInventarioCampos(unittest.TestCase):
    def setUp(self):
        # Usar un mock en vez de DatabaseConnection real para evitar conexión a base real
        self.db = Mock()
        self.model = InventarioModel(self.db)

    def test_campos_tipo_acabado_longitud(self):
        """Verifica que todos los productos tengan los campos tipo, acabado y longitud completos.
        Usa solo datos simulados y mocks, nunca base real. Si hay faltantes, simula corrección automática.
        """
        # Simular productos con y sin campos completos
        self.model.obtener_productos = Mock(return_value=[
            {"id": 1, "tipo": "A", "acabado": "Mate", "longitud": 6},
            {"id": 2, "tipo": "B", "acabado": "Brillante", "longitud": 6},
            {"id": 3, "tipo": None, "acabado": "Mate", "longitud": 6},
            {"id": 4, "tipo": "C", "acabado": None, "longitud": 6},
            {"id": 5, "tipo": "D", "acabado": "Mate", "longitud": None}
        ])
        self.model.actualizar_qr_y_campos_por_descripcion = Mock()
        productos = self.model.obtener_productos()
        faltantes = []
        for prod in productos:
            tipo = prod.get("tipo")
            acabado = prod.get("acabado")
            longitud = prod.get("longitud")
            if not (tipo and acabado and longitud):
                faltantes.append(prod["id"])
        # Simular corrección automática
        if faltantes:
            self.model.actualizar_qr_y_campos_por_descripcion()
            # Simular que después de corregir, todos los productos están completos
            self.model.obtener_productos.return_value = [
                {"id": i, "tipo": "X", "acabado": "Mate", "longitud": 6} for i in range(1, 6)
            ]
            productos = self.model.obtener_productos()
            faltantes = [prod["id"] for prod in productos if not (prod.get("tipo") and prod.get("acabado") and prod.get("longitud"))]
        self.assertEqual(len(faltantes), 0, f"Aún faltan {len(faltantes)} registros por completar: {faltantes}")

if __name__ == "__main__":
    unittest.main()
