class ComprasModel:
    def __init__(self, db):
        self.db = db

    def obtener_comparacion_presupuestos(self, id_pedido):
        query = """
        SELECT proveedor, precio_total, comentarios
        FROM presupuestos
        WHERE id_pedido = ?
        """
        presupuestos = self.db.ejecutar_query(query, (id_pedido,))
        if not presupuestos:
            return "No se encontraron presupuestos para este pedido."

        return presupuestos

    def crear_pedido(self, solicitado_por, prioridad, observaciones):
        query = "INSERT INTO pedidos_compra (solicitado_por, prioridad, observaciones) VALUES (?, ?, ?)"
        self.db.ejecutar_query(query, (solicitado_por, prioridad, observaciones))

    def agregar_item_pedido(self, id_pedido, id_item, cantidad_solicitada, unidad):
        query = "INSERT INTO detalle_pedido (id_pedido, id_item, cantidad_solicitada, unidad) VALUES (?, ?, ?, ?)"
        self.db.ejecutar_query(query, (id_pedido, id_item, cantidad_solicitada, unidad))

    def aprobar_pedido(self, id_pedido):
        query = "UPDATE pedidos_compra SET estado = 'aprobado' WHERE id = ?"
        self.db.ejecutar_query(query, (id_pedido,))