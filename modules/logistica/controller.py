from modules.usuarios.model import UsuariosModel
from modules.auditoria.model import AuditoriaModel
from functools import wraps
from PyQt6.QtWidgets import QLabel

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

    def actualizar_por_cambio_estado_obra(self, id_obra, nuevo_estado):
        from datetime import datetime, timedelta
        usuario = getattr(self, 'usuario_actual', None)
        ip = usuario.get('ip', '') if usuario else ''
        auditoria_model = getattr(self, 'auditoria_model', None)
        try:
            if not hasattr(self.view, 'label'):
                self.view.label = QLabel()
                self.view.layout().addWidget(self.view.label)
            # Si el estado es 'Entrega', programar una entrega real para la obra
            if nuevo_estado.lower() == "entrega":
                fecha_programada = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
                vehiculo_asignado = "Vehículo 1"
                chofer_asignado = "Chofer 1"
                control_subida = self.usuario_actual['username'] if hasattr(self, 'usuario_actual') and self.usuario_actual else "controlador"
                fecha_llegada = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
                # Obtener datos de la obra y armar fila extendida
                obra = self.model.db.ejecutar_query("SELECT id, nombre, direccion, estado, cliente FROM obras WHERE id = ?", (id_obra,))
                fila = None
                if obra:
                    fila = list(obra[0]) + [chofer_asignado, control_subida, fecha_llegada]
                    self.view.cargar_datos_obras_en_logistica([fila])
                self.model.programar_entrega(id_obra, fecha_programada, vehiculo_asignado, chofer_asignado, control_subida, fecha_llegada)
                self.view.label.setText(f"Entrega programada para la obra {id_obra} el {fecha_programada} (Vehículo: {vehiculo_asignado}, Chofer: {chofer_asignado}, Control: {control_subida}, Llegada: {fecha_llegada})")
                if auditoria_model:
                    auditoria_model.registrar_evento(usuario, 'logistica', f'programar_entrega_obra_{id_obra}', ip_origen=ip, resultado="éxito")
            elif nuevo_estado.lower() in ("colocada", "finalizada"):
                self.view.label.setText(f"Obra {id_obra} marcada como '{nuevo_estado}'. Puede cerrar la entrega si corresponde.")
                if auditoria_model:
                    auditoria_model.registrar_evento(usuario, 'logistica', f'cambio_estado_obra_{id_obra}_{nuevo_estado}', ip_origen=ip, resultado="éxito")
            # Refrescar la tabla/envíos
            if hasattr(self.view, 'tabla_envios'):
                if hasattr(self.view, 'cargar_datos_envios'):
                    self.view.cargar_datos_envios()
        except Exception as e:
            if auditoria_model:
                auditoria_model.registrar_evento(usuario, 'logistica', f'actualizar_por_cambio_estado_obra_{id_obra}_{nuevo_estado}', ip_origen=ip, resultado=f"error: {e}")
            raise
