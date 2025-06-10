from modules.usuarios.model import UsuariosModel
from modules.auditoria.model import AuditoriaModel
from functools import wraps
from PyQt6.QtWidgets import QLabel, QTableWidgetItem
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
                    print(f"[LOG ACCIÓN] Ejecutando acción '{accion}' en módulo '{self.modulo}' por usuario: {usuario.get('username', 'desconocido')} (id={usuario.get('id', '-')})")
                    resultado = func(controller, *args, **kwargs)
                    print(f"[LOG ACCIÓN] Acción '{accion}' en módulo '{self.modulo}' finalizada con éxito.")
                    if auditoria_model:
                        usuario_id = usuario.get('id') if usuario else None
                        detalle = f"{accion} - éxito"
                        auditoria_model.registrar_evento(usuario_id, self.modulo, accion, detalle, ip)
                    return resultado
                except Exception as e:
                    print(f"[LOG ACCIÓN] Error en acción '{accion}' en módulo '{self.modulo}': {e}")
                    if auditoria_model:
                        usuario_id = usuario.get('id') if usuario else None
                        detalle = f"{accion} - error: {e}"
                        auditoria_model.registrar_evento(usuario_id, self.modulo, accion, detalle, ip)
                    log_error(f"Error en {accion}: {e}")
                    raise
            return wrapper
        return decorador

permiso_auditoria_logistica = PermisoAuditoria('logistica')

class LogisticaController:
    """
    Controlador para el módulo de Logística.
    
    Todas las acciones públicas relevantes están decoradas con @permiso_auditoria_logistica,
    lo que garantiza el registro automático en el módulo de auditoría.
    
    Patrón de auditoría:
    - Decorador @permiso_auditoria_logistica('accion') en cada método público relevante.
    - El decorador valida permisos, registra el evento en auditoría (usuario, módulo, acción, detalle, ip, estado).
    - Feedback visual inmediato ante denegación o error.
    - Para casos personalizados, se puede usar self._registrar_evento_auditoria().
    
    Ejemplo de uso:
        @permiso_auditoria_logistica('ver')
        def ver_entregas(self):
            ...
    """
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

    @permiso_auditoria_logistica('consultar')
    def consultar_obras_listas_para_entrega(self, obras_model, inventario_model, vidrios_model, herrajes_model, contabilidad_model):
        """
        Consulta y muestra las obras listas para fabricar/entregar (todos los pedidos realizados y pagados).
        Feedback visual y registro en auditoría.
        """
        try:
            obras_listas = self.model.obtener_obras_listas_para_entrega(
                obras_model, inventario_model, vidrios_model, herrajes_model, contabilidad_model
            )
            if hasattr(self.view, 'mostrar_obras_listas_para_entrega'):
                self.view.mostrar_obras_listas_para_entrega(obras_listas)
            self._registrar_evento_auditoria('consultar_obras_listas_para_entrega', estado='éxito')
            return obras_listas
        except Exception as e:
            if hasattr(self.view, 'mostrar_mensaje'):
                self.view.mostrar_mensaje(f"Error al consultar obras listas: {e}", tipo='error')
            self._registrar_evento_auditoria('consultar_obras_listas_para_entrega', estado=f'error: {e}')
            return []

    @permiso_auditoria_logistica('asignar')
    def asignar_colocador_a_obra(self, id_obra, colocador):
        """
        Asigna un colocador a una obra lista para entrega y registra la acción en auditoría.
        """
        try:
            query = "UPDATE entregas_obras SET colocador_asignado = ? WHERE id_obra = ?"
            self.model.db.ejecutar_query(query, (colocador, id_obra))
            if hasattr(self.view, 'mostrar_mensaje'):
                self.view.mostrar_mensaje(f"Colocador '{colocador}' asignado a la obra {id_obra}.", tipo='info')
            self._registrar_evento_auditoria('asignar_colocador', f'id_obra={id_obra}, colocador={colocador}', estado='éxito')
        except Exception as e:
            if hasattr(self.view, 'mostrar_mensaje'):
                self.view.mostrar_mensaje(f"Error al asignar colocador: {e}", tipo='error')
            self._registrar_evento_auditoria('asignar_colocador', f'id_obra={id_obra}, colocador={colocador}', estado=f'error: {e}')


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

    def validar_pago_colocacion(self, id_pedido, obra_id, contabilidad_controller, modulo="logistica"):
        """
        Verifica si el pago de la colocación está realizado. Si no, requiere justificación para continuar.
        Retorna True si se puede continuar, False si debe bloquearse.
        """
        estado_pago = contabilidad_controller.obtener_estado_pago_pedido(id_pedido, modulo)
        if estado_pago == "pagado":
            return True
        # Si no está pagado, solicitar justificación
        from PyQt6.QtWidgets import QInputDialog, QMessageBox
        justificacion, ok = QInputDialog.getText(self.view, "Colocación sin pago registrado", "Ingrese motivo/justificación para continuar:")
        if ok and justificacion.strip():
            self.registrar_excepcion_colocacion_sin_pago(id_pedido, obra_id, justificacion, self.usuario_actual)
            QMessageBox.warning(self.view, "Advertencia", "Se registró la colocación sin pago. Justificación guardada.")
            return True
        else:
            QMessageBox.critical(self.view, "Acción bloqueada", "No se puede realizar la colocación sin pago o justificación.")
            return False

    def registrar_excepcion_colocacion_sin_pago(self, id_pedido, obra_id, justificacion, usuario):
        """
        Registra en auditoría y/o en la base de datos la excepción de colocación sin pago.
        """
        detalle = f"Colocación sin pago | Pedido: {id_pedido} | Obra: {obra_id} | Usuario: {usuario.get('usuario', '')} | Motivo: {justificacion}"
        self._registrar_evento_auditoria('colocacion_sin_pago', detalle_extra=detalle, estado="excepcion")
        # Opcional: guardar en tabla de excepciones si existe

    def mostrar_y_editar_pago_colocacion(self, id_pedido, obra_id, contabilidad_controller, usuario_actual):
        """
        Muestra el estado de pago y permite registrar/editar pago de colocación desde Logística.
        """
        pagos = contabilidad_controller.obtener_pagos_por_pedido(id_pedido, modulo="logistica")
        datos_pago = None
        if pagos:
            pago = pagos[-1]  # Tomar el último pago registrado
            datos_pago = {
                'monto': pago[4],
                'fecha': pago[5],
                'comprobante': pago[8],
                'estado': pago[7],
                'observaciones': pago[9]
            }
        datos_nuevos = self.view.mostrar_dialogo_pago_colocacion(datos_pago)
        if datos_nuevos:
            contabilidad_controller.registrar_pago_pedido(
                id_pedido=id_pedido,
                modulo="logistica",
                obra_id=obra_id,
                monto=datos_nuevos['monto'],
                fecha=datos_nuevos['fecha'],
                usuario=usuario_actual['usuario'],
                estado=datos_nuevos['estado'],
                comprobante=datos_nuevos['comprobante'],
                observaciones=datos_nuevos['observaciones']
            )
            self.view.mostrar_estado_pago_colocacion(datos_nuevos['estado'], datos_nuevos['fecha'])

    def mostrar_estado_pago_colocacion_en_tabla(self, id_pedido, contabilidad_controller, fila, tabla):
        pagos = contabilidad_controller.obtener_pagos_por_pedido(id_pedido, modulo="logistica")
        if pagos:
            pago = pagos[-1]
            estado = pago[7]
            fecha = pago[5]
        else:
            estado = "Pendiente"
            fecha = ""
        tabla.setItem(fila, tabla.columnCount()-1, QTableWidgetItem(f"{estado} | {fecha}"))
