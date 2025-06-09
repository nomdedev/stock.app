import unittest
from modules.pedidos.model import PedidosModel
from modules.pedidos.controller import PedidosController
from modules.pedidos.view import PedidosView
from unittest.mock import MagicMock

class TestPedidos(unittest.TestCase):

    def setUp(self):
        self.view = PedidosView()
        self.model = PedidosModel()
        self.controller = PedidosController(self.view)
        self.model.obtener_pedidos = MagicMock(return_value=[
            (1, "Obra A", "2025-05-08", "Pendiente", "Sin observaciones"),
            (2, "Obra B", "2025-05-07", "Aprobado", "Entrega urgente")
        ])

    def test_cargar_pedidos(self):
        self.controller.cargar_pedidos()
        self.assertEqual(self.view.tabla_pedidos.rowCount(), 2)
        self.assertEqual(self.view.tabla_pedidos.item(0, 1).text(), "Obra A")

    def test_crear_pedido(self):
        self.model.insertar_pedido = MagicMock()
        self.controller.crear_pedido("Obra C", "2025-05-09", "Material X", "Sin observaciones")
        self.model.insertar_pedido.assert_called_once_with("Obra C", "2025-05-09", "Material X", "Sin observaciones")

    def test_eliminar_pedido(self):
        self.model.eliminar_pedido = MagicMock()
        self.controller.eliminar_pedido(1)
        self.model.eliminar_pedido.assert_called_once_with(1)

    def test_aprobar_pedido(self):
        self.model.actualizar_estado_pedido = MagicMock()
        self.controller.aprobar_pedido(1)
        self.model.actualizar_estado_pedido.assert_called_once_with(1, "Aprobado")

    def test_rechazar_pedido(self):
        self.model.actualizar_estado_pedido = MagicMock()
        self.controller.rechazar_pedido(1)
        self.model.actualizar_estado_pedido.assert_called_once_with(1, "Rechazado")

if __name__ == "__main__":
    unittest.main()
