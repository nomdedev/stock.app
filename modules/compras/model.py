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

import logging
from modules.auditoria.helpers import _registrar_evento_auditoria

class ComprasModel:
    def __init__(self, db):
        self.db = db
        self.logger = logging.getLogger(__name__)

    def obtener_comparacion_presupuestos(self, id_pedido, view=None, usuario=None):
        try:
            query = """
            SELECT proveedor, precio_total, comentarios
            FROM presupuestos
            WHERE id_pedido = ?
            """
            presupuestos = self.db.ejecutar_query(query, (id_pedido,))
            if not presupuestos:
                msg = "No se encontraron presupuestos para este pedido."
                if view and hasattr(view, 'mostrar_mensaje'):
                    view.mostrar_mensaje(msg, tipo='info')
                return msg
            return presupuestos
        except Exception as e:
            self.logger.error(f"Error al obtener comparación de presupuestos: {e}")
            _registrar_evento_auditoria(usuario, "Compras", f"Error al obtener comparación de presupuestos: {e}")
            if view and hasattr(view, 'mostrar_mensaje'):
                view.mostrar_mensaje(f"Error: {e}", tipo='error')
            raise

    def crear_pedido(self, solicitado_por, prioridad, observaciones, usuario=None, view=None):
        try:
            if not solicitado_por or not prioridad:
                raise ValueError("Faltan datos obligatorios para crear el pedido.")
            query = "INSERT INTO pedidos_compra (solicitado_por, prioridad, observaciones) VALUES (?, ?, ?)"
            with self.db.transaction():
                self.db.ejecutar_query(query, (solicitado_por, prioridad, observaciones))
                _registrar_evento_auditoria(usuario, "Compras", f"Creó pedido de compra: {solicitado_por}, prioridad: {prioridad}")
            self.logger.info(f"Pedido de compra creado por {solicitado_por} (prioridad: {prioridad})")
            if view and hasattr(view, 'mostrar_mensaje'):
                view.mostrar_mensaje("Pedido creado correctamente", tipo='success')
        except Exception as e:
            self.logger.error(f"Error al crear pedido: {e}")
            _registrar_evento_auditoria(usuario, "Compras", f"Error al crear pedido: {e}")
            if view and hasattr(view, 'mostrar_mensaje'):
                view.mostrar_mensaje(f"Error al crear pedido: {e}", tipo='error')
            raise

    def agregar_item_pedido(self, id_pedido, id_item, cantidad_solicitada, unidad, usuario=None, view=None):
        try:
            if not id_pedido or not id_item or not cantidad_solicitada:
                raise ValueError("Datos incompletos para agregar ítem al pedido.")
            query = "INSERT INTO detalle_pedido (id_pedido, id_item, cantidad_solicitada, unidad) VALUES (?, ?, ?, ?)"
            with self.db.transaction():
                self.db.ejecutar_query(query, (id_pedido, id_item, cantidad_solicitada, unidad))
                _registrar_evento_auditoria(usuario, "Compras", f"Agregó ítem {id_item} (cant: {cantidad_solicitada}) a pedido {id_pedido}")
            self.logger.info(f"Ítem {id_item} agregado a pedido {id_pedido}")
            if view and hasattr(view, 'mostrar_mensaje'):
                view.mostrar_mensaje("Ítem agregado correctamente", tipo='success')
        except Exception as e:
            self.logger.error(f"Error al agregar ítem al pedido: {e}")
            _registrar_evento_auditoria(usuario, "Compras", f"Error al agregar ítem al pedido: {e}")
            if view and hasattr(view, 'mostrar_mensaje'):
                view.mostrar_mensaje(f"Error al agregar ítem: {e}", tipo='error')
            raise

    def aprobar_pedido(self, id_pedido, usuario=None, view=None):
        try:
            if not id_pedido:
                raise ValueError("ID de pedido requerido para aprobar.")
            query = "UPDATE pedidos_compra SET estado = 'aprobado' WHERE id = ?"
            with self.db.transaction():
                self.db.ejecutar_query(query, (id_pedido,))
                _registrar_evento_auditoria(usuario, "Compras", f"Aprobó pedido {id_pedido}")
            self.logger.info(f"Pedido {id_pedido} aprobado")
            if view and hasattr(view, 'mostrar_mensaje'):
                view.mostrar_mensaje("Pedido aprobado correctamente", tipo='success')
        except Exception as e:
            self.logger.error(f"Error al aprobar pedido: {e}")
            _registrar_evento_auditoria(usuario, "Compras", f"Error al aprobar pedido: {e}")
            if view and hasattr(view, 'mostrar_mensaje'):
                view.mostrar_mensaje(f"Error al aprobar pedido: {e}", tipo='error')
            raise