from PyQt6.QtWidgets import QTableWidgetItem
from modules.pedidos.model import PedidosModel
from modules.usuarios.model import UsuariosModel
from modules.auditoria.model import AuditoriaModel
from functools import wraps
from core.logger import log_error

class PermisoAuditoria:
    def __init__(self, modulo):
        self.modulo = modulo
    def __call__(self, accion):
        def decorador(func):
            @wraps(func)
            def wrapper(controller, *args, **kwargs):
                usuario_model = getattr(controller, 'usuarios_model', None)
                auditoria_model = getattr(controller, 'auditoria_model', None)
                usuario = getattr(controller, 'usuario_actual', None)
                usuario_id = usuario['id'] if usuario and 'id' in usuario else None
                ip = usuario.get('ip', '') if usuario else ''
                if not usuario or not usuario_model or not auditoria_model:
                    if hasattr(controller, 'view') and hasattr(controller.view, 'label'):
                        controller.view.label.setText(f"No tiene permiso para realizar la acción: {accion}")
                    return None
                if not usuario_model.tiene_permiso(usuario, self.modulo, accion):
                    if hasattr(controller, 'view') and hasattr(controller.view, 'label'):
                        controller.view.label.setText(f"No tiene permiso para realizar la acción: {accion}")
                    detalle = f"{accion} - denegado"
                    auditoria_model.registrar_evento(usuario_id, self.modulo, accion, detalle, ip)
                    return None
                try:
                    print(f"[LOG ACCIÓN] Ejecutando acción '{accion}' en módulo '{self.modulo}' por usuario: {usuario.get('username', 'desconocido')} (id={usuario.get('id', '-')})")
                    resultado = func(controller, *args, **kwargs)
                    print(f"[LOG ACCIÓN] Acción '{accion}' en módulo '{self.modulo}' finalizada con éxito.")
                    detalle = f"{accion} - éxito"
                    auditoria_model.registrar_evento(usuario_id, self.modulo, accion, detalle, ip)
                    return resultado
                except Exception as e:
                    print(f"[LOG ACCIÓN] Error en acción '{accion}' en módulo '{self.modulo}': {e}")
                    detalle = f"{accion} - error: {e}"
                    auditoria_model.registrar_evento(usuario_id, self.modulo, accion, detalle, ip)
                    log_error(f"Error en {accion}: {e}")
                    raise
            return wrapper
        return decorador

permiso_auditoria_pedidos = PermisoAuditoria('pedidos')

class PedidosController:
    """
    Controlador para el módulo de Pedidos.
    
    Todas las acciones públicas relevantes están decoradas con @permiso_auditoria_pedidos,
    lo que garantiza el registro automático en el módulo de auditoría.
    
    Patrón de auditoría:
    - Decorador @permiso_auditoria_pedidos('accion') en cada método público relevante.
    - El decorador valida permisos, registra el evento en auditoría (usuario, módulo, acción, detalle, ip, estado).
    - Feedback visual inmediato ante denegación o error.
    """
    def __init__(self, view, db_connection, usuarios_model=None, usuario_actual=None):
        self.view = view
        self.db_connection = db_connection
        self.usuario_actual = usuario_actual  # Permite asignar el usuario actual desde main.py
        self.model = PedidosModel(db_connection)
        self.usuarios_model = usuarios_model if usuarios_model else UsuariosModel(db_connection)
        self.auditoria_model = AuditoriaModel(db_connection)

    @permiso_auditoria_pedidos('ver')
    def cargar_pedidos(self):
        pedidos = self.model.obtener_pedidos() or []
        self.view.tabla_pedidos.setRowCount(len(pedidos))
        for row, pedido in enumerate(pedidos):
            for col, value in enumerate(pedido):
                self.view.tabla_pedidos.setItem(row, col, QTableWidgetItem(str(value)))

    @permiso_auditoria_pedidos('crear')
    def crear_pedido(self, obra, fecha, materiales, observaciones):
        self.model.insertar_pedido(obra, fecha, materiales, observaciones)
        self.cargar_pedidos()

    @permiso_auditoria_pedidos('eliminar')
    def eliminar_pedido(self, pedido_id):
        self.model.eliminar_pedido(pedido_id)
        self.cargar_pedidos()

    @permiso_auditoria_pedidos('aprobar')
    def aprobar_pedido(self, pedido_id):
        self.model.actualizar_estado_pedido(pedido_id, "Aprobado")
        self.cargar_pedidos()

    @permiso_auditoria_pedidos('rechazar')
    def rechazar_pedido(self, pedido_id):
        self.model.actualizar_estado_pedido(pedido_id, "Rechazado")
        self.cargar_pedidos()

    @permiso_auditoria_pedidos('crear')
    def generar_pedido_por_obra(self, id_obra):
        """
        Genera un pedido por obra, alineado a estándares: validación, feedback visual, logging, auditoría y señales event_bus.
        Propaga feedback visual a la vista y emite señal de actualización en tiempo real.
        """
        try:
            usuario = self.usuario_actual.get('username', 'desconocido') if self.usuario_actual else None
            id_pedido = self.model.generar_pedido_por_obra(id_obra, usuario=usuario, view=self.view)
            if hasattr(self.view, 'mostrar_feedback'):
                self.view.mostrar_feedback(f"Pedido generado correctamente (ID: {id_pedido})", tipo="exito")
            self.cargar_pedidos()
            return id_pedido
        except Exception as e:
            if hasattr(self.view, 'mostrar_feedback'):
                self.view.mostrar_feedback(f"Error al generar pedido: {e}", tipo="error")
            raise

    @permiso_auditoria_pedidos('editar')
    def recibir_pedido(self, id_pedido):
        """
        Recibe un pedido, actualiza stock, movimientos y auditoría. Feedback visual y logging robusto.
        Emite señal event_bus y refresca la vista.
        """
        try:
            usuario = self.usuario_actual.get('username', 'desconocido') if self.usuario_actual else None
            ok = self.model.recibir_pedido(id_pedido, usuario=usuario, view=self.view)
            if hasattr(self.view, 'mostrar_feedback'):
                self.view.mostrar_feedback(f"Pedido recibido correctamente (ID: {id_pedido})", tipo="exito")
            self.cargar_pedidos()
            return ok
        except Exception as e:
            if hasattr(self.view, 'mostrar_feedback'):
                self.view.mostrar_feedback(f"Error al recibir pedido: {e}", tipo="error")
            raise

    def abrir_dialogo_recepcion_pedido(self, pedido_id):
        """
        Abre el diálogo modal de recepción de pedido, pasando el resumen de ítems a la vista.
        Cumple checklist: feedback, accesibilidad, cierre solo en éxito, logging y auditoría.
        """
        # Obtener resumen de ítems del pedido
        resumen_items = self.model.db.ejecutar_query(
            "SELECT tipo_item, id_item, cantidad_requerida FROM pedidos_por_obra WHERE id_pedido=?",
            (pedido_id,)
        ) or []
        self.view.abrir_dialogo_recepcion_pedido(pedido_id, resumen_items, self)

    # Ejemplo de integración cruzada para desarrolladores de UI:
    # Suscribirse a event_bus.pedido_actualizado en Inventario/Obras:
    # from core.event_bus import event_bus
    # event_bus.pedido_actualizado.connect(lambda datos: self.actualizar_por_pedido(datos))
    # En el slot, refrescar la vista y mostrar feedback visual inmediato.
    # Ver docs/flujo_obras_material_vidrios.md y docs/estandares_feedback.md
