"""
FLUJO PASO A PASO DEL MÓDULO COMPRAS

1. Crear pedido de compra: crear_pedido(datos)
2. Agregar ítems al pedido: agregar_item_pedido(id_pedido, id_item, cantidad_solicitada, unidad)
3. Agregar detalle de pedido: agregar_detalle_pedido(datos)
4. Cargar y comparar presupuestos: agregar_presupuesto(datos), obtener_presupuestos_por_pedido(id_pedido), obtener_comparacion_presupuestos(id_pedido)
5. Aprobar pedido: aprobar_pedido(id_pedido), actualizar_estado_pedido(id_pedido, nuevo_estado)
6. Visualizar pedidos y detalles: obtener_pedidos(), obtener_todos_pedidos(), obtener_detalle_pedido(id_pedido)
7. Sincronizar con inventario: sincronizar_pedido_con_inventario(id_pedido)
8. Exportar información (si aplica): métodos de exportación en el controlador
9. Auditoría: todas las acciones relevantes quedan registradas (controlador)
10. Decorador de permisos aplicado en el controlador
11. Checklist funcional y visual cubierto
"""

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