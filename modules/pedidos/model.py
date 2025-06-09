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

    def generar_pedido_por_obra(self, id_obra, usuario=None, view=None):
        """
        Genera un pedido por obra, calcula faltantes y registra auditoría (helper global).
        Feedback visual y logging robusto. Cumple estándares de seguridad, feedback, logging y auditoría.
        """
        import datetime
        from modules.auditoria.helpers import _registrar_evento_auditoria
        try:
            perfiles = self.db.ejecutar_query(
                """
                SELECT p.id_perfil, pp.cantidad_reservada, p.stock_actual, p.precio_unitario
                FROM inventario_perfiles p
                JOIN perfiles_por_obra pp ON p.id_perfil = pp.id_perfil
                WHERE pp.id_obra = ?
                """, (id_obra,)) or []
            herrajes = self.db.ejecutar_query(
                """
                SELECT h.id_herraje, hh.cantidad_reservada, h.stock_actual, h.precio_unitario
                FROM herrajes h
                JOIN herrajes_por_obra hh ON h.id_herraje = hh.id_herraje
                WHERE hh.id_obra = ?
                """, (id_obra,)) or []
            vidrios = self.db.ejecutar_query(
                """
                SELECT v.id_vidrio, vv.cantidad_reservada, v.stock_actual, v.precio_unitario
                FROM vidrios v
                JOIN vidrios_por_obra vv ON v.id_vidrio = vv.id_vidrio
                WHERE vv.id_obra = ?
                """, (id_obra,)) or []
            faltantes = []
            total_estimado = 0
            for id_perfil, cant_res, stock, precio in perfiles:
                faltante = cant_res - stock
                if faltante > 0:
                    faltantes.append(("perfil", id_perfil, faltante, precio))
                    total_estimado += faltante * precio
            for id_herraje, cant_res, stock, precio in herrajes:
                faltante = cant_res - stock
                if faltante > 0:
                    faltantes.append(("herraje", id_herraje, faltante, precio))
                    total_estimado += faltante * precio
            for id_vidrio, cant_res, stock, precio in vidrios:
                faltante = cant_res - stock
                if faltante > 0:
                    faltantes.append(("vidrio", id_vidrio, faltante, precio))
                    total_estimado += faltante * precio
            if not faltantes:
                raise ValueError("No hay faltantes para pedir en esta obra.")
            fecha_emision = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with self.db.transaction(timeout=30, retries=2):
                self.db.ejecutar_query(
                    "INSERT INTO pedidos (id_obra, fecha_emision, estado, total_estimado) VALUES (?, ?, ?, ?)",
                    (id_obra, fecha_emision, "Pendiente", total_estimado)
                )
                # Obtener id_pedido recién insertado (soporte para SQLite y SQL Server)
                id_pedido_row = self.db.ejecutar_query("SELECT SCOPE_IDENTITY()")
                id_pedido = None
                if id_pedido_row and id_pedido_row[0][0]:
                    id_pedido = int(id_pedido_row[0][0])
                else:
                    id_pedido_row = self.db.ejecutar_query("SELECT last_insert_rowid()")
                    if id_pedido_row and id_pedido_row[0][0]:
                        id_pedido = int(id_pedido_row[0][0])
                if id_pedido is None:
                    raise RuntimeError("No se pudo obtener el id del pedido recién insertado.")
                for tipo, id_item, cantidad, _ in faltantes:
                    self.db.ejecutar_query(
                        "INSERT INTO pedidos_por_obra (id_pedido, id_obra, id_item, tipo_item, cantidad_requerida) VALUES (?, ?, ?, ?, ?)",
                        (id_pedido, id_obra, id_item, tipo, cantidad)
                    )
                _registrar_evento_auditoria(usuario, "Pedidos", f"Generó pedido {id_pedido} para obra {id_obra}")
            self.logger.info(f"Pedido generado correctamente (ID: {id_pedido}) para obra {id_obra}")
            if view and hasattr(view, 'mostrar_mensaje'):
                view.mostrar_mensaje(f"Pedido generado correctamente (ID: {id_pedido})", tipo='success')
            # Emitir señal de actualización en tiempo real
            try:
                from core.event_bus import event_bus
                event_bus.pedido_actualizado.emit({'id': id_pedido, 'obra': id_obra, 'usuario': usuario})
            except Exception as e:
                self.logger.warning(f"No se pudo emitir señal pedido_actualizado: {e}")
            return id_pedido
        except Exception as e:
            self.logger.warning(f"Error al generar pedido: {e}")
            _registrar_evento_auditoria(usuario, "Pedidos", f"Error al generar pedido: {e}")
            if view and hasattr(view, 'mostrar_mensaje'):
                view.mostrar_mensaje(f"Error al generar pedido: {e}", tipo='error')
            raise

    def recibir_pedido(self, id_pedido, usuario=None, view=None):
        """
        Recibe un pedido, actualiza stock, movimientos y auditoría (helper global).
        Feedback visual y logging robusto. Cumple estándares de seguridad, feedback, logging y auditoría.
        """
        import datetime
        from modules.auditoria.helpers import _registrar_evento_auditoria
        try:
            pedido = self.db.ejecutar_query("SELECT estado FROM pedidos WHERE id_pedido=?", (id_pedido,))
            if not pedido:
                raise ValueError("Pedido no existe")
            estado = pedido[0][0]
            if estado == "Recibido":
                raise ValueError("Pedido ya recibido")
            items = self.db.ejecutar_query("SELECT tipo_item, id_item, cantidad_requerida FROM pedidos_por_obra WHERE id_pedido=?", (id_pedido,)) or []
            fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with self.db.transaction(timeout=30, retries=2):
                self.db.ejecutar_query("UPDATE pedidos SET estado='Recibido' WHERE id_pedido=?", (id_pedido,))
                for tipo, id_item, cantidad in items:
                    if tipo == "perfil":
                        self.db.ejecutar_query("UPDATE inventario_perfiles SET stock_actual = stock_actual + ? WHERE id_perfil = ?", (cantidad, id_item))
                        self.db.ejecutar_query("INSERT INTO movimientos_stock (id_perfil, tipo_movimiento, cantidad, fecha, usuario) VALUES (?, 'Ingreso', ?, ?, ?)", (id_item, cantidad, fecha, usuario or ""))
                    elif tipo == "herraje":
                        self.db.ejecutar_query("UPDATE herrajes SET stock_actual = stock_actual + ? WHERE id_herraje = ?", (cantidad, id_item))
                        self.db.ejecutar_query("INSERT INTO movimientos_herrajes (id_herraje, tipo_movimiento, cantidad, fecha, usuario) VALUES (?, 'Ingreso', ?, ?, ?)", (id_item, cantidad, fecha, usuario or ""))
                    elif tipo == "vidrio":
                        self.db.ejecutar_query("UPDATE vidrios SET stock_actual = stock_actual + ? WHERE id_vidrio = ?", (cantidad, id_item))
                        self.db.ejecutar_query("INSERT INTO movimientos_vidrios (id_vidrio, tipo_movimiento, cantidad, fecha, usuario) VALUES (?, 'Ingreso', ?, ?, ?)", (id_item, cantidad, fecha, usuario or ""))
                _registrar_evento_auditoria(usuario, "Pedidos", f"Recibió pedido {id_pedido}")
            self.logger.info(f"Pedido recibido correctamente (ID: {id_pedido})")
            if view and hasattr(view, 'mostrar_mensaje'):
                view.mostrar_mensaje(f"Pedido recibido correctamente (ID: {id_pedido})", tipo='success')
            # Emitir señal de actualización en tiempo real
            try:
                from core.event_bus import event_bus
                event_bus.pedido_actualizado.emit({'id': id_pedido, 'usuario': usuario})
            except Exception as e:
                self.logger.warning(f"No se pudo emitir señal pedido_actualizado: {e}")
            return True
        except Exception as e:
            self.logger.warning(f"Error al recibir pedido: {e}")
            _registrar_evento_auditoria(usuario, "Pedidos", f"Error al recibir pedido: {e}")
            if view and hasattr(view, 'mostrar_mensaje'):
                view.mostrar_mensaje(f"Error al recibir pedido: {e}", tipo='error')
            raise
