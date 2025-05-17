from PyQt6.QtWidgets import QTableWidgetItem, QDialog, QVBoxLayout, QTableWidget, QFormLayout, QLineEdit, QHBoxLayout, QPushButton, QMessageBox
from PyQt6 import QtGui
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
                usuario_model = getattr(controller, 'usuarios_model', None)
                auditoria_model = getattr(controller, 'auditoria_model', None)
                usuario = getattr(controller, 'usuario_actual', None)
                # Nueva validación: solo admin/supervisor o usuarios con permiso al módulo
                if not usuario or not usuario_model:
                    if hasattr(controller, 'view') and hasattr(controller.view, 'label'):
                        controller.view.label.setText(f"No tiene permiso para realizar la acción: {accion}")
                    return None
                if usuario['rol'] not in ('admin', 'supervisor'):
                    modulos_permitidos = usuario_model.obtener_modulos_permitidos(usuario)
                    if self.modulo not in modulos_permitidos:
                        if hasattr(controller, 'view') and hasattr(controller.view, 'label'):
                            controller.view.label.setText(f"No tiene permiso para acceder al módulo: {self.modulo}")
                        return None
                if not usuario_model.tiene_permiso(usuario, self.modulo, accion):
                    if hasattr(controller, 'view') and hasattr(controller.view, 'label'):
                        controller.view.label.setText(f"No tiene permiso para realizar la acción: {accion}")
                    return None
                resultado = func(controller, *args, **kwargs)
                if auditoria_model:
                    ip = usuario.get('ip', '') if usuario else ''
                    auditoria_model.registrar_evento(self.modulo, accion, f"Acción realizada: {accion}", ip)
                return resultado
            return wrapper
        return decorador

permiso_auditoria_inventario = PermisoAuditoria('inventario')

class InventarioController:
    def __init__(self, model, view, db_connection, usuario_actual=None):
        self.model = model
        self.view = view
        self.usuario_actual = usuario_actual  # dict con id, nombre, rol, ip, etc.
        self.usuarios_model = UsuariosModel(db_connection)
        self.auditoria_model = AuditoriaModel(db_connection)
        self.db_connection = db_connection

        # Conexión de señales de la vista a métodos del controlador
        self.view.nuevo_item_signal.connect(self.agregar_item)
        self.view.ver_movimientos_signal.connect(self.ver_movimientos)
        self.view.reservar_signal.connect(self.reservar_item)
        self.view.exportar_excel_signal.connect(lambda: self.exportar_inventario("excel"))
        self.view.exportar_pdf_signal.connect(lambda: self.exportar_inventario("pdf"))
        self.view.buscar_signal.connect(self.buscar_item)
        self.view.generar_qr_signal.connect(self.generar_qr_para_item)
        self.view.generar_qr_signal.connect(self.ver_qr_item_seleccionado)
        self.view.generar_qr_signal.connect(self.asociar_qr_a_perfil)
        self.view.actualizar_signal.connect(self.actualizar_inventario)
        self.view.ajustar_stock_signal.connect(self.ajustar_stock)
        self.view.reservar_signal.connect(self.abrir_reserva_lote_perfiles)

        self.actualizar_inventario()
        self.cargar_productos()

    def cargar_productos(self):
        productos = self.model.obtener_productos()  # Debe devolver lista de dicts con los headers correctos
        self.view.cargar_items(productos)

    @permiso_auditoria_inventario('ver')
    def actualizar_inventario(self):
        datos = self.model.obtener_items()
        print(f"[DEBUG] Registros obtenidos de inventario: {len(datos)}")
        self.view.tabla_inventario.setRowCount(len(datos))
        self.view.tabla_inventario.setColumnCount(18)  # Ajusta según las columnas de inventario_perfiles
        if not datos:
            self.view.label_titulo.setText("No hay datos de inventario para mostrar.")
        else:
            self.view.label_titulo.setText("INVENTORY")
        for row, item in enumerate(datos):
            for col, value in enumerate(item):
                self.view.tabla_inventario.setItem(row, col, QTableWidgetItem(str(value)))

    def cargar_datos_inventario(self, offset=0, limite=500):
        items = self.model.obtener_items_por_lotes(offset, limite)
        self.view.cargar_items(items)

    def _solicitud_aprobacion_o_ejecucion(self, tipo_accion, datos_accion, funcion_ejecucion, *args, **kwargs):
        """
        Si el usuario es 'usuario', crea una solicitud de aprobación y muestra feedback.
        Si es supervisor/admin, ejecuta la acción real.
        """
        usuario = self.usuario_actual
        if usuario and usuario.get('rol') == 'usuario':
            # Insertar solicitud en la tabla solicitudes_aprobacion
            import json
            try:
                self.model.db.ejecutar_query(
                    """
                    INSERT INTO solicitudes_aprobacion (id_usuario, modulo, tipo_accion, datos_json)
                    VALUES (?, ?, ?, ?)
                    """,
                    (usuario['id'], 'inventario', tipo_accion, json.dumps(datos_accion))
                )
                if hasattr(self.view, 'mostrar_mensaje'):
                    self.view.mostrar_mensaje("La acción requiere aprobación de un supervisor. Solicitud registrada y pendiente de aprobación.", tipo='info')
                else:
                    self.view.label.setText("La acción requiere aprobación de un supervisor. Solicitud registrada.")
                if hasattr(self, 'auditoria_model'):
                    ip = usuario.get('ip', '') if usuario else ''
                    self.auditoria_model.registrar_evento('inventario', f'solicitud_aprobacion_{tipo_accion}', str(datos_accion), ip)
            except Exception as e:
                if hasattr(self.view, 'mostrar_mensaje'):
                    self.view.mostrar_mensaje(f"Error al registrar la solicitud de aprobación: {e}", tipo='error')
                else:
                    self.view.label.setText(f"Error al registrar la solicitud de aprobación: {e}")
            return
        # Si es supervisor/admin, ejecutar la acción real
        return funcion_ejecucion(*args, **kwargs)

    @permiso_auditoria_inventario('editar')
    def agregar_item(self):
        def ejecutar():
            try:
                datos = self.view.abrir_formulario_nuevo_item()
                campos_obligatorios = ["codigo", "nombre", "tipo_material", "unidad", "stock_actual", "stock_minimo", "ubicacion", "descripcion"]
                if not datos or not all(datos.get(campo) for campo in campos_obligatorios):
                    if hasattr(self.view, 'mostrar_mensaje'):
                        self.view.mostrar_mensaje("Todos los campos son obligatorios para agregar un ítem.")
                    else:
                        self.view.label.setText("Todos los campos son obligatorios para agregar un ítem.")
                    return
                codigo = datos.get("codigo")
                if not isinstance(codigo, str) or not codigo.strip():
                    if hasattr(self.view, 'mostrar_mensaje'):
                        self.view.mostrar_mensaje("El código del ítem es obligatorio y debe ser texto.")
                    else:
                        self.view.label.setText("El código del ítem es obligatorio y debe ser texto.")
                    return
                if self.model.obtener_item_por_codigo(codigo):
                    if hasattr(self.view, 'mostrar_mensaje'):
                        self.view.mostrar_mensaje("Ya existe un ítem con ese código.")
                    else:
                        self.view.label.setText("Ya existe un ítem con el mismo código.")
                    return
                try:
                    self.model.agregar_item(tuple(datos.get(campo, None) for campo in ["codigo", "nombre", "tipo_material", "unidad", "stock_actual", "stock_minimo", "ubicacion", "descripcion", "qr", "imagen_referencia"]))
                except Exception as e:
                    if hasattr(self.view, 'mostrar_mensaje'):
                        self.view.mostrar_mensaje(f"Error al agregar ítem en la base de datos: {e}")
                    else:
                        self.view.label.setText(f"Error al agregar ítem en la base de datos: {e}")
                    usuario = self.usuario_actual
                    ip = usuario.get('ip', '') if usuario else ''
                    self.auditoria_model.registrar_evento('inventario', 'error', f"Error al agregar ítem: {e}", ip)
                    return
                try:
                    item_row = self.model.obtener_item_por_codigo(codigo)
                    usuario = self.usuario_actual
                    nombre_usuario = ''
                    if usuario and isinstance(usuario, dict):
                        nombre_usuario = usuario.get("nombre", "")
                    if item_row:
                        self.model.registrar_movimiento((item_row[0][0], "alta", datos["stock_actual"], nombre_usuario, "Alta inicial de ítem", None))
                except Exception as e:
                    usuario = self.usuario_actual
                    ip = usuario.get('ip', '') if usuario else ''
                    self.auditoria_model.registrar_evento('inventario', 'error', f"Error al registrar movimiento de alta: {e}", ip)
                usuario = self.usuario_actual
                ip = usuario.get('ip', '') if usuario else ''
                self.auditoria_model.registrar_evento('inventario', 'alta', f"Ítem agregado: {codigo}", ip)
                self.actualizar_inventario()
                if hasattr(self.view, 'mostrar_mensaje'):
                    self.view.mostrar_mensaje(f"Ítem '{codigo}' agregado correctamente.")
                else:
                    self.view.label.setText(f"Ítem '{codigo}' agregado correctamente.")
            except Exception as e:
                if hasattr(self.view, 'mostrar_mensaje'):
                    self.view.mostrar_mensaje(f"Error al agregar ítem: {e}")
                else:
                    self.view.label.setText(f"Error al agregar ítem: {e}")
                usuario = self.usuario_actual
                ip = usuario.get('ip', '') if usuario else ''
                self.auditoria_model.registrar_evento('inventario', 'error', f"Error al agregar ítem: {e}", ip)
        datos = self.view.abrir_formulario_nuevo_item()
        if not datos:
            return
        return self._solicitud_aprobacion_o_ejecucion('agregar', datos, ejecutar)

    @permiso_auditoria_inventario('editar')
    def reservar_item(self):
        def ejecutar():
            try:
                dialog = QDialog(self.view)
                dialog.setWindowTitle("Reservar material para obra")
                layout = QVBoxLayout()
                form_layout = QFormLayout()
                obra_input = QLineEdit()
                id_item_input = QLineEdit()
                cantidad_input = QLineEdit()
                codigo_reserva_input = QLineEdit()
                form_layout.addRow("Obra (ID o nombre):", obra_input)
                form_layout.addRow("ID de material:", id_item_input)
                form_layout.addRow("Cantidad a reservar:", cantidad_input)
                form_layout.addRow("Código de reserva único:", codigo_reserva_input)
                layout.addLayout(form_layout)
                botones_layout = QHBoxLayout()
                reservar_button = QPushButton("Reservar")
                cancelar_button = QPushButton("Cancelar")
                botones_layout.addWidget(reservar_button)
                botones_layout.addWidget(cancelar_button)
                layout.addLayout(botones_layout)
                dialog.setLayout(layout)
                def on_reservar():
                    obra = obra_input.text().strip()
                    id_item = id_item_input.text().strip()
                    cantidad = cantidad_input.text().strip()
                    codigo_reserva = codigo_reserva_input.text().strip()
                    if not (obra and id_item and cantidad and codigo_reserva):
                        self.view.mostrar_mensaje("Complete todos los campos para reservar.")
                        return
                    try:
                        cantidad_int = int(cantidad)
                        if cantidad_int <= 0:
                            self.view.mostrar_mensaje("La cantidad debe ser mayor a cero.")
                            return
                    except Exception:
                        self.view.mostrar_mensaje("Ingrese un número válido para la cantidad.")
                        return
                    item_row = self.model.obtener_item_por_codigo(id_item) if not id_item.isdigit() else self.model.db.ejecutar_query("SELECT * FROM inventario_perfiles WHERE id = ?", (id_item,))
                    if not item_row:
                        self.view.mostrar_mensaje("No se encontró el material especificado.")
                        return
                    stock_actual = item_row[0][5] if len(item_row[0]) > 5 else None
                    if stock_actual is None or int(stock_actual) < cantidad_int:
                        self.view.mostrar_mensaje("Stock insuficiente para reservar la cantidad solicitada.")
                        return
                    reservas_existentes = self.model.db.ejecutar_query(
                        "SELECT COUNT(*) FROM reservas_materiales WHERE (codigo_reserva = ? OR (referencia_obra = ? AND id_item = ?)) AND estado = 'activa'",
                        (codigo_reserva, obra, id_item)
                    )
                    if reservas_existentes and reservas_existentes[0][0] > 0:
                        self.view.mostrar_mensaje("Ya existe una reserva activa para este material y obra, o el código ya está en uso.")
                        return
                    try:
                        self.model.db.ejecutar_query(
                            "INSERT INTO reservas_materiales (id_item, cantidad_reservada, referencia_obra, estado, codigo_reserva) VALUES (?, ?, ?, ?, ?)",
                            (id_item, cantidad_int, obra, 'activa', codigo_reserva)
                        )
                    except Exception as e:
                        usuario = self.usuario_actual
                        ip = usuario.get('ip', '') if usuario else ''
                        self.view.mostrar_mensaje(f"Error al registrar la reserva: {e}")
                        self.auditoria_model.registrar_evento('inventario', 'error', f'error reserva material {id_item} para obra {obra} (código: {codigo_reserva}): {e}', ip)
                        return
                    usuario = self.usuario_actual
                    ip = usuario.get('ip', '') if usuario else ''
                    self.auditoria_model.registrar_evento('inventario', 'info', f'reserva material {id_item} para obra {obra} (código: {codigo_reserva})', ip)
                    self.actualizar_inventario()
                    self.view.mostrar_mensaje(f"Reserva realizada correctamente para obra {obra}.")
                    dialog.accept()
                reservar_button.clicked.connect(on_reservar)
                cancelar_button.clicked.connect(dialog.reject)
                dialog.exec()
            except Exception as e:
                self.view.mostrar_mensaje(f"Error al abrir la ventana de reserva: {e}")
        dialog = QDialog(self.view)
        dialog.setWindowTitle("Reservar material para obra")
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        obra_input = QLineEdit()
        id_item_input = QLineEdit()
        cantidad_input = QLineEdit()
        codigo_reserva_input = QLineEdit()
        form_layout.addRow("Obra (ID o nombre):", obra_input)
        form_layout.addRow("ID de material:", id_item_input)
        form_layout.addRow("Cantidad a reservar:", cantidad_input)
        form_layout.addRow("Código de reserva único:", codigo_reserva_input)
        layout.addLayout(form_layout)
        botones_layout = QHBoxLayout()
        reservar_button = QPushButton("Reservar")
        cancelar_button = QPushButton("Cancelar")
        botones_layout.addWidget(reservar_button)
        botones_layout.addWidget(cancelar_button)
        layout.addLayout(botones_layout)
        dialog.setLayout(layout)
        datos_accion = {}
        def on_reservar():
            datos_accion['obra'] = obra_input.text().strip()
            datos_accion['id_item'] = id_item_input.text().strip()
            datos_accion['cantidad'] = cantidad_input.text().strip()
            datos_accion['codigo_reserva'] = codigo_reserva_input.text().strip()
            dialog.accept()
        reservar_button.clicked.connect(on_reservar)
        cancelar_button.clicked.connect(dialog.reject)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return self._solicitud_aprobacion_o_ejecucion('reservar', datos_accion, ejecutar)

    @permiso_auditoria_inventario('editar')
    def ajustar_stock(self):
        def ejecutar():
            try:
                dialog = self.view.abrir_ajustar_stock_dialog()
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    datos_ajuste = dialog.obtener_datos_ajuste_stock()
                    for ajuste in datos_ajuste:
                        codigo = ajuste["codigo"]
                        cantidad = ajuste["cantidad"]
                        if not codigo or cantidad is None:
                            self.view.label.setText("Datos incompletos en el ajuste de stock.")
                            continue
                        try:
                            self.model.ajustar_stock(codigo, cantidad)
                            self.view.label.setText(f"Stock ajustado para {codigo} (+{cantidad}).")
                        except Exception as e:
                            usuario = self.usuario_actual
                            ip = usuario.get('ip', '') if usuario else ''
                            self.view.label.setText(f"Error al ajustar stock de {codigo}: {e}")
                            self.auditoria_model.registrar_evento('inventario', 'error', f"Error al ajustar stock: {e}", ip)
                    self.actualizar_inventario()
            except Exception as e:
                self.view.label.setText(f"Error al ajustar el stock: {e}")
        dialog = self.view.abrir_ajustar_stock_dialog()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            datos_ajuste = dialog.obtener_datos_ajuste_stock()
            return self._solicitud_aprobacion_o_ejecucion('ajustar_stock', datos_ajuste, ejecutar)

    @permiso_auditoria_inventario('ver')
    def ver_movimientos(self):
        try:
            id_item = self.view.obtener_id_item_seleccionado()
            if id_item:
                movimientos = self.model.obtener_movimientos(id_item)
                self.view.mostrar_movimientos(movimientos)
                self.view.label.setText("")
            else:
                self.view.label.setText("Seleccione un ítem para ver sus movimientos.")
        except Exception as e:
            self.view.label.setText(f"Error al mostrar movimientos: {e}")

    @permiso_auditoria_inventario('ver')
    def buscar_item(self):
        try:
            codigo = self.view.buscar_input.text()
            if not codigo:
                self.view.label.setText("Ingrese un código para buscar.")
                return
            item = self.model.obtener_item_por_codigo(codigo)
            if item:
                self.view.tabla_inventario.setRowCount(1)
                for col, value in enumerate(item[0]):
                    self.view.tabla_inventario.setItem(0, col, QTableWidgetItem(str(value)))
                self.view.label.setText("")
            else:
                self.view.label.setText("Ítem no encontrado.")
        except Exception as e:
            self.view.label.setText(f"Error al buscar ítem: {e}")

    @permiso_auditoria_inventario('ver')
    def exportar_inventario(self, formato):
        try:
            resultado = self.model.exportar_inventario(formato)
            self.view.label.setText(resultado)
        except Exception as e:
            self.view.label.setText(f"Error al exportar inventario: {e}")

    @permiso_auditoria_inventario('editar')
    def generar_qr_para_item(self):
        try:
            id_item = self.view.id_item_input.text()
            if not id_item:
                self.view.label.setText("Por favor, ingrese un ID de ítem válido.")
                return
            qr_code = self.model.generar_qr(id_item)
            if qr_code:
                self.view.label.setText(f"Código QR generado: {qr_code}")
            else:
                self.view.label.setText("Error al generar el código QR.")
        except Exception as e:
            self.view.label.setText(f"Error al generar QR: {e}")

    @permiso_auditoria_inventario('editar')
    def asociar_qr_a_perfil(self):
        id_item = self.view.obtener_id_item_seleccionado()
        if not id_item:
            QMessageBox.warning(self.view, "QR", "Seleccione un perfil para asociar QR.")
            return
        item = self.model.obtener_item_por_id(id_item)
        if not item or "codigo" not in item:
            QMessageBox.warning(self.view, "QR", "No se encontró el código para este perfil.")
            return
        codigo = item["codigo"]
        qr_code = f"QR-{codigo}"
        self.model.actualizar_qr_code(id_item, qr_code)
        QMessageBox.information(self.view, "QR asociado", f"QR '{qr_code}' asociado al perfil con código '{codigo}'.")
        self.actualizar_inventario()

    def ver_qr_item_seleccionado(self):
        id_item = self.view.obtener_id_item_seleccionado()
        if not id_item:
            QMessageBox.warning(self.view, "QR", "Seleccione un perfil para ver su QR.")
            return
        item = self.model.obtener_item_por_id(id_item)
        if item and ("qr" in item or "qr_code" in item):
            qr_valor = item.get("qr") or item.get("qr_code")
            QMessageBox.information(self.view, "QR del perfil", f"QR asociado: {qr_valor}")
        else:
            QMessageBox.warning(self.view, "QR", "No se encontró el QR para este perfil.")

    def resaltar_items_bajo_stock(self, datos):
        try:
            for row, item in enumerate(datos):
                stock_actual = item[5]  # Suponiendo que la columna 5 es el stock actual
                stock_minimo = item[6]  # Suponiendo que la columna 6 es el stock mínimo
                if stock_actual < stock_minimo:
                    for col in range(self.view.tabla_inventario.columnCount()):
                        self.view.tabla_inventario.item(row, col).setBackground(QtGui.QColor("red"))
        except Exception as e:
            print(f"Error al resaltar ítems bajo stock: {e}")
            self.view.label_estado.setText("Error al resaltar ítems con bajo stock.")

    def mostrar_mensaje_confirmacion(self):
        QMessageBox.information(self.view, "Inventario actualizado", "La tabla de inventario se ha actualizado correctamente.")

    def abrir_reserva_lote_perfiles(self):
        self.view.abrir_reserva_lote_perfiles()

    def mostrar_feedback_entrega(self, exito, mensaje):
        if exito:
            self.view.label.setText(f"Entrega realizada correctamente: {mensaje}")
        else:
            self.view.label.setText(f"Error en la entrega: {mensaje}")

    @permiso_auditoria_inventario('editar')
    def transformar_reserva_en_entrega(self, id_reserva):
        try:
            resultado = self.model.transformar_reserva_en_entrega(id_reserva)
            if resultado is True:
                self.view.mostrar_mensaje("Entrega realizada correctamente.")
            elif resultado is False:
                self.view.mostrar_mensaje("Stock insuficiente para entregar la cantidad solicitada.")
            else:
                self.view.mostrar_mensaje("No se pudo entregar la reserva (verifique el estado o los datos).")
        except Exception as e:
            self.view.mostrar_mensaje(f"Error al entregar reserva: {e}")
