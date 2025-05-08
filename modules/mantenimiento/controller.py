from core.base_controller import BaseController
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

permiso_auditoria_mantenimiento = PermisoAuditoria('mantenimiento')

class MantenimientoController(BaseController):
    def __init__(self, model, view, usuario_actual=None):
        super().__init__(model, view)
        self.usuario_actual = usuario_actual
        self.usuarios_model = UsuariosModel()
        self.auditoria_model = AuditoriaModel()

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

    @permiso_auditoria_mantenimiento('mostrar_tareas_recurrentes')
    def mostrar_tareas_recurrentes(self):
        tareas = self.model.obtener_tareas_recurrentes()
        self.view.mostrar_tareas_recurrentes(tareas)

    @permiso_auditoria_mantenimiento('registrar_repuesto_utilizado')
    def registrar_repuesto_utilizado(self):
        id_mantenimiento = self.view.id_mantenimiento_input.text()
        id_item = self.view.id_item_input.text()
        cantidad_utilizada = self.view.cantidad_utilizada_input.text()

        if id_mantenimiento and id_item and cantidad_utilizada:
            datos = (id_mantenimiento, id_item, cantidad_utilizada)
            self.model.registrar_repuesto_utilizado(datos)
            self.view.label.setText("Repuesto registrado exitosamente.")
        else:
            self.view.label.setText("Por favor, complete todos los campos.")

    @permiso_auditoria_mantenimiento('verificar_tareas_recurrentes')
    def verificar_tareas_recurrentes(self):
        tareas = self.model.obtener_tareas_recurrentes()
        if tareas:
            mensaje = f"Hay {len(tareas)} tareas recurrentes vencidas."
            self.notificaciones_controller.enviar_notificacion_automatica(mensaje, "mantenimiento")
            self.view.label.setText(mensaje)

    @permiso_auditoria_mantenimiento('exportar_reporte_mantenimiento')
    def exportar_reporte_mantenimiento(self, formato):
        mensaje = self.model.exportar_reporte_mantenimiento(formato)
        self.view.label.setText(mensaje)

    @permiso_auditoria_mantenimiento('exportar_historial_mantenimientos')
    def exportar_historial_mantenimientos(self, formato):
        mensaje = self.model.exportar_historial_mantenimientos(formato)
        self.view.label.setText(mensaje)
