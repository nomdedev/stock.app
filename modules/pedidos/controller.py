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
                    resultado = func(controller, *args, **kwargs)
                    detalle = f"{accion} - éxito"
                    auditoria_model.registrar_evento(usuario_id, self.modulo, accion, detalle, ip)
                    return resultado
                except Exception as e:
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
