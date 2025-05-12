from core.database import PedidosDatabaseConnection  # Importar la clase correcta

class PedidosModel:
    def __init__(self, db_connection):
        self.db = db_connection

    def obtener_pedidos(self):
        query = "SELECT * FROM pedidos"
        return self.db.ejecutar_query(query)

    def obtener_todos_pedidos(self):
        """Obtiene todos los pedidos de la base de datos."""
        try:
            query = "SELECT id, cliente, producto, cantidad, fecha, estado FROM pedidos"
            return self.db.ejecutar_query(query)
        except Exception as e:
            print(f"Error al obtener pedidos: {e}")
            return []

    def crear_pedido(self, datos):
        try:
            query = "INSERT INTO pedidos (cliente, producto, cantidad, fecha) VALUES (?, ?, ?, ?)"
            self.db.ejecutar_query(query, datos)
        except Exception as e:
            print(f"Error al crear pedido: {e}")
            raise

    def obtener_detalle_pedido(self, id_pedido):
        try:
            query = "SELECT * FROM detalle_pedido WHERE id_pedido = ?"
            return self.db.ejecutar_query(query, (id_pedido,))
        except Exception as e:
            print(f"Error al obtener detalle del pedido: {e}")
            return []

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
        try:
            query = """
            INSERT INTO presupuestos (id_pedido, proveedor, fecha_recepcion, archivo_adjunto, comentarios, precio_total, seleccionado)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            self.db.ejecutar_query(query, datos)
        except Exception as e:
            print(f"Error al agregar presupuesto: {e}")
            raise

    def actualizar_estado_pedido(self, id_pedido, nuevo_estado):
        query = "UPDATE pedidos_compra SET estado = ? WHERE id = ?"
        self.db.ejecutar_query(query, (nuevo_estado, id_pedido))
