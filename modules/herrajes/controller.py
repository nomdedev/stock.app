from PyQt6.QtWidgets import QMessageBox
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
                db_connection = getattr(controller, 'db_connection', None)
                usuario_model = getattr(controller, 'usuarios_model', None)
                auditoria_model = getattr(controller, 'auditoria_model', None)
                if usuario_model is None and db_connection is not None:
                    from modules.usuarios.model import UsuariosModel
                    usuario_model = UsuariosModel(db_connection)
                if auditoria_model is None and db_connection is not None:
                    from modules.auditoria.model import AuditoriaModel
                    auditoria_model = AuditoriaModel(db_connection)
                usuario = getattr(controller, 'usuario_actual', None)
                if not usuario or not usuario_model or not auditoria_model:
                    if hasattr(controller, 'view') and hasattr(controller.view, 'label'):
                        controller.view.label.setText("Error interno: modelo de usuario o auditoría no disponible.")
                    return None
                if not usuario_model.tiene_permiso(usuario, self.modulo, accion):
                    if hasattr(controller, 'view') and hasattr(controller.view, 'label'):
                        controller.view.label.setText(f"No tiene permiso para realizar la acción: {accion}")
                    return None
                resultado = func(controller, *args, **kwargs)
                auditoria_model.registrar_evento(usuario, self.modulo, accion)
                return resultado
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

    @permiso_auditoria_herrajes('editar')
    def agregar_material(self):
        try:
            nombre = self.view.nombre_input.text()
            cantidad = self.view.cantidad_input.text()
            proveedor = self.view.proveedor_input.text()
            if not (nombre and cantidad and proveedor):
                self.view.label.setText("Por favor, complete todos los campos.")
                return
            if self.model.verificar_material_existente(nombre):
                QMessageBox.warning(
                    self.view,
                    "Material Existente",
                    "Ya existe un material con el mismo nombre."
                )
                self.view.nombre_input.setStyleSheet("border: 1px solid red;")
                return
            self.model.agregar_material((nombre, cantidad, proveedor))
            self.view.label.setText("Material agregado exitosamente.")
            self.view.nombre_input.setStyleSheet("")
        except Exception as e:
            self.view.label.setText(f"Error al agregar material: {e}")
