import logging
from core.database import PedidosDatabaseConnection

class PedidosModel:
    """
    Modelo de Pedidos que utiliza PedidosDatabaseConnection (hereda de BaseDatabaseConnection) para conexión persistente y segura.
    """
    def __init__(self, db_connection=None):
        self.db = db_connection or PedidosDatabaseConnection()
        self.logger = logging.getLogger(__name__)

    def obtener_pedidos(self):
        query = "SELECT * FROM pedidos"
        return self.db.ejecutar_query(query)

    def insertar_pedido(self, obra, fecha, materiales, observaciones):
        query = (
            "INSERT INTO pedidos (obra, fecha, materiales, observaciones, estado) "
            "VALUES (?, ?, ?, ?, ?)"
        )
        parametros = (obra, fecha, materiales, observaciones, "Pendiente")
        try:
            self.db.ejecutar_query(query, parametros)
            self.logger.info(f"Pedido insertado correctamente: {parametros}")
        except Exception as e:
            self.logger.error(f"Error al insertar pedido: {e}")
            raise

    def eliminar_pedido(self, pedido_id):
        query = "DELETE FROM pedidos WHERE id = ?"
        parametros = (pedido_id,)
        self.db.ejecutar_query(query, parametros)

    def actualizar_estado_pedido(self, pedido_id, estado):
        query = "UPDATE pedidos SET estado = ? WHERE id = ?"
        parametros = (estado, pedido_id)
        self.db.ejecutar_query(query, parametros)
