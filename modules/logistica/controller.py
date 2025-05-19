from modules.usuarios.model import UsuariosModel
from modules.auditoria.model import AuditoriaModel
from functools import wraps
from PyQt6.QtWidgets import QLabel
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
                    if auditoria_model:
                        usuario_id = usuario.get('id') if usuario else None
                        detalle = f"{accion} - denegado"
                        auditoria_model.registrar_evento(usuario_id, self.modulo, accion, detalle, ip)
                    return None
                try:
                    resultado = func(controller, *args, **kwargs)
                    if auditoria_model:
                        usuario_id = usuario.get('id') if usuario else None
                        detalle = f"{accion} - éxito"
                        auditoria_model.registrar_evento(usuario_id, self.modulo, accion, detalle, ip)
                    return resultado
                except Exception as e:
                    if auditoria_model:
                        usuario_id = usuario.get('id') if usuario else None
                        detalle = f"{accion} - error: {e}"
                        auditoria_model.registrar_evento(usuario_id, self.modulo, accion, detalle, ip)
                    raise
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

    def _registrar_evento_auditoria(self, accion, detalle_extra="", estado=""):
        usuario = getattr(self, 'usuario_actual', None)
        ip = usuario.get('ip', '') if usuario else ''
        usuario_id = usuario.get('id') if usuario else None
        detalle = f"{accion}{' - ' + detalle_extra if detalle_extra else ''}{' - ' + estado if estado else ''}"
        try:
            if self.auditoria_model:
                self.auditoria_model.registrar_evento(usuario_id, 'logistica', accion, detalle, ip)
        except Exception as e:
            log_error(f"Error registrando evento auditoría: {e}")

    @permiso_auditoria_logistica('ver')
    def ver_entregas(self):
        try:
            # Implementar lógica de visualización de entregas
            self._registrar_evento_auditoria('ver_entregas', estado="éxito")
        except Exception as e:
            self._registrar_evento_auditoria('ver_entregas', estado=f"error: {e}")
            log_error(f"Error en ver_entregas: {e}")
            if hasattr(self.view, 'label'):
                self.view.label.setText(f"Error al ver entregas: {e}")

    @permiso_auditoria_logistica('editar')
    def editar_entrega(self):
        try:
            # Implementar lógica de edición de entrega
            self._registrar_evento_auditoria('editar_entrega', estado="éxito")
        except Exception as e:
            self._registrar_evento_auditoria('editar_entrega', estado=f"error: {e}")
            log_error(f"Error en editar_entrega: {e}")
            if hasattr(self.view, 'label'):
                self.view.label.setText(f"Error al editar entrega: {e}")

    @permiso_auditoria_logistica('firmar')
    def firmar_entrega(self):
        try:
            # Implementar lógica de firma de entrega
            self._registrar_evento_auditoria('firmar_entrega', estado="éxito")
        except Exception as e:
            self._registrar_evento_auditoria('firmar_entrega', estado=f"error: {e}")
            log_error(f"Error en firmar_entrega: {e}")
            if hasattr(self.view, 'label'):
                self.view.label.setText(f"Error al firmar entrega: {e}")

    @permiso_auditoria_logistica('reprogramar')
    def reprogramar_entrega(self):
        try:
            # Implementar lógica de reprogramación de entrega
            self._registrar_evento_auditoria('reprogramar_entrega', estado="éxito")
        except Exception as e:
            self._registrar_evento_auditoria('reprogramar_entrega', estado=f"error: {e}")
            log_error(f"Error en reprogramar_entrega: {e}")
            if hasattr(self.view, 'label'):
                self.view.label.setText(f"Error al reprogramar entrega: {e}")

    def actualizar_por_cambio_estado_obra(self, id_obra, nuevo_estado):
        from datetime import datetime, timedelta
        usuario = getattr(self, 'usuario_actual', None)
        ip = usuario.get('ip', '') if usuario else ''
        usuario_id = usuario.get('id') if usuario else None
        try:
            if not id_obra or not nuevo_estado:
                if hasattr(self.view, 'label'):
                    self.view.label.setText("Faltan argumentos para actualizar el estado de la obra.")
                self._registrar_evento_auditoria('actualizar_por_cambio_estado_obra', f"id_obra={id_obra}, nuevo_estado={nuevo_estado}", estado="denegado (faltan argumentos)")
                return
            if not hasattr(self.view, 'label'):
                self.view.label = QLabel()
                self.view.layout().addWidget(self.view.label)
            if nuevo_estado.lower() == "entrega":
                fecha_programada = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
                vehiculo_asignado = "Vehículo 1"
                chofer_asignado = "Chofer 1"
                control_subida = self.usuario_actual['username'] if hasattr(self, 'usuario_actual') and self.usuario_actual else "controlador"
                fecha_llegada = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
                obra = self.model.db.ejecutar_query("SELECT id, nombre, direccion, estado, cliente FROM obras WHERE id = ?", (id_obra,))
                fila = None
                if obra:
                    fila = list(obra[0]) + [chofer_asignado, control_subida, fecha_llegada]
                    self.view.cargar_datos_obras_en_logistica([fila])
                self.model.programar_entrega(id_obra, fecha_programada, vehiculo_asignado, chofer_asignado, control_subida, fecha_llegada)
                self.view.label.setText(f"Entrega programada para la obra {id_obra} el {fecha_programada} (Vehículo: {vehiculo_asignado}, Chofer: {chofer_asignado}, Control: {control_subida}, Llegada: {fecha_llegada})")
                self._registrar_evento_auditoria('programar_entrega_obra', f"id_obra={id_obra}", estado="éxito")
            elif nuevo_estado.lower() in ("colocada", "finalizada"):
                self.view.label.setText(f"Obra {id_obra} marcada como '{nuevo_estado}'. Puede cerrar la entrega si corresponde.")
                self._registrar_evento_auditoria('cambio_estado_obra', f"id_obra={id_obra}, nuevo_estado={nuevo_estado}", estado="éxito")
            if hasattr(self.view, 'tabla_envios'):
                if hasattr(self.view, 'cargar_datos_envios'):
                    self.view.cargar_datos_envios()
        except Exception as e:
            self._registrar_evento_auditoria('actualizar_por_cambio_estado_obra', f"id_obra={id_obra}, nuevo_estado={nuevo_estado}", estado=f"error: {e}")
            log_error(f"Error en actualizar_por_cambio_estado_obra: {e}")
            if hasattr(self.view, 'label'):
                self.view.label.setText(f"Error al actualizar estado de obra: {e}")
