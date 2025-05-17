from modules.usuarios.model import UsuariosModel
from modules.auditoria.model import AuditoriaModel
from functools import wraps

class PermisoAuditoria:
    def __init__(self, modulo):
        self.modulo = modulo
    def __call__(self, accion):
        def decorador(func):
            @wraps(func)
            def wrapper(controller, *args, **kwargs):
                usuario_model = getattr(controller, 'usuarios_model', UsuariosModel())
                auditoria_model = getattr(controller, 'auditoria_model', AuditoriaModel())
                usuario = getattr(controller, 'usuario_actual', None)
                ip = usuario.get('ip', '') if usuario else ''
                if not usuario or not usuario_model.tiene_permiso(usuario, self.modulo, accion):
                    if hasattr(controller, 'view') and hasattr(controller.view, 'label'):
                        controller.view.label.setText(f"No tiene permiso para realizar la acción: {accion}")
                    if auditoria_model:
                        auditoria_model.registrar_evento(usuario if usuario else {'id': None}, self.modulo, f"{accion} - denegado", ip_origen=ip)
                    return None
                try:
                    resultado = func(controller, *args, **kwargs)
                    auditoria_model.registrar_evento(usuario, self.modulo, f"{accion} - éxito", ip_origen=ip)
                    return resultado
                except Exception as e:
                    auditoria_model.registrar_evento(usuario, self.modulo, f"{accion} - error: {e}", ip_origen=ip)
                    raise
            return wrapper
        return decorador

permiso_auditoria_compras = PermisoAuditoria('compras')

class ComprasController:
    def __init__(self, model, view, usuario_actual=None):
        self.model = model
        self.view = view
        self.usuario_actual = usuario_actual
        self.usuarios_model = UsuariosModel()
        self.auditoria_model = AuditoriaModel()

    @permiso_auditoria_compras('ver')
    def ver_compras(self):
        usuario = getattr(self, 'usuario_actual', None)
        ip = usuario.get('ip', '') if usuario else ''
        try:
            # Implementar lógica de visualización de compras
            if hasattr(self, 'auditoria_model'):
                self.auditoria_model.registrar_evento(usuario, 'compras', 'ver_compras', ip_origen=ip, resultado="éxito")
        except Exception as e:
            if hasattr(self, 'auditoria_model'):
                self.auditoria_model.registrar_evento(usuario, 'compras', 'ver_compras', ip_origen=ip, resultado=f"error: {e}")
            raise

    @permiso_auditoria_compras('crear')
    def crear_compra(self):
        usuario = getattr(self, 'usuario_actual', None)
        ip = usuario.get('ip', '') if usuario else ''
        try:
            # Implementar lógica de creación de compra
            if hasattr(self, 'auditoria_model'):
                self.auditoria_model.registrar_evento(usuario, 'compras', 'crear_compra', ip_origen=ip, resultado="éxito")
        except Exception as e:
            if hasattr(self, 'auditoria_model'):
                self.auditoria_model.registrar_evento(usuario, 'compras', 'crear_compra', ip_origen=ip, resultado=f"error: {e}")
            raise

    @permiso_auditoria_compras('aprobar')
    def aprobar_compra(self):
        usuario = getattr(self, 'usuario_actual', None)
        ip = usuario.get('ip', '') if usuario else ''
        try:
            # Implementar lógica de aprobación de compra
            if hasattr(self, 'auditoria_model'):
                self.auditoria_model.registrar_evento(usuario, 'compras', 'aprobar_compra', ip_origen=ip, resultado="éxito")
        except Exception as e:
            if hasattr(self, 'auditoria_model'):
                self.auditoria_model.registrar_evento(usuario, 'compras', 'aprobar_compra', ip_origen=ip, resultado=f"error: {e}")
            raise
