class PedidosModel:
    def __init__(self, db_connection):
        self.db = InventarioDatabaseConnection()

    def obtener_pedidos(self):
        query = "SELECT * FROM pedidos"
        return self.db.ejecutar_query(query)

    def crear_pedido(self, datos):
        query = "INSERT INTO pedidos (cliente, producto, cantidad, fecha) VALUES (?, ?, ?, ?)"
        self.db.ejecutar_query(query, datos)

    def obtener_detalle_pedido(self, id_pedido):
        query = "SELECT * FROM detalle_pedido WHERE id_pedido = ?"
        return self.db.ejecutar_query(query, (id_pedido,))

    def agregar_detalle_pedido(self, datos):
        query = """
        INSERT INTO detalle_pedido (id_pedido, id_item, cantidad_solicitada, unidad, justificacion)
        VALUES (?, ?, ?, ?, ?)
        """
        self.db.ejecutar_query(query, datos)

    def obtener_presupuestos_por_pedido(self, id_pedido):
        query = "SELECT * FROM presupuestos WHERE id_pedido = ?"
        return self.db.ejecutar_query(query, (id_pedido,))

    def agregar_presupuesto(self, datos):
        query = """
        INSERT INTO presupuestos (id_pedido, proveedor, fecha_recepcion, archivo_adjunto, comentarios, precio_total, seleccionado)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        self.db.ejecutar_query(query, datos)

    def actualizar_estado_pedido(self, id_pedido, nuevo_estado):
        query = "UPDATE pedidos_compra SET estado = ? WHERE id = ?"
        self.db.ejecutar_query(query, (nuevo_estado, id_pedido))
