from core.base_controller import BaseController
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

permiso_auditoria_mantenimiento = PermisoAuditoria('mantenimiento')

class MantenimientoController(BaseController):
    """
    Controlador para el módulo de Mantenimiento.
    
    Todas las acciones públicas relevantes están decoradas con @permiso_auditoria_mantenimiento,
    lo que garantiza el registro automático en el módulo de auditoría.
    
    Patrón de auditoría:
    - Decorador @permiso_auditoria_mantenimiento('accion') en cada método público relevante.
    - El decorador valida permisos, registra el evento en auditoría (usuario, módulo, acción, detalle, ip, estado).
    - Feedback visual inmediato ante denegación o error.
    - Para casos personalizados, se puede usar self._registrar_evento_auditoria().
    
    Ejemplo de uso:
        @permiso_auditoria_mantenimiento('registrar_mantenimiento')
        def registrar_mantenimiento(self):
            ...
    """

    def __init__(self, model, view, db_connection, usuarios_model, usuario_actual=None, notificaciones_controller=None):
        super().__init__(model, view)
        self.usuario_actual = usuario_actual
        self.usuarios_model = usuarios_model
        self.auditoria_model = AuditoriaModel(db_connection)
        self.notificaciones_controller = notificaciones_controller

    def _registrar_evento_auditoria(self, accion, detalle_extra="", estado=""):
        usuario = getattr(self, 'usuario_actual', None)
        usuario_id = usuario['id'] if usuario and 'id' in usuario else None
        ip = usuario.get('ip', '') if usuario else ''
        detalle = f"{accion}{' - ' + detalle_extra if detalle_extra else ''}{' - ' + estado if estado else ''}"
        try:
            if self.auditoria_model:
                self.auditoria_model.registrar_evento(usuario_id, 'mantenimiento', accion, detalle, ip)
        except Exception as e:
            log_error(f"Error registrando evento auditoría: {e}")

    def setup_view_signals(self):
        if hasattr(self.view, 'boton_agregar_mantenimiento'):
            self.view.boton_agregar_mantenimiento.clicked.connect(self.registrar_mantenimiento)
        if hasattr(self.view, 'boton_ver_tareas_recurrentes'):
            self.view.boton_ver_tareas_recurrentes.clicked.connect(self.mostrar_tareas_recurrentes)
        if hasattr(self.view, 'boton_registrar_repuesto'):
            self.view.boton_registrar_repuesto.clicked.connect(self.registrar_repuesto_utilizado)
        if hasattr(self.view, 'boton_exportar_excel'):
            self.view.boton_exportar_excel.clicked.connect(lambda: self.exportar_reporte_mantenimiento('excel'))
        if hasattr(self.view, 'boton_exportar_pdf'):
            self.view.boton_exportar_pdf.clicked.connect(lambda: self.exportar_reporte_mantenimiento('pdf'))

    @permiso_auditoria_mantenimiento('registrar_mantenimiento')
    def registrar_mantenimiento(self):
        datos = (
            self.view.tipo_mantenimiento_input.currentText(),
            self.view.fecha_realizacion_input.date().toString("yyyy-MM-dd"),
            self.view.realizado_por_input.text(),
            self.view.observaciones_input.toPlainText(),
            self.view.firma_digital_input.text()
        )
        self.model.registrar_mantenimiento(datos)
        self.view.label.setText("Mantenimiento registrado exitosamente.")
        self._registrar_evento_auditoria('registrar_mantenimiento', estado="éxito")

    @permiso_auditoria_mantenimiento('mostrar_tareas_recurrentes')
    def mostrar_tareas_recurrentes(self):
        tareas = self.model.obtener_tareas_recurrentes()
        self.view.mostrar_tareas_recurrentes(tareas)
        self._registrar_evento_auditoria('mostrar_tareas_recurrentes', estado="éxito")

    @permiso_auditoria_mantenimiento('registrar_repuesto_utilizado')
    def registrar_repuesto_utilizado(self):
        id_mantenimiento = self.view.id_mantenimiento_input.text()
        id_item = self.view.id_item_input.text()
        cantidad_utilizada = self.view.cantidad_utilizada_input.text()

        if id_mantenimiento and id_item and cantidad_utilizada:
            datos = (id_mantenimiento, id_item, cantidad_utilizada)
            self.model.registrar_repuesto_utilizado(datos)
            self.view.label.setText("Repuesto registrado exitosamente.")
            self._registrar_evento_auditoria('registrar_repuesto_utilizado', estado="éxito")
        else:
            self.view.label.setText("Por favor, complete todos los campos.")
            self._registrar_evento_auditoria('registrar_repuesto_utilizado', estado="denegado")

    @permiso_auditoria_mantenimiento('verificar_tareas_recurrentes')
    def verificar_tareas_recurrentes(self):
        tareas = self.model.obtener_tareas_recurrentes()
        if tareas:
            mensaje = f"Hay {len(tareas)} tareas recurrentes vencidas."
            if hasattr(self, 'notificaciones_controller') and self.notificaciones_controller:
                self.notificaciones_controller.enviar_notificacion_automatica(mensaje, "mantenimiento")
            else:
                self.view.label.setText("No se puede enviar notificación automática: controlador de notificaciones no definido.")
            self.view.label.setText(mensaje)
            self._registrar_evento_auditoria('verificar_tareas_recurrentes', estado="éxito")
        else:
            self._registrar_evento_auditoria('verificar_tareas_recurrentes', estado="sin tareas")

    @permiso_auditoria_mantenimiento('exportar_reporte_mantenimiento')
    def exportar_reporte_mantenimiento(self, formato):
        mensaje = self.model.exportar_reporte_mantenimiento(formato)
        self.view.label.setText(mensaje)
        self._registrar_evento_auditoria('exportar_reporte_mantenimiento', estado="éxito")

    @permiso_auditoria_mantenimiento('exportar_historial_mantenimientos')
    def exportar_historial_mantenimientos(self, formato):
        mensaje = self.model.exportar_historial_mantenimientos(formato)
        self.view.label.setText(mensaje)
        self._registrar_evento_auditoria('exportar_historial_mantenimientos', estado="éxito")
