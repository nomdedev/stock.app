from modules.pedidos.model import PedidosModel

class PedidosController:
    def __init__(self, view, db_connection):
        self.view = view
        self.model = PedidosModel(db_connection)

    def cargar_pedidos(self):
        pedidos = self.model.obtener_pedidos()
        self.view.tabla_pedidos.setRowCount(len(pedidos))
        for row, pedido in enumerate(pedidos):
            for col, value in enumerate(pedido):
                self.view.tabla_pedidos.setItem(row, col, QTableWidgetItem(str(value)))

    def crear_pedido(self, obra, fecha, materiales, observaciones):
        self.model.insertar_pedido(obra, fecha, materiales, observaciones)
        self.cargar_pedidos()

    def eliminar_pedido(self, pedido_id):
        self.model.eliminar_pedido(pedido_id)
        self.cargar_pedidos()

    def aprobar_pedido(self, pedido_id):
        self.model.actualizar_estado_pedido(pedido_id, "Aprobado")
        self.cargar_pedidos()

    def rechazar_pedido(self, pedido_id):
        self.model.actualizar_estado_pedido(pedido_id, "Rechazado")
        self.cargar_pedidos()
