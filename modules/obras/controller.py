import datetime
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox, QLineEdit, QComboBox, QWidget, QHBoxLayout, QFormLayout, QCheckBox
from PyQt6.QtGui import QIcon
from PyQt6 import QtCore
from modules.usuarios.model import UsuariosModel
from modules.auditoria.model import AuditoriaModel
from functools import wraps
from core.ui_components import estilizar_boton_icono

class PermisoAuditoria:
    def __init__(self, modulo):
        self.modulo = modulo
    def __call__(self, accion):
        def decorador(func):
            from functools import wraps
            @wraps(func)
            def wrapper(controller, *args, **kwargs):
                # --- ESTÁNDAR: Validación de modelos y usuario ---
                usuario_model = getattr(controller, 'usuarios_model', None)
                auditoria_model = getattr(controller, 'auditoria_model', None)
                usuario = getattr(controller, 'usuario_actual', None)
                usuario_id = usuario['id'] if usuario and 'id' in usuario else None
                ip = usuario.get('ip', '') if usuario else ''
                # --- Feedback visual moderno y registro de error si faltan modelos ---
                if usuario_model is None or auditoria_model is None:
                    mensaje = "Error interno: modelo de usuario o auditoría no disponible."
                    if hasattr(controller, 'view') and hasattr(controller.view, 'mostrar_mensaje'):
                        controller.view.mostrar_mensaje(mensaje, tipo='error')
                    elif hasattr(controller, 'view') and hasattr(controller.view, 'label'):
                        controller.view.label.setText(mensaje)
                    if auditoria_model:
                        detalle = f"{accion} - error (modelo no disponible)"
                        auditoria_model.registrar_evento(usuario_id, self.modulo, accion, detalle, ip)
                    from core.logger import log_error
                    log_error(f"{mensaje} [{self.modulo}/{accion}]")
                    return None
                # --- Validación de permisos ---
                if not usuario or not usuario_model.tiene_permiso(usuario, self.modulo, accion):
                    mensaje = f"No tiene permiso para realizar la acción: {accion}"
                    if hasattr(controller, 'view') and hasattr(controller.view, 'mostrar_mensaje'):
                        controller.view.mostrar_mensaje(mensaje, tipo='error')
                    elif hasattr(controller, 'view') and hasattr(controller.view, 'label'):
                        controller.view.label.setText(mensaje)
                    detalle = f"{accion} - denegado"
                    auditoria_model.registrar_evento(usuario_id, self.modulo, accion, detalle, ip)
                    from core.logger import log_error
                    log_error(f"Permiso denegado: {accion} [{self.modulo}] usuario_id={usuario_id}")
                    return None
                # --- Ejecución y registro de auditoría ---
                try:
                    resultado = func(controller, *args, **kwargs)
                    detalle = f"{accion} - éxito"
                    auditoria_model.registrar_evento(usuario_id, self.modulo, accion, detalle, ip)
                    return resultado
                except Exception as e:
                    detalle = f"{accion} - error: {e}"
                    auditoria_model.registrar_evento(usuario_id, self.modulo, accion, detalle, ip)
                    from core.logger import log_error
                    log_error(f"Error en {accion} [{self.modulo}]: {e}")
                    # Feedback visual de error
                    mensaje = f"Error interno en la acción: {accion}. Detalle: {e}"
                    if hasattr(controller, 'view') and hasattr(controller.view, 'mostrar_mensaje'):
                        controller.view.mostrar_mensaje(mensaje, tipo='error')
                    elif hasattr(controller, 'view') and hasattr(controller.view, 'label'):
                        controller.view.label.setText(mensaje)
                    raise
            # --- Documentación inline del estándar ---
            # Todos los métodos públicos decorados deben:
            # - Validar argumentos requeridos
            # - Usar feedback visual moderno (mostrar_mensaje)
            # - Registrar evento de auditoría con usuario_id, modulo, accion, detalle, ip
            # - Loggear errores críticos
            return wrapper
        return decorador

permiso_auditoria_obras = PermisoAuditoria('obras')

class ObrasController:
    """
    Controlador para el módulo de Obras.
    
    Todas las acciones públicas relevantes están decoradas con @permiso_auditoria_obras,
    lo que garantiza el registro automático en el módulo de auditoría.
    
    Patrón de auditoría:
    - Decorador @permiso_auditoria_obras('accion') en cada método público relevante.
    - El decorador valida permisos, registra el evento en auditoría (usuario, módulo, acción, detalle, ip, estado).
    - Feedback visual inmediato ante denegación o error.
    - Para casos personalizados, se puede usar self._registrar_evento_auditoria().
    
    Ejemplo de uso:
        @permiso_auditoria_obras('cambiar_estado')
        def cambiar_estado_obra(self, id_obra, nuevo_estado):
            ...
    """
    def __init__(self, model, view, db_connection, usuarios_model, usuario_actual=None, logistica_controller=None, pedidos_controller=None, produccion_controller=None):
        self.model = model
        self.view = view
        self.usuario_actual = usuario_actual
        self.usuarios_model = usuarios_model
        self.auditoria_model = AuditoriaModel(db_connection)
        self.logistica_controller = logistica_controller  # Referencia cruzada opcional
        self.pedidos_controller = pedidos_controller  # Nuevo: para gestión de pedidos
        self.produccion_controller = produccion_controller  # Nuevo: para gestión de producción
        self.view.boton_agregar.clicked.connect(self.agregar_obra)
        self.view.gantt_on_bar_clicked = self.editar_fecha_entrega
        # Conexión del botón de verificación manual (si existe en la vista)
        if hasattr(self.view, 'boton_verificar_obra'):
            self.view.boton_verificar_obra.clicked.connect(self.verificar_obra_en_sql_dialog)
        self._insertar_obras_ejemplo_si_vacio()
        self.cargar_headers_obras()
        self.cargar_datos_obras()
        self.mostrar_gantt()
        self.actualizar_calendario()

    def _registrar_evento_auditoria(self, tipo_evento, detalle, exito=True):
        """Utilidad para registrar eventos de auditoría en el formato correcto."""
        usuario_id = self.usuario_actual['id'] if self.usuario_actual and 'id' in self.usuario_actual else None
        ip = self.usuario_actual.get('ip', '') if self.usuario_actual else ''
        estado = "éxito" if exito else "error"
        detalle_final = f"{detalle} - {estado}"
        self.auditoria_model.registrar_evento(usuario_id, "obras", tipo_evento, detalle_final, ip)

    def _insertar_obras_ejemplo_si_vacio(self):
        datos = self.model.obtener_datos_obras()
        if not datos or len(datos) == 0:
            from datetime import date, timedelta
            hoy = date.today()
            ejemplos = [
                ("Edificio Central", "Constructora Sur", "Medición", (hoy-timedelta(days=10)).strftime("%Y-%m-%d"), (hoy+timedelta(days=30)).strftime("%Y-%m-%d")),
                ("Torre Norte", "Desarrollos Río", "Fabricación", (hoy-timedelta(days=20)).strftime("%Y-%m-%d"), (hoy+timedelta(days=15)).strftime("%Y-%m-%d")),
                ("Residencial Sur", "Grupo Delta", "Entrega", (hoy-timedelta(days=40)).strftime("%Y-%m-%d"), (hoy+timedelta(days=5)).strftime("%Y-%m-%d")),
            ]
            for nombre, cliente, estado, fecha, fecha_entrega in ejemplos:
                self.model.agregar_obra((nombre, cliente, estado, fecha, fecha_entrega))

    @permiso_auditoria_obras('cambiar_estado')
    def cambiar_estado_obra(self, id_obra, nuevo_estado):
        # Lógica especial para transición de estados
        if nuevo_estado == "pedido cargado" and hasattr(self, 'pedidos_controller') and self.pedidos_controller:
            # Generar pedido si no existe
            if not self.pedidos_controller.existe_pedido_para_obra(id_obra):
                self.pedidos_controller.generar_pedido_para_obra(id_obra)
        elif nuevo_estado == "en producción" and hasattr(self, 'produccion_controller') and self.produccion_controller:
            # Iniciar producción si corresponde
            self.produccion_controller.iniciar_produccion_obra(id_obra)
            # Reservar materiales si el modelo lo permite
            if hasattr(self, 'inventario_model') and hasattr(self.model, 'reservar_materiales_para_obra'):
                self.model.reservar_materiales_para_obra(id_obra)
        self.model.actualizar_estado_obra(id_obra, nuevo_estado)
        # Notificar a logística si corresponde
        if self.logistica_controller and nuevo_estado.lower() in ("entrega", "colocada", "finalizada"):
            self.logistica_controller.actualizar_por_cambio_estado_obra(id_obra, nuevo_estado)
        self.cargar_datos_obras()
        self.mostrar_gantt()
        self.actualizar_calendario()
        if hasattr(self.view, 'mostrar_mensaje'):
            self.view.mostrar_mensaje(f"Estado de la obra actualizado a {nuevo_estado}.", tipo='info')
        elif hasattr(self.view, 'label'):
            self.view.label.setText(f"Estado de la obra actualizado a {nuevo_estado}.")

    def cargar_headers_obras(self):
        try:
            headers = self.model.obtener_headers_obras()
            # Quitar columnas técnicas si es necesario (ejemplo: id, usuario_creador)
            headers_visibles = [h for h in headers if h not in ("usuario_creador",)]
            if hasattr(self.view, 'cargar_headers'):
                self.view.cargar_headers(headers_visibles)
        except Exception as e:
            mensaje = f"Error al cargar headers: {e}"
            if hasattr(self.view, 'mostrar_mensaje'):
                self.view.mostrar_mensaje(mensaje, tipo='error')
            elif hasattr(self.view, 'label'):
                self.view.label.setText(mensaje)
            self._registrar_evento_auditoria("cargar_headers", mensaje, exito=False)

    def cargar_datos_obras(self):
        try:
            datos = self.model.obtener_datos_obras()
            # Adaptar a lista de dicts para la tabla visual
            obras = []
            for d in datos:
                obra = dict(zip(self.model.obtener_headers_obras(), d))
                obras.append(obra)
            if hasattr(self.view, 'cargar_tabla_obras'):
                self.view.cargar_tabla_obras(obras)
            # Para los tests: asegurarse de que setItem se llama
            if hasattr(self.view, 'tabla_obras') and hasattr(self.view.tabla_obras, 'setItem'):
                self.view.tabla_obras.setRowCount(len(obras))
                self.view.tabla_obras.setColumnCount(len(self.model.obtener_headers_obras()))
                for row, obra in enumerate(obras):
                    for col, header in enumerate(self.model.obtener_headers_obras()):
                        self.view.tabla_obras.setItem(row, col, QTableWidgetItem(str(obra.get(header, ''))))
        except Exception as e:
            mensaje = f"Error al cargar datos: {e}"
            if hasattr(self.view, 'mostrar_mensaje'):
                self.view.mostrar_mensaje(mensaje, tipo='error')
            elif hasattr(self.view, 'label'):
                self.view.label.setText(mensaje)
            self._registrar_evento_auditoria("cargar_datos", mensaje, exito=False)

    def verificar_obra_en_sql(self, nombre, cliente):
        """Verifica si la obra existe en la base de datos SQL Server y muestra el resultado en el label."""
        try:
            datos = self.model.obtener_obra_por_nombre_cliente(nombre, cliente)
            if datos:
                if hasattr(self.view, 'mostrar_mensaje'):
                    self.view.mostrar_mensaje(f"✔ Obra encontrada en SQL: {datos}", tipo='info')
                elif hasattr(self.view, 'label'):
                    self.view.label.setText(f"✔ Obra encontrada en SQL: {datos}")
            else:
                if hasattr(self.view, 'mostrar_mensaje'):
                    self.view.mostrar_mensaje("✖ La obra NO se encuentra en la base de datos SQL.", tipo='warning')
                elif hasattr(self.view, 'label'):
                    self.view.label.setText("✖ La obra NO se encuentra en la base de datos SQL.")
        except Exception as e:
            mensaje = f"Error al verificar obra en SQL: {e}"
            if hasattr(self.view, 'mostrar_mensaje'):
                self.view.mostrar_mensaje(mensaje, tipo='error')
            elif hasattr(self.view, 'label'):
                self.view.label.setText(mensaje)
            self._registrar_evento_auditoria("verificar_obra_sql", mensaje, exito=False)

    def verificar_obra_en_sql_dialog(self):
        """Abre un diálogo para ingresar nombre y cliente y verifica la existencia en SQL Server."""
        dialog = QDialog(self.view)
        dialog.setWindowTitle("Verificar obra en SQL")
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("Nombre de la obra:"))
        nombre_input = QLineEdit()
        layout.addWidget(nombre_input)
        layout.addWidget(QLabel("Cliente:"))
        cliente_input = QLineEdit()
        layout.addWidget(cliente_input)
        btn_verificar = QPushButton("Verificar")
        estilizar_boton_icono(btn_verificar)
        btn_cancelar = QPushButton("Cancelar")
        estilizar_boton_icono(btn_cancelar)
        btn_verificar.clicked.connect(dialog.accept)
        btn_cancelar.clicked.connect(dialog.reject)
        layout.addWidget(btn_verificar)
        layout.addWidget(btn_cancelar)
        dialog.setLayout(layout)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            nombre = nombre_input.text()
            cliente = cliente_input.text()
            if not (nombre and cliente):
                if hasattr(self.view, 'mostrar_mensaje'):
                    self.view.mostrar_mensaje("Debe ingresar nombre y cliente.", tipo='warning')
                elif hasattr(self.view, 'label'):
                    self.view.label.setText("Debe ingresar nombre y cliente.")
                return
            self.verificar_obra_en_sql(nombre, cliente)

    @permiso_auditoria_obras('agregar')
    def agregar_obra(self):
        """Abre un diálogo para cargar los datos clave de la obra y la registra."""
        try:
            usuario = self.usuario_actual
            dialog = QDialog(self.view)
            dialog.setWindowTitle("Agregar nueva obra")
            dialog.setFixedSize(600, 600)
            layout = QVBoxLayout(dialog)
            label = QLabel("Ingrese los datos completos de la nueva obra:")
            label.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 8px;")
            layout.addWidget(label)

            # Usuario actual visible
            if usuario and 'username' in usuario:
                usuario_label = QLabel(f"<b>Usuario cargando: <span style='color:#2563eb'>{usuario['username']} ({usuario.get('rol','')})</span></b>")
                usuario_label.setStyleSheet("font-size: 13px; margin-bottom: 8px; background: #f1f5f9; border-radius: 8px; padding: 4px 8px;")
                layout.addWidget(usuario_label)

            from PyQt6.QtWidgets import QFormLayout, QDateEdit, QCheckBox, QSpinBox
            from PyQt6.QtCore import QDate
            form = QFormLayout()
            nombre_input = QLineEdit()
            apellido_input = QLineEdit()
            cliente_input = QLineEdit()
            direccion_input = QLineEdit()
            telefono_input = QLineEdit()
            cantidad_aberturas_input = QLineEdit()
            fecha_compra_input = QDateEdit()
            fecha_compra_input.setCalendarPopup(True)
            fecha_compra_input.setDate(QDate.currentDate())
            pago_completo_input = QCheckBox("Pago completo")
            pago_porcentaje_input = QLineEdit()
            monto_usd_input = QLineEdit()
            monto_ars_input = QLineEdit()
            estado_input = QComboBox()
            estado_input.addItems(["Medición", "Fabricación", "Entrega"])
            # Campos nuevos para planificación
            fecha_medicion_input = QDateEdit()
            fecha_medicion_input.setCalendarPopup(True)
            fecha_medicion_input.setDate(QDate.currentDate())
            dias_entrega_input = QSpinBox()
            dias_entrega_input.setMinimum(1)
            dias_entrega_input.setMaximum(365)
            dias_entrega_input.setValue(90)
            fecha_entrega_input = QDateEdit()
            fecha_entrega_input.setCalendarPopup(True)
            # Se actualizará automáticamente al cambiar fecha_medicion o dias_entrega
            def actualizar_fecha_entrega():
                fecha_med = fecha_medicion_input.date().toPyDate()
                dias = dias_entrega_input.value()
                nueva_fecha = fecha_med + datetime.timedelta(days=dias)
                fecha_entrega_input.setDate(QDate(nueva_fecha.year, nueva_fecha.month, nueva_fecha.day))
            fecha_medicion_input.dateChanged.connect(actualizar_fecha_entrega)
            dias_entrega_input.valueChanged.connect(actualizar_fecha_entrega)
            actualizar_fecha_entrega()

            nombre_input.setPlaceholderText("Nombre de la obra")
            apellido_input.setPlaceholderText("Apellido del cliente")
            cliente_input.setPlaceholderText("Cliente o razón social")
            direccion_input.setPlaceholderText("Dirección de la obra")
            telefono_input.setPlaceholderText("Teléfono de contacto")
            cantidad_aberturas_input.setPlaceholderText("Cantidad de aberturas")
            pago_porcentaje_input.setPlaceholderText("% pago (si no es completo)")
            monto_usd_input.setPlaceholderText("Monto en USD")
            monto_ars_input.setPlaceholderText("Monto en ARS")

            form.addRow("Nombre:", nombre_input)
            form.addRow("Apellido:", apellido_input)
            form.addRow("Cliente:", cliente_input)
            form.addRow("Dirección:", direccion_input)
            form.addRow("Teléfono:", telefono_input)
            form.addRow("Cantidad de aberturas:", cantidad_aberturas_input)
            form.addRow("Fecha de compra:", fecha_compra_input)
            form.addRow("Pago completo:", pago_completo_input)
            form.addRow("Pago en %:", pago_porcentaje_input)
            form.addRow("Monto USD:", monto_usd_input)
            form.addRow("Monto ARS:", monto_ars_input)
            form.addRow("Estado inicial:", estado_input)
            # Nuevos campos
            form.addRow("Fecha de medición:", fecha_medicion_input)
            form.addRow("Días de entrega:", dias_entrega_input)
            form.addRow("Fecha de entrega:", fecha_entrega_input)
            layout.addLayout(form)

            # Botones
            btns_layout = QHBoxLayout()
            btn_guardar = QPushButton()
            btn_guardar.setIcon(QIcon("img/plus_icon.svg"))
            btn_guardar.setToolTip("Guardar obra")
            estilizar_boton_icono(btn_guardar, tam_icono=28, tam_boton=48)
            btn_guardar.clicked.connect(dialog.accept)
            btn_cancelar = QPushButton()
            btn_cancelar.setIcon(QIcon("img/reject.svg"))
            btn_cancelar.setToolTip("Cancelar")
            estilizar_boton_icono(btn_cancelar, tam_icono=28, tam_boton=48)
            btn_cancelar.clicked.connect(dialog.reject)
            btns_layout.addWidget(btn_guardar)
            btns_layout.addWidget(btn_cancelar)
            layout.addLayout(btns_layout)

            dialog.setLayout(layout)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # --- SIMULACIÓN DE ERROR DE BASE DE DATOS (descomentar para probar feedback visual) ---
                # raise Exception("Simulación de error de base de datos en alta de obra (prueba de feedback visual)")
                # --- FIN SIMULACIÓN ---
                nombre = nombre_input.text().strip()
                apellido = apellido_input.text().strip()
                cliente = cliente_input.text().strip()
                direccion = direccion_input.text().strip()
                telefono = telefono_input.text().strip()
                cantidad_aberturas = cantidad_aberturas_input.text().strip()
                fecha_compra = fecha_compra_input.date().toString("yyyy-MM-dd")
                pago_completo = pago_completo_input.isChecked()
                pago_porcentaje = pago_porcentaje_input.text().strip()
                monto_usd = monto_usd_input.text().strip()
                monto_ars = monto_ars_input.text().strip()
                estado = estado_input.currentText()
                fecha_medicion = fecha_medicion_input.date().toString("yyyy-MM-dd")
                dias_entrega = dias_entrega_input.value()
                fecha_entrega = fecha_entrega_input.date().toString("yyyy-MM-dd")
                # Validación básica
                if not (nombre and cliente and direccion and telefono and cantidad_aberturas and fecha_compra and estado and fecha_medicion and dias_entrega and fecha_entrega):
                    if hasattr(self.view, 'mostrar_mensaje'):
                        self.view.mostrar_mensaje("Por favor, complete todos los campos obligatorios.", tipo='warning')
                    elif hasattr(self.view, 'label'):
                        self.view.label.setText("Por favor, complete todos los campos obligatorios.")
                    return
                # Guardar todos los campos en el modelo
                self.model.agregar_obra((
                    nombre, cliente, estado, fecha_compra, cantidad_aberturas, pago_completo, pago_porcentaje, monto_usd, monto_ars,
                    fecha_medicion, dias_entrega, fecha_entrega, self.usuario_actual['id'] if self.usuario_actual else None
                ))
                # Registrar en auditoría con formato unificado
                self._registrar_evento_auditoria("alta_obra", f"Alta de obra: {nombre}")
                mensaje = (
                    f"<b>Obra agregada exitosamente:</b><br>"
                    f"<ul style='margin:0 0 0 16px;padding:0'>"
                    f"<li><b>Nombre:</b> {nombre}</li>"
                    f"<li><b>Apellido:</b> {apellido}</li>"
                    f"<li><b>Cliente:</b> {cliente}</li>"
                    f"<li><b>Dirección:</b> {direccion}</li>"
                    f"<li><b>Teléfono:</b> {telefono}</li>"
                    f"<li><b>Cant. aberturas:</b> {cantidad_aberturas}</li>"
                    f"<li><b>Fecha compra:</b> {fecha_compra}</li>"
                    f"<li><b>Pago completo:</b> {'Sí' if pago_completo else 'No'} {pago_porcentaje+'%' if pago_porcentaje else ''}</li>"
                    f"<li><b>Monto USD:</b> {monto_usd}</li>"
                    f"<li><b>Monto ARS:</b> {monto_ars}</li>"
                    f"<li><b>Fecha medición:</b> {fecha_medicion}</li>"
                    f"<li><b>Días entrega:</b> {dias_entrega}</li>"
                    f"<li><b>Fecha entrega:</b> {fecha_entrega}</li>"
                    f"<li><b>Estado inicial:</b> {estado}</li>"
                    f"</ul>"
                    f"<br>" 
                    f"<span style='color:#2563eb'><b>¿Qué desea hacer ahora?</b></span><br>"
                    f"- <b>Asignar materiales</b> a la obra desde el menú de acciones.<br>"
                    f"- <b>Programar cronograma</b> en la pestaña Cronograma.<br>"
                    f"- <b>Ver la obra</b> en la tabla principal.<br>"
                )
                if hasattr(self.view, 'mostrar_mensaje'):
                    self.view.mostrar_mensaje(mensaje, tipo='exito', duracion=9000)
                else:
                    self.view.label.setText(mensaje)
                self.cargar_datos_obras()
                self.mostrar_gantt()
        except Exception as e:
            from core.logger import log_error
            log_error(f"Error al agregar obra: {e}")
            if hasattr(self.view, 'mostrar_mensaje'):
                self.view.mostrar_mensaje(f"Error al agregar la obra: {e}", tipo='error')
            elif hasattr(self.view, 'label'):
                self.view.label.setText("Error al agregar la obra.")
            # Registrar error en auditoría con formato unificado
            self._registrar_evento_auditoria("alta_obra", f"Error alta obra: {e}", exito=False)

    def editar_fecha_entrega(self, id_obra, fecha_actual):
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton
        dialog = QDialog(self.view)
        dialog.setWindowTitle("Editar fecha de entrega")
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel(f"Fecha actual: {fecha_actual}"))
        fecha_input = QLineEdit(fecha_actual)
        layout.addWidget(QLabel("Nueva fecha de entrega (YYYY-MM-DD):"))
        layout.addWidget(fecha_input)
        btn_guardar = QPushButton("Guardar")
        estilizar_boton_icono(btn_guardar)
        btn_cancelar = QPushButton("Cancelar")
        estilizar_boton_icono(btn_cancelar)
        btn_guardar.clicked.connect(dialog.accept)
        btn_cancelar.clicked.connect(dialog.reject)
        layout.addWidget(btn_guardar)
        layout.addWidget(btn_cancelar)
        dialog.setLayout(layout)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            nueva_fecha = fecha_input.text()
            # Obtener datos actuales de la obra
            datos = self.model.obtener_obra_por_id(id_obra)
            if datos:
                nombre, cliente, estado = datos[1], datos[2], datos[3]
                self.model.actualizar_obra(id_obra, nombre, cliente, estado, nueva_fecha)
                self.mostrar_gantt()

    def editar_obra(self, id_obra):
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QFormLayout, QLineEdit, QDateEdit, QSpinBox, QCheckBox, QComboBox, QPushButton
        from PyQt6.QtCore import QDate
        datos = self.model.obtener_obra_por_id(id_obra)
        if not datos:
            if hasattr(self.view, 'mostrar_mensaje'):
                self.view.mostrar_mensaje("No se encontró la obra para editar.", tipo='error')
            elif hasattr(self.view, 'label'):
                self.view.label.setText("No se encontró la obra para editar.")
            return
        # Mapear datos actuales
        nombre, cliente, estado, fecha_compra, cantidad_aberturas, pago_completo, pago_porcentaje, monto_usd, monto_ars, fecha_medicion, dias_entrega, fecha_entrega = (
            datos[1], datos[2], datos[3], datos[4], datos[6], datos[8], datos[9], datos[10], datos[11], datos[14], datos[15], datos[5]
        )
        dialog = QDialog(self.view)
        dialog.setWindowTitle("Editar obra")
        layout = QVBoxLayout(dialog)
        form = QFormLayout()
        nombre_input = QLineEdit(nombre)
        cliente_input = QLineEdit(cliente)
        estado_input = QComboBox()
        estado_input.addItems(["Medición", "Fabricación", "Entrega"])
        estado_input.setCurrentText(estado)
        fecha_compra_input = QDateEdit()
        fecha_compra_input.setDate(QDate.fromString(str(fecha_compra), "yyyy-MM-dd"))
        cantidad_aberturas_input = QLineEdit(str(cantidad_aberturas))
        pago_completo_input = QCheckBox("Pago completo")
        pago_completo_input.setChecked(bool(pago_completo))
        pago_porcentaje_input = QLineEdit(str(pago_porcentaje))
        monto_usd_input = QLineEdit(str(monto_usd))
        monto_ars_input = QLineEdit(str(monto_ars))
        fecha_medicion_input = QDateEdit()
        fecha_medicion_input.setDate(QDate.fromString(str(fecha_medicion), "yyyy-MM-dd"))
        dias_entrega_input = QSpinBox()
        dias_entrega_input.setMinimum(1)
        dias_entrega_input.setMaximum(365)
        dias_entrega_input.setValue(int(dias_entrega) if dias_entrega else 90)
        fecha_entrega_input = QDateEdit()
        fecha_entrega_input.setDate(QDate.fromString(str(fecha_entrega), "yyyy-MM-dd"))
        # Lógica de actualización automática
        def actualizar_fecha_entrega():
            fecha_med = fecha_medicion_input.date().toPyDate()
            dias = dias_entrega_input.value()
            nueva_fecha = fecha_med + datetime.timedelta(days=dias)
            fecha_entrega_input.setDate(QDate(nueva_fecha.year, nueva_fecha.month, nueva_fecha.day))
        fecha_medicion_input.dateChanged.connect(actualizar_fecha_entrega)
        dias_entrega_input.valueChanged.connect(actualizar_fecha_entrega)
        # Formulario
        form.addRow("Nombre:", nombre_input)
        form.addRow("Cliente:", cliente_input)
        form.addRow("Estado:", estado_input)
        form.addRow("Fecha compra:", fecha_compra_input)
        form.addRow("Cantidad aberturas:", cantidad_aberturas_input)
        form.addRow("Pago completo:", pago_completo_input)
        form.addRow("Pago en %:", pago_porcentaje_input)
        form.addRow("Monto USD:", monto_usd_input)
        form.addRow("Monto ARS:", monto_ars_input)
        form.addRow("Fecha medición:", fecha_medicion_input)
        form.addRow("Días entrega:", dias_entrega_input)
        form.addRow("Fecha entrega:", fecha_entrega_input)
        layout.addLayout(form)
        btn_guardar = QPushButton("Guardar cambios")
        estilizar_boton_icono(btn_guardar, tam_icono=24, tam_boton=40)
        btn_guardar.clicked.connect(dialog.accept)
        layout.addWidget(btn_guardar)
        dialog.setLayout(layout)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Guardar cambios
            self.model.actualizar_obra_completa(
                id_obra,
                nombre_input.text().strip(),
                cliente_input.text().strip(),
                estado_input.currentText(),
                fecha_compra_input.date().toString("yyyy-MM-dd"),
                cantidad_aberturas_input.text().strip(),
                pago_completo_input.isChecked(),
                pago_porcentaje_input.text().strip(),
                monto_usd_input.text().strip(),
                monto_ars_input.text().strip(),
                fecha_medicion_input.date().toString("yyyy-MM-dd"),
                dias_entrega_input.value(),
                fecha_entrega_input.date().toString("yyyy-MM-dd")
            )
            # Registrar en auditoría con formato unificado
            self._registrar_evento_auditoria("editar_obra", f"Edición de obra: {id_obra}")
            self.cargar_datos_obras()
            self.mostrar_gantt()

    def mostrar_gantt(self):
        datos = self.model.obtener_datos_obras()
        # Adaptar a lista de dicts con los campos requeridos por el Gantt
        obras = []
        for d in datos:
            # d: (id, nombre, cliente, estado, fecha, fecha_entrega, ...)
            obra = {
                'id': d[0],
                'nombre': d[1],
                'cliente': d[2],
                'estado': d[3],
                'fecha': d[4],
                'fecha_entrega': d[5],
            }
            obras.append(obra)
        if hasattr(self.view, 'cronograma_view'):
            self.view.cronograma_view.set_obras(obras)

    @staticmethod
    def _parse_fecha(fecha_str):
        import datetime
        if not fecha_str:
            return None
        try:
            return datetime.datetime.strptime(str(fecha_str), "%Y-%m-%d").date()
        except Exception:
            return None

    def actualizar_calendario(self):
        """Actualiza el calendario con las fechas del cronograma."""
        try:
            cronograma = self.model.obtener_todas_las_fechas()
            for fecha in cronograma:
                # Aquí puedes agregar lógica para resaltar fechas en el calendario
                print(f"Fecha programada: {fecha}")
        except Exception as e:
            mensaje = f"Error al actualizar calendario: {e}"
            if hasattr(self.view, 'mostrar_mensaje'):
                self.view.mostrar_mensaje(mensaje, tipo='error')
            elif hasattr(self.view, 'label'):
                self.view.label.setText(mensaje)
            self._registrar_evento_auditoria("actualizar_calendario", mensaje, exito=False)

    @permiso_auditoria_obras('crear')
    def asociar_material_a_obra(self, id_obra, id_item, cantidad_necesaria):
        try:
            # Instanciar modelos si no existen como atributos
            inventario_model = getattr(self, 'inventario_model', None)
            if inventario_model is None:
                from modules.inventario.model import InventarioModel
                inventario_model = InventarioModel(self.model.db_connection)
            auditoria_model = getattr(self, 'auditoria_model', None)
            if auditoria_model is None:
                from modules.auditoria.model import AuditoriaModel
                auditoria_model = AuditoriaModel(self.model.db_connection)
            # 1. Verificar stock actual
            stock_actual = inventario_model.obtener_stock_item(id_item)
            if stock_actual >= cantidad_necesaria:
                inventario_model.reservar_stock(id_item, cantidad_necesaria, id_obra)
                estado = "Reservado"
            else:
                estado = "Pendiente"
            # 2. Asociar material a la obra
            self.model.insertar_material_obra(id_obra, id_item, cantidad_necesaria, estado)
            # 3. Registrar movimiento de stock solo si se reservó
            if estado == "Reservado":
                inventario_model.registrar_movimiento(
                    id_item, -cantidad_necesaria, "Reserva", id_obra
                )
            # 4. Registrar auditoría con formato unificado
            self._registrar_evento_auditoria("asociar_material", f"Asoció material {id_item} a obra {id_obra} (estado: {estado})")
            # 5. Feedback UI
            if hasattr(self.view, 'mostrar_mensaje'):
                self.view.mostrar_mensaje(f"✔ Material {id_item} asociado a obra. Estado: {estado}", tipo="exito")
            else:
                self.view.label.setText(f"✔ Material {id_item} asociado a obra. Estado: {estado}")
        except Exception as e:
            mensaje = "❌ Error al asociar material: " + str(e)
            if hasattr(self.view, 'mostrar_mensaje'):
                self.view.mostrar_mensaje(mensaje, tipo="error")
            elif hasattr(self.view, 'label'):
                self.view.label.setText(mensaje)
            from core.logger import Logger
            Logger().error("Error al asociar material: " + str(e))
            # Registrar error en auditoría con formato unificado
            self._registrar_evento_auditoria("asociar_material", f"Error asociar material: {e}", exito=False)

    @permiso_auditoria_obras('exportar')
    def exportar_cronograma(self, formato, id_obra):
        try:
            mensaje = self.model.exportar_cronograma(formato, id_obra)
            self._registrar_evento_auditoria("exportar_cronograma", f"Exportación de cronograma de obra {id_obra} a {formato}")
            if hasattr(self.view, 'mostrar_mensaje'):
                self.view.mostrar_mensaje(mensaje, tipo='exito')
            else:
                self.view.label.setText(mensaje)
        except Exception as e:
            self._registrar_evento_auditoria("exportar_cronograma", f"Error exportando cronograma de obra {id_obra}: {e}", exito=False)
            mensaje = f"Error al exportar cronograma: {e}"
            if hasattr(self.view, 'mostrar_mensaje'):
                self.view.mostrar_mensaje(mensaje, tipo='error')
            elif hasattr(self.view, 'label'):
                self.view.label.setText(mensaje)

    @permiso_auditoria_obras('eliminar')
    def eliminar_etapa_cronograma(self, id_etapa):
        try:
            self.model.eliminar_etapa_cronograma(id_etapa)
            self._registrar_evento_auditoria("eliminar_etapa", f"Eliminación de etapa de cronograma {id_etapa}")
            if hasattr(self.view, 'mostrar_mensaje'):
                self.view.mostrar_mensaje(f"Etapa {id_etapa} eliminada correctamente.", tipo='exito')
            else:
                self.view.label.setText(f"Etapa {id_etapa} eliminada correctamente.")
        except Exception as e:
            self._registrar_evento_auditoria("eliminar_etapa", f"Error eliminando etapa de cronograma {id_etapa}: {e}", exito=False)
            mensaje = f"Error al eliminar etapa: {e}"
            if hasattr(self.view, 'mostrar_mensaje'):
                self.view.mostrar_mensaje(mensaje, tipo='error')
            elif hasattr(self.view, 'label'):
                self.view.label.setText(mensaje)
