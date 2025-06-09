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
                    print(f"[LOG ACCIÓN] Ejecutando acción '{accion}' en módulo '{self.modulo}' por usuario: {usuario.get('username', 'desconocido')} (id={usuario.get('id', '-')})")
                    resultado = func(controller, *args, **kwargs)
                    print(f"[LOG ACCIÓN] Acción '{accion}' en módulo '{self.modulo}' finalizada con éxito.")
                    usuario_id = usuario.get('id') if usuario else None
                    detalle = f"{accion} - éxito"
                    auditoria_model.registrar_evento(usuario_id, self.modulo, accion, detalle, ip)
                    return resultado
                except Exception as e:
                    print(f"[LOG ACCIÓN] Error en acción '{accion}' en módulo '{self.modulo}': {e}")
                    usuario_id = usuario.get('id') if usuario else None
                    detalle = f"{accion} - error: {e}"
                    auditoria_model.registrar_evento(usuario_id, self.modulo, accion, detalle, ip)
                    log_error(f"Error en {accion}: {e}")
                    raise
            return wrapper
        return decorador

permiso_auditoria_herrajes = PermisoAuditoria('herrajes')

class HerrajesController:
    """
    Controlador para el módulo de Herrajes.
    
    Todas las acciones públicas relevantes están decoradas con @permiso_auditoria_herrajes,
    lo que garantiza el registro automático en el módulo de auditoría.
    
    Patrón de auditoría:
    - Decorador @permiso_auditoria_herrajes('accion') en cada método público relevante.
    - El decorador valida permisos, registra el evento en auditoría (usuario, módulo, acción, detalle, ip, estado).
    - Feedback visual inmediato ante denegación o error.
    - Para casos personalizados, se puede usar self._registrar_evento_auditoria().
    
    Ejemplo de uso:
        @permiso_auditoria_herrajes('editar')
        def agregar_material(self):
            ...
    """
    def __init__(self, model, view, db_connection, usuarios_model, usuario_actual=None):
        self.model = model
        self.view = view
        self.usuario_actual = usuario_actual
        self.usuarios_model = usuarios_model
        self.auditoria_model = AuditoriaModel(db_connection)
        self.db_connection = db_connection
        self.view.boton_agregar.clicked.connect(self.agregar_material)
        # Conexión del botón de nuevo pedido de herrajes con autocompletado
        if hasattr(self.view, '_conectar_nuevo_pedido'):
            self.view._conectar_nuevo_pedido(self)

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
                # Migrado a QSS: se usa property 'error' en vez de setStyleSheet
                self.view.nombre_input.setProperty("error", True)
                self.view.nombre_input.style().unpolish(self.view.nombre_input)
                self.view.nombre_input.style().polish(self.view.nombre_input)
                self._registrar_evento_auditoria('agregar_material', 'material existente', 'denegado')
                return
            self.model.agregar_material((nombre, cantidad, proveedor))
            self.view.label.setText("Material agregado exitosamente.")
            # Limpiar estado de error visual en input
            self.view.nombre_input.setProperty("error", False)
            self.view.nombre_input.style().unpolish(self.view.nombre_input)
            self.view.nombre_input.style().polish(self.view.nombre_input)
            self._registrar_evento_auditoria('agregar_material', '', 'éxito')
        except Exception as e:
            self.view.label.setText(f"Error al agregar material: {e}")
            self._registrar_evento_auditoria('agregar_material', f"error: {e}", 'error')
            log_error(f"Error en agregar_material: {e}")

    def validar_obra_existente(self, id_obra, obras_model):
        """
        Valida que la obra exista en el sistema antes de permitir registrar un pedido de herrajes.
        Retorna True si existe, False si no.
        """
        if not id_obra:
            return False
        try:
            # El modelo de obras debe tener un método obtener_obra_por_id
            obra = obras_model.obtener_obra_por_id(id_obra)
            return obra is not None
        except Exception as e:
            print(f"[ERROR] No se pudo validar existencia de obra: {e}")
            return False

    def guardar_pedido_herrajes(self, datos, obras_model=None):
        """
        Guarda el pedido de herrajes solo si la obra existe (validación cruzada).
        Si obras_model es None, no valida (para compatibilidad).
        """
        id_obra = datos.get('id_obra') if isinstance(datos, dict) else None
        if obras_model is not None and not self.validar_obra_existente(id_obra, obras_model):
            if hasattr(self.view, 'mostrar_mensaje'):
                self.view.mostrar_mensaje(f"No se puede registrar el pedido: la obra {id_obra} no existe.", tipo='error')
            return
        self.model.guardar_pedido_herrajes(datos)
        self.auditoria_model.registrar_evento(
            usuario_id=self.usuario_actual,
            modulo="Herrajes",
            tipo_evento="Guardar pedido herrajes",
            detalle=f"Guardó pedido de herrajes: {datos}",
            ip_origen="127.0.0.1"
        )
        # Refrescar la tabla de pedidos si existe el método en la vista
        if hasattr(self.view, 'mostrar_resumen_obras'):
            self.view.mostrar_resumen_obras(self.model.obtener_obras_con_estado_pedido())
        elif hasattr(self.view, 'mostrar_pedidos_usuario'):
            self.view.mostrar_pedidos_usuario(self.model.obtener_pedidos_por_usuario(self.usuario_actual))
