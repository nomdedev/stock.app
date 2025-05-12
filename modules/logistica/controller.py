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
                if not usuario or not usuario_model.tiene_permiso(usuario, self.modulo, accion):
                    if hasattr(controller, 'view') and hasattr(controller.view, 'label'):
                        controller.view.label.setText(f"No tiene permiso para realizar la acción: {accion}")
                    return None
                resultado = func(controller, *args, **kwargs)
                auditoria_model.registrar_evento(usuario, self.modulo, accion)
                return resultado
            return wrapper
        return decorador

permiso_auditoria_logistica = PermisoAuditoria('logistica')

class LogisticaController:
    def __init__(self, model, view, db_connection, usuarios_model, usuario_actual=None):
        self.model = model
        self.view = view
        self.usuario_actual = usuario_actual
        self.usuarios_model = usuarios_model
        self.auditoria_model = AuditoriaModel(db_connection)

    @permiso_auditoria_logistica('ver')
    def ver_entregas(self):
        # Implementar lógica de visualización de entregas
        pass

    @permiso_auditoria_logistica('editar')
    def editar_entrega(self):
        # Implementar lógica de edición de entrega
        pass

    @permiso_auditoria_logistica('firmar')
    def firmar_entrega(self):
        # Implementar lógica de firma de entrega
        pass

    @permiso_auditoria_logistica('reprogramar')
    def reprogramar_entrega(self):
        # Implementar lógica de reprogramación de entrega
        pass
