from modules.usuarios.model import UsuariosModel
from modules.auditoria.model import AuditoriaModel
from core.logger import log_error
from functools import wraps

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

permiso_auditoria_compras = PermisoAuditoria('compras')

class ComprasController:
    def __init__(self, model, view, db_connection, usuario_actual=None):
        self.model = model
        self.view = view
        self.usuario_actual = usuario_actual
        self.usuarios_model = UsuariosModel(db_connection)
        self.auditoria_model = AuditoriaModel(db_connection)
        self.db_connection = db_connection

    def _registrar_evento_auditoria(self, accion, detalle_extra="", estado=""):
        usuario = getattr(self, 'usuario_actual', None)
        usuario_id = usuario['id'] if usuario and 'id' in usuario else None
        ip = usuario.get('ip', '') if usuario else ''
        detalle = f"{accion}{' - ' + detalle_extra if detalle_extra else ''}{' - ' + estado if estado else ''}"
        try:
            if self.auditoria_model:
                self.auditoria_model.registrar_evento(usuario_id, 'compras', accion, detalle, ip)
        except Exception as e:
            log_error(f"Error registrando evento auditoría: {e}")

    @permiso_auditoria_compras('ver')
    def ver_compras(self):
        try:
            # Implementar lógica de visualización de compras
            self._registrar_evento_auditoria('ver_compras', estado="éxito")
        except Exception as e:
            self._registrar_evento_auditoria('ver_compras', estado=f"error: {e}")
            log_error(f"Error en ver_compras: {e}")
            raise

    @permiso_auditoria_compras('crear')
    def crear_compra(self):
        try:
            # Implementar lógica de creación de compra
            self._registrar_evento_auditoria('crear_compra', estado="éxito")
        except Exception as e:
            self._registrar_evento_auditoria('crear_compra', estado=f"error: {e}")
            log_error(f"Error en crear_compra: {e}")
            raise

    @permiso_auditoria_compras('aprobar')
    def aprobar_compra(self):
        try:
            # Implementar lógica de aprobación de compra
            self._registrar_evento_auditoria('aprobar_compra', estado="éxito")
        except Exception as e:
            self._registrar_evento_auditoria('aprobar_compra', estado=f"error: {e}")
            log_error(f"Error en aprobar_compra: {e}")
            raise
