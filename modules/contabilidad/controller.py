import hashlib
from core.base_controller import BaseController
from PyQt6.QtWidgets import QTableWidgetItem
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

permiso_auditoria_contabilidad = PermisoAuditoria('contabilidad')

class ContabilidadController(BaseController):
    """
    Controlador para el módulo de Contabilidad.
    
    Todas las acciones públicas relevantes están decoradas con @permiso_auditoria_contabilidad,
    lo que garantiza el registro automático en el módulo de auditoría.
    
    Patrón de auditoría:
    - Decorador @permiso_auditoria_contabilidad('accion') en cada método público relevante.
    - El decorador valida permisos, registra el evento en auditoría (usuario, módulo, acción, detalle, ip, estado).
    - Feedback visual inmediato ante denegación o error.
    - Para casos personalizados, se puede usar self._registrar_evento_auditoria().
    
    Ejemplo de uso:
        @permiso_auditoria_contabilidad('agregar_recibo')
        def agregar_recibo(self):
            ...
    """

    def __init__(self, model, view, db_connection, usuarios_model, obras_model=None, usuario_actual=None):
        super().__init__(model, view)
        self.usuario_actual = usuario_actual
        self.usuarios_model = usuarios_model
        self.auditoria_model = AuditoriaModel(db_connection)
        self.obras_model = obras_model
        self.setup_view_signals()

    def setup_view_signals(self):
        if hasattr(self.view, 'boton_agregar_recibo'):
            self.view.boton_agregar_recibo.clicked.connect(self.abrir_dialogo_nuevo_recibo)
        if hasattr(self.view, 'boton_agregar_balance'):
            self.view.boton_agregar_balance.clicked.connect(self.abrir_dialogo_nuevo_movimiento)
        if hasattr(self.view, 'boton_generar_pdf'):
            self.view.boton_generar_pdf.clicked.connect(self.generar_recibo_pdf_desde_vista)

    def abrir_dialogo_nuevo_recibo(self):
        self.view.abrir_dialogo_nuevo_recibo(self)

    @permiso_auditoria_contabilidad('agregar_recibo')
    def agregar_recibo(self, datos):
        # datos: [fecha, obra_id, monto, concepto, destinatario, estado]
        if not all(datos[:-1]):
            self.view.label_titulo.setText("Complete todos los campos.")
            return
        try:
            self.model.agregar_recibo((datos[0], datos[1], datos[2], datos[3], datos[4], '', 1, datos[5], ''))
            self.actualizar_tabla_recibos()
            self.view.label_titulo.setText("Recibo agregado exitosamente.")
        except Exception as e:
            self.view.label_titulo.setText(f"Error al agregar recibo: {e}")
            log_error(f"Error al agregar recibo: {e}")

    def generar_recibo_pdf_desde_vista(self):
        fila_seleccionada = self.view.tabla_recibos.currentRow()
        if fila_seleccionada != -1:
            id_recibo = self.view.tabla_recibos.item(fila_seleccionada, 0).text()
            self.generar_recibo_pdf(id_recibo)
        else:
            self.view.label.setText("Seleccione un recibo para generar el PDF.")

    @permiso_auditoria_contabilidad('generar_recibo_pdf')
    def generar_recibo_pdf(self, id_recibo):
        try:
            mensaje = self.model.generar_recibo_pdf(id_recibo)
            self.view.label.setText(mensaje)
        except Exception as e:
            self.view.label.setText(f"Error al generar PDF: {e}")
            log_error(f"Error al generar PDF: {e}")

    def actualizar_tabla_recibos(self):
        recibos = self.model.obtener_recibos()
        self.view.tabla_recibos.setRowCount(len(recibos))
        for row, recibo in enumerate(recibos):
            for col, value in enumerate(recibo):
                self.view.tabla_recibos.setItem(row, col, QTableWidgetItem(str(value)))

    def abrir_dialogo_nuevo_movimiento(self):
        self.view.abrir_dialogo_nuevo_movimiento(self)

    @permiso_auditoria_contabilidad('agregar_movimiento_contable')
    def agregar_movimiento_contable(self, datos):
        # datos: [fecha, tipo, monto, concepto, referencia, observaciones]
        if not all(datos):
            self.view.label_titulo.setText("Complete todos los campos.")
            return
        try:
            self.model.agregar_movimiento_contable(tuple(datos))
            self.actualizar_tabla_balance()
            self.view.label_titulo.setText("Movimiento agregado exitosamente.")
        except Exception as e:
            self.view.label_titulo.setText(f"Error al agregar movimiento: {e}")
            log_error(f"Error al agregar movimiento: {e}")

    def actualizar_tabla_balance(self):
        movimientos = self.model.obtener_movimientos_contables()
        self.view.tabla_balance.setRowCount(len(movimientos))
        for row, mov in enumerate(movimientos):
            for col, value in enumerate(mov):
                self.view.tabla_balance.setItem(row, col, QTableWidgetItem(str(value)))

    @permiso_auditoria_contabilidad('exportar_balance')
    def exportar_balance(self, formato):
        try:
            datos_balance = self.model.obtener_datos_balance()  # Método que debe obtener los datos del balance
            mensaje = self.model.exportar_balance(formato, datos_balance)
            self.view.label.setText(mensaje)
        except Exception as e:
            self.view.label.setText(f"Error al exportar balance: {e}")
            log_error(f"Error al exportar balance: {e}")

    @permiso_auditoria_contabilidad('generar_firma_digital')
    def generar_firma_digital(self, datos_recibo):
        try:
            firma = self.model.generar_firma_digital(datos_recibo)
            self.view.label.setText(f"Firma generada: {firma}")
        except Exception as e:
            self.view.label.setText(f"Error al generar firma digital: {e}")
            log_error(f"Error al generar firma digital: {e}")

    @permiso_auditoria_contabilidad('verificar_firma_digital')
    def verificar_firma_digital(self, id_recibo):
        try:
            es_valida = self.model.verificar_firma_digital(id_recibo)
            if es_valida == "Recibo no encontrado.":
                self.view.label.setText(es_valida)
            elif es_valida:
                self.view.label.setText("La firma digital es válida.")
            else:
                self.view.label.setText("La firma digital no es válida.")
        except Exception as e:
            self.view.label.setText(f"Error al verificar firma digital: {e}")
            log_error(f"Error al verificar firma digital: {e}")

    def crear_recibo(self, obra_id, monto_total, concepto, destinatario):
        try:
            self.model.generar_recibo(obra_id, monto_total, concepto, destinatario)
            self.view.label.setText("Recibo creado exitosamente.")
        except Exception as e:
            self.view.label.setText(f"Error al crear el recibo: {e}")
            log_error(f"Error al crear el recibo: {e}")

    def mostrar_estadistica_personalizada(self, config):
        '''Procesa y muestra una estadística personalizada según la configuración guardada.'''
        try:
            # 1. Obtener todos los movimientos contables
            datos = self.model.obtener_movimientos_contables()
            if not datos:
                self.view.label_resumen.setText("No hay datos para mostrar.")
                return
            # Obtener headers dinámicos
            headers = self.view.balance_headers if hasattr(self.view, 'balance_headers') else []
            if not headers:
                headers = ["tipo", "monto", "moneda", "obra", "fecha"]
            # Convertir a lista de dicts
            datos_dict = [dict(zip(headers, row)) for row in datos]
            columna = config.get("columna")
            filtro = config.get("filtro")
            metrica = config.get("metrica")
            tipo_grafico = config.get("tipo_grafico", "Barra")
            # Agrupar y calcular métrica
            grupos = {}
            for d in datos_dict:
                clave = d.get(columna, "Sin valor")
                if filtro and filtro in d and d[filtro]:
                    clave_filtro = f"{clave} - {d[filtro]}"
                else:
                    clave_filtro = clave
                if clave_filtro not in grupos:
                    grupos[clave_filtro] = []
                try:
                    monto = float(d.get("monto", 0))
                except Exception:
                    monto = 0
                grupos[clave_filtro].append(monto)
            # Calcular métrica
            etiquetas = list(grupos.keys())
            if metrica == "Suma":
                valores = [sum(grupos[k]) for k in etiquetas]
            elif metrica == "Promedio":
                valores = [sum(grupos[k])/len(grupos[k]) if grupos[k] else 0 for k in etiquetas]
            elif metrica == "Conteo":
                valores = [len(grupos[k]) for k in etiquetas]
            else:
                valores = [sum(grupos[k]) for k in etiquetas]
            # Llamar a la vista para graficar
            self.view.mostrar_grafico_personalizado(etiquetas, valores, config)
        except Exception as e:
            self.view.label_resumen.setText(f"Error al mostrar estadística: {e}")
            log_error(f"Error al mostrar estadística: {e}")

    def _registrar_evento_auditoria(self, accion, detalle_extra="", estado=""):
        usuario = getattr(self, 'usuario_actual', None)
        usuario_id = usuario['id'] if usuario and 'id' in usuario else None
        ip = usuario.get('ip', '') if usuario else ''
        detalle = f"{accion}{' - ' + detalle_extra if detalle_extra else ''}{' - ' + estado if estado else ''}"
        try:
            if self.auditoria_model:
                self.auditoria_model.registrar_evento(usuario_id, 'contabilidad', accion, detalle, ip)
        except Exception as e:
            log_error(f"Error registrando evento auditoría: {e}")

    # --- INTEGRACIÓN DE PAGOS POR PEDIDO (expuestos para otros módulos y la UI) ---
    @permiso_auditoria_contabilidad('registrar_pago_pedido')
    def registrar_pago_pedido(self, id_pedido, modulo, obra_id, monto, fecha, usuario, estado, comprobante=None, observaciones=None):
        return self.model.registrar_pago_pedido(id_pedido, modulo, obra_id, monto, fecha, usuario, estado, comprobante, observaciones)

    @permiso_auditoria_contabilidad('actualizar_estado_pago')
    def actualizar_estado_pago(self, id_pago, nuevo_estado):
        return self.model.actualizar_estado_pago(id_pago, nuevo_estado)

    def obtener_pagos_por_pedido(self, id_pedido, modulo):
        return self.model.obtener_pagos_por_pedido(id_pedido, modulo)

    def obtener_pagos_por_obra(self, obra_id, modulo=None):
        return self.model.obtener_pagos_por_obra(obra_id, modulo)

    def obtener_estado_pago_pedido(self, id_pedido, modulo):
        return self.model.obtener_estado_pago_pedido(id_pedido, modulo)

    def obtener_pagos_por_usuario(self, usuario):
        return self.model.obtener_pagos_por_usuario(usuario)
    # --- FIN INTEGRACIÓN DE PAGOS POR PEDIDO ---
