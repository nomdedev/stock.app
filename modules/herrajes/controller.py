from PyQt6.QtWidgets import QMessageBox
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
                ip = usuario.get('ip', '') if usuario else ''
                if not usuario or not usuario_model or not auditoria_model:
                    if hasattr(controller, 'view') and hasattr(controller.view, 'label'):
                        controller.view.label.setText(f"No tiene permiso para realizar la acción: {accion}")
                    return None
                if not usuario_model.tiene_permiso(usuario, self.modulo, accion):
                    if hasattr(controller, 'view') and hasattr(controller.view, 'label'):
                        controller.view.label.setText(f"No tiene permiso para realizar la acción: {accion}")
                    usuario_id = usuario.get('id') if usuario else None
                    detalle = f"{accion} - denegado"
                    auditoria_model.registrar_evento(usuario_id, self.modulo, accion, detalle, ip)
                    return None
                try:
                    resultado = func(controller, *args, **kwargs)
                    usuario_id = usuario.get('id') if usuario else None
                    detalle = f"{accion} - éxito"
                    auditoria_model.registrar_evento(usuario_id, self.modulo, accion, detalle, ip)
                    return resultado
                except Exception as e:
                    usuario_id = usuario.get('id') if usuario else None
                    detalle = f"{accion} - error: {e}"
                    auditoria_model.registrar_evento(usuario_id, self.modulo, accion, detalle, ip)
                    log_error(f"Error en {accion}: {e}")
                    raise
            return wrapper
        return decorador

permiso_auditoria_herrajes = PermisoAuditoria('herrajes')

class HerrajesController:
    def __init__(self, model, view, db_connection, usuarios_model, usuario_actual=None):
        self.model = model
        self.view = view
        self.usuario_actual = usuario_actual
        self.usuarios_model = usuarios_model
        self.auditoria_model = AuditoriaModel(db_connection)
        self.db_connection = db_connection
        self.view.boton_agregar.clicked.connect(self.agregar_material)

    def _registrar_evento_auditoria(self, accion, detalle_extra="", estado=""):
        usuario = getattr(self, 'usuario_actual', None)
        ip = usuario.get('ip', '') if usuario else ''
        usuario_id = usuario.get('id') if usuario else None
        detalle = f"{accion}{' - ' + detalle_extra if detalle_extra else ''}{' - ' + estado if estado else ''}"
        try:
            if self.auditoria_model:
                self.auditoria_model.registrar_evento(usuario_id, 'herrajes', accion, detalle, ip)
        except Exception as e:
            log_error(f"Error registrando evento auditoría: {e}")

    @permiso_auditoria_herrajes('editar')
    def agregar_material(self):
        usuario = getattr(self, 'usuario_actual', None)
        ip = usuario.get('ip', '') if usuario else ''
        try:
            nombre = self.view.nombre_input.text()
            cantidad = self.view.cantidad_input.text()
            proveedor = self.view.proveedor_input.text()
            if not (nombre and cantidad and proveedor):
                self.view.label.setText("Por favor, complete todos los campos.")
                self._registrar_evento_auditoria('agregar_material', 'faltan campos', 'denegado')
                return
            if self.model.verificar_material_existente(nombre):
                QMessageBox.warning(
                    self.view,
                    "Material Existente",
                    "Ya existe un material con el mismo nombre."
                )
                self.view.nombre_input.setStyleSheet("border: 1px solid red;")
                self._registrar_evento_auditoria('agregar_material', 'material existente', 'denegado')
                return
            self.model.agregar_material((nombre, cantidad, proveedor))
            self.view.label.setText("Material agregado exitosamente.")
            self.view.nombre_input.setStyleSheet("")
            self._registrar_evento_auditoria('agregar_material', '', 'éxito')
        except Exception as e:
            self.view.label.setText(f"Error al agregar material: {e}")
            self._registrar_evento_auditoria('agregar_material', f"error: {e}", 'error')
            log_error(f"Error en agregar_material: {e}")
