from datetime import datetime
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

permiso_auditoria_notificaciones = PermisoAuditoria('notificaciones')

class NotificacionesController:
    def __init__(self, model, view, db_connection, usuarios_model, usuario_actual=None):
        self.model = model
        self.view = view
        self.usuario_actual = usuario_actual
        self.usuarios_model = usuarios_model
        self.auditoria_model = AuditoriaModel(db_connection)
        self.view.boton_agregar.clicked.connect(self.agregar_notificacion)

    @permiso_auditoria_notificaciones('editar')
    def agregar_notificacion(self):
        mensaje = self.view.mensaje_input.text()
        fecha = self.view.fecha_input.text()
        tipo = self.view.tipo_input.text()

        if mensaje and fecha and tipo:
            self.model.agregar_notificacion((mensaje, fecha, tipo))
            self.view.label.setText("Notificación agregada exitosamente.")
        else:
            self.view.label.setText("Por favor, complete todos los campos.")

    @permiso_auditoria_notificaciones('editar')
    def enviar_notificacion_automatica(self, mensaje, tipo):
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.model.agregar_notificacion((mensaje, fecha, tipo))
        self.view.label.setText(f"Notificación automática enviada: {mensaje}")
