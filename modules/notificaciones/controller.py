from datetime import datetime
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

permiso_auditoria_notificaciones = PermisoAuditoria('notificaciones')

class NotificacionesController:
    def __init__(self, model, view, db_connection, usuarios_model, usuario_actual=None):
        self.model = model
        self.view = view
        self.usuario_actual = usuario_actual
        self.usuarios_model = usuarios_model
        self.auditoria_model = AuditoriaModel(db_connection)
        self.view.boton_agregar.clicked.connect(self.agregar_notificacion)

    def _registrar_evento_auditoria(self, accion, detalle_extra="", estado=""):
        usuario = getattr(self, 'usuario_actual', None)
        usuario_id = usuario['id'] if usuario and 'id' in usuario else None
        ip = usuario.get('ip', '') if usuario else ''
        detalle = f"{accion}{' - ' + detalle_extra if detalle_extra else ''}{' - ' + estado if estado else ''}"
        try:
            if self.auditoria_model:
                self.auditoria_model.registrar_evento(usuario_id, 'notificaciones', accion, detalle, ip)
        except Exception as e:
            log_error(f"Error registrando evento auditoría: {e}")

    @permiso_auditoria_notificaciones('editar')
    def agregar_notificacion(self):
        mensaje = self.view.mensaje_input.text()
        fecha = self.view.fecha_input.text()
        tipo = self.view.tipo_input.text()
        if mensaje and fecha and tipo:
            try:
                self.model.agregar_notificacion((mensaje, fecha, tipo))
                self.view.label.setText("Notificación agregada exitosamente.")
                self._registrar_evento_auditoria('agregar_notificacion', '', 'éxito')
            except Exception as e:
                self.view.label.setText(f"Error al agregar notificación: {e}")
                self._registrar_evento_auditoria('agregar_notificacion', f"error: {e}", 'error')
                log_error(f"Error al agregar notificación: {e}")
        else:
            self.view.label.setText("Por favor, complete todos los campos.")
            self._registrar_evento_auditoria('agregar_notificacion', 'faltan campos', 'denegado')

    @permiso_auditoria_notificaciones('editar')
    def enviar_notificacion_automatica(self, mensaje, tipo):
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            self.model.agregar_notificacion((mensaje, fecha, tipo))
            self.view.label.setText(f"Notificación automática enviada: {mensaje}")
            self._registrar_evento_auditoria('enviar_notificacion_automatica', '', 'éxito')
        except Exception as e:
            self.view.label.setText(f"Error al enviar notificación automática: {e}")
            self._registrar_evento_auditoria('enviar_notificacion_automatica', f"error: {e}", 'error')
            log_error(f"Error al enviar notificación automática: {e}")
