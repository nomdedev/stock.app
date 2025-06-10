import json
from PyQt6.QtWidgets import QTableWidgetItem, QDialog, QVBoxLayout, QTableWidget, QFormLayout, QLineEdit, QHBoxLayout, QPushButton, QMessageBox, QLabel
from PyQt6 import QtGui
from modules.usuarios.model import UsuariosModel
from modules.auditoria.model import AuditoriaModel
from modules.inventario.view import InventarioView
from modules.obras.model import ObrasModel
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
                usuario_id = usuario['id'] if usuario and 'id' in usuario else None
                if not usuario or not usuario_model:
                    if hasattr(controller, 'view') and hasattr(controller.view, 'mostrar_mensaje'):
                        controller.view.mostrar_mensaje(f"No tiene permiso para realizar la acción: {accion}", tipo='error')
                    elif hasattr(controller, 'view') and hasattr(controller.view, 'label'):
                        controller.view.label.setText(f"No tiene permiso para realizar la acción: {accion}")
                    if auditoria_model:
                        detalle = f"{accion} - denegado"
                        auditoria_model.registrar_evento(usuario_id, self.modulo, accion, detalle, ip)
                    return None
                if usuario['rol'] not in ('admin', 'supervisor'):
                    modulos_permitidos = usuario_model.obtener_modulos_permitidos(usuario)
                    if self.modulo not in modulos_permitidos:
                        if hasattr(controller, 'view') and hasattr(controller.view, 'mostrar_mensaje'):
                            controller.view.mostrar_mensaje(f"No tiene permiso para acceder al módulo: {self.modulo}", tipo='error')
                        elif hasattr(controller, 'view') and hasattr(controller.view, 'label'):
                            controller.view.label.setText(f"No tiene permiso para acceder al módulo: {self.modulo}")
                        if auditoria_model:
                            detalle = f"{accion} - denegado (módulo)"
                            auditoria_model.registrar_evento(usuario_id, self.modulo, accion, detalle, ip)
                        return None
                try:
                    # print(f"[LOG ACCIÓN] Ejecutando acción '{accion}' en módulo '{self.modulo}' por usuario: {usuario.get('username', 'desconocido')} (id={usuario.get('id', '-')})")
                    resultado = func(controller, *args, **kwargs)
                    # print(f"[LOG ACCIÓN] Acción '{accion}' en módulo '{self.modulo}' finalizada con éxito.")
                    if auditoria_model:
                        detalle = f"{accion} - éxito"
                        auditoria_model.registrar_evento(usuario_id, self.modulo, accion, detalle, ip)
                    return resultado
                except Exception as e:
                    # print(f"[LOG ACCIÓN] Error en acción '{accion}' en módulo '{self.modulo}': {e}")
                    if auditoria_model:
                        detalle = f"{accion} - error: {e}"
                        auditoria_model.registrar_evento(usuario_id, self.modulo, accion, detalle, ip)
                    log_error(f"Error en {accion}: {e}")
                    raise
            return wrapper
        return decorador

permiso_auditoria_inventario = PermisoAuditoria('inventario')

class InventarioController:
    """
    Controlador para el módulo de Inventario.
    
    Todas las acciones públicas relevantes están decoradas con @permiso_auditoria_inventario,
    lo que garantiza el registro automático en el módulo de auditoría.
    
    Patrón de auditoría:
    - Decorador @permiso_auditoria_inventario('accion') en cada método público relevante.
    - El decorador valida permisos, registra el evento en auditoría (usuario, módulo, acción, detalle, ip, estado).
    - Feedback visual inmediato ante denegación o error.
    - Para casos personalizados, se puede usar self._registrar_evento_auditoria().
    
    Ejemplo de uso:
        @permiso_auditoria_inventario('editar')
        def agregar_item(self):
            ...
    """
    def __init__(self, model, view, db_connection, usuario_actual=None):
        self.model = model
        self.view = view
        self.usuario_actual = usuario_actual  # dict con id, nombre, rol, ip, etc.
        self.usuarios_model = UsuariosModel(db_connection)
        self.auditoria_model = AuditoriaModel(db_connection)
        self.db_connection = db_connection
        from modules.obras.model import ObrasModel
        self.obras_model = ObrasModel(db_connection)

        # Integración en tiempo real con ObrasView
        # Se debe conectar la señal 'obra_agregada' de ObrasView a este controlador:
        # Ejemplo (en main.py o donde se inicializan los controladores):
        # obras_view.obra_agregada.connect(self.actualizar_por_obra)
        #
        # Implementar el método 'actualizar_por_obra' para refrescar datos según la obra agregada

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
        self.view.ajustes_stock_guardados.connect(self.procesar_ajustes_stock)

        self.actualizar_inventario()
        self.cargar_productos()

    def _registrar_evento_auditoria(self, tipo_evento, detalle, exito=True):
        usuario_id = self.usuario_actual['id'] if self.usuario_actual and 'id' in self.usuario_actual else -1
        ip = self.usuario_actual.get('ip', '') if self.usuario_actual else ''
        estado = "éxito" if exito else "error"
        detalle_final = f"{detalle} - {estado}"
        if usuario_id == -1:
            detalle_final = f"{detalle_final} [usuario no autenticado]"
            log_error(f"[AUDITORÍA] Evento sin usuario autenticado: modulo='inventario', tipo_evento='{tipo_evento}', detalle='{detalle_final}'")
            if hasattr(self.view, 'mostrar_mensaje'):
                self.view.mostrar_mensaje("Advertencia: acción registrada sin usuario autenticado.", tipo='advertencia')
        try:
            self.auditoria_model.registrar_evento(usuario_id, "inventario", tipo_evento, detalle_final, ip)
        except Exception as e:
            log_error(f"Error al registrar evento de auditoría: {e}")

    def _feedback(self, mensaje, tipo='info'):
        if hasattr(self.view, 'mostrar_mensaje'):
            self.view.mostrar_mensaje(mensaje, tipo=tipo)
        elif hasattr(self.view, 'label'):
            self.view.label.setText(mensaje)

    @permiso_auditoria_inventario('ver')
    def actualizar_inventario(self):
        try:
            datos = self.model.obtener_items()
            self.view.tabla_inventario.setRowCount(len(datos))
            self.view.tabla_inventario.setColumnCount(18)
            if not datos:
                self.view.label_titulo.setText("No hay datos de inventario para mostrar.")
            else:
                self.view.label_titulo.setText("INVENTORY")
            for row, item in enumerate(datos):
                for col, value in enumerate(item):
                    self.view.tabla_inventario.setItem(row, col, QTableWidgetItem(str(value)))
        except Exception as e:
            log_error(f"Error al actualizar inventario: {e}")
            self._feedback(f"Error al actualizar inventario: {e}", tipo='error')
            self._registrar_evento_auditoria('error', f"Error al actualizar inventario: {e}", exito=False)

    def cargar_productos(self):
        try:
            productos = self.model.obtener_productos()
            self.view.cargar_items(productos)
        except Exception as e:
            log_error(f"Error al cargar productos: {e}")
            self._feedback(f"Error al cargar productos: {e}", tipo='error')
            self._registrar_evento_auditoria('error', f"Error al cargar productos: {e}", exito=False)

    def cargar_datos_inventario(self, offset=0, limite=500):
        try:
            items = self.model.obtener_items_por_lotes(offset, limite)
            self.view.cargar_items(items)
        except Exception as e:
            log_error(f"Error al cargar datos de inventario: {e}")
            self._feedback(f"Error al cargar datos de inventario: {e}", tipo='error')
            self._registrar_evento_auditoria('error', f"Error al cargar datos de inventario: {e}", exito=False)

    def _solicitud_aprobacion_o_ejecucion(self, tipo_accion, datos_accion, funcion_ejecucion, *args, **kwargs):
        usuario = self.usuario_actual
        if usuario and usuario.get('rol') == 'usuario':
            try:
                self.model.db.ejecutar_query(
                    """
                    INSERT INTO solicitudes_aprobacion (id_usuario, modulo, tipo_accion, datos_json)
                    VALUES (?, ?, ?, ?)
                    """,
                    (usuario['id'], 'inventario', tipo_accion, json.dumps(datos_accion))
                )
                self._feedback("La acción requiere aprobación de un supervisor. Solicitud registrada y pendiente de aprobación.", tipo='info')
                self._registrar_evento_auditoria(f'solicitud_aprobacion_{tipo_accion}', str(datos_accion))
            except Exception as e:
                log_error(f"Error al registrar la solicitud de aprobación: {e}")
                self._feedback(f"Error al registrar la solicitud de aprobación: {e}", tipo='error')
                self._registrar_evento_auditoria('error', f"Error al registrar solicitud aprobación: {e}", exito=False)
            return
        return funcion_ejecucion(*args, **kwargs)

    @permiso_auditoria_inventario('editar')
    def agregar_item(self):
        def ejecutar():
            try:
                print(f"[DEBUG] Tipo de self.view: {type(self.view)}")
                datos = self.view.abrir_formulario_nuevo_item()
                campos_obligatorios = ["codigo", "nombre", "tipo_material", "unidad", "stock_actual", "stock_minimo", "ubicacion", "descripcion"]
                if not datos or not all(datos.get(campo) for campo in campos_obligatorios):
                    self._feedback("Todos los campos son obligatorios para agregar un ítem.", tipo='warning')
                    return
                codigo = datos.get("codigo")
                if not isinstance(codigo, str) or not codigo.strip():
                    self._feedback("El código del ítem es obligatorio y debe ser texto.", tipo='warning')
                    return
                if self.model.obtener_item_por_codigo(codigo):
                    self._feedback("Ya existe un ítem con ese código.", tipo='warning')
                    return
                try:
                    self.model.agregar_item(tuple(datos.get(campo, None) for campo in ["codigo", "nombre", "tipo_material", "unidad", "stock_actual", "stock_minimo", "ubicacion", "descripcion", "qr", "imagen_referencia"]))
                except Exception as e:
                    log_error(f"Error al agregar ítem en la base de datos: {e}")
                    self._feedback(f"Error al agregar ítem en la base de datos: {e}", tipo='error')
                    self._registrar_evento_auditoria('error', f"Error al agregar ítem: {e}", exito=False)
                    return
                try:
                    item_row = self.model.obtener_item_por_codigo(codigo)
                    nombre_usuario = self.usuario_actual.get("nombre", "") if self.usuario_actual else ''
                    if item_row:
                        self.model.registrar_movimiento((item_row[0][0], "alta", datos["stock_actual"], nombre_usuario, "Alta inicial de ítem", None))
                except Exception as e:
                    log_error(f"Error al registrar movimiento de alta: {e}")
                    self._registrar_evento_auditoria('error', f"Error al registrar movimiento de alta: {e}", exito=False)
                self._registrar_evento_auditoria('alta', f"Ítem agregado: {codigo}")
                self.actualizar_inventario()
                self._feedback(f"Ítem '{codigo}' agregado correctamente.", tipo='success')
            except Exception as e:
                log_error(f"Error general al agregar ítem: {e}")
                self._feedback(f"Error al agregar ítem: {e}", tipo='error')
                self._registrar_evento_auditoria('error', f"Error general al agregar ítem: {e}", exito=False)
        print(f"[DEBUG] Tipo de self.view (fuera de ejecutar): {type(self.view)}")
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
                        self._feedback("Complete todos los campos para reservar.", tipo='warning')
                        self._registrar_evento_auditoria('reserva_material', "Campos incompletos para reserva", exito=False)
                        return
                    try:
                        cantidad_int = int(cantidad)
                        if cantidad_int <= 0:
                            self._feedback("La cantidad debe ser mayor a cero.", tipo='warning')
                            self._registrar_evento_auditoria('reserva_material', "Cantidad no válida", exito=False)
                            return
                    except Exception:
                        self._feedback("Ingrese un número válido para la cantidad.", tipo='warning')
                        self._registrar_evento_auditoria('reserva_material', "Cantidad no numérica", exito=False)
                        return
                    item_row = self.model.obtener_item_por_codigo(id_item) if not id_item.isdigit() else self.model.db.ejecutar_query("SELECT * FROM inventario_perfiles WHERE id = ?", (id_item,))
                    if not item_row:
                        self._feedback("No se encontró el material especificado.", tipo='warning')
                        self._registrar_evento_auditoria('reserva_material', f"Material no encontrado: {id_item}", exito=False)
                        return
                    stock_actual = item_row[0][5] if len(item_row[0]) > 5 else None
                    if stock_actual is None or int(stock_actual) < cantidad_int:
                        self._feedback("Stock insuficiente para reservar la cantidad solicitada.", tipo='warning')
                        self._registrar_evento_auditoria('reserva_material', f"Stock insuficiente para {id_item}", exito=False)
                        return
                    reservas_existentes = self.model.db.ejecutar_query(
                        "SELECT COUNT(*) FROM reservas_materiales WHERE (codigo_reserva = ? OR (referencia_obra = ? AND id_item = ?)) AND estado = 'activa'",
                        (codigo_reserva, obra, id_item)
                    )
                    if reservas_existentes and reservas_existentes[0][0] > 0:
                        self._feedback("Ya existe una reserva activa para este material y obra, o el código ya está en uso.", tipo='warning')
                        self._registrar_evento_auditoria('reserva_material', f"Reserva duplicada para {id_item} obra {obra}", exito=False)
                        return
                    # Validación cruzada: impedir reservas a obras inexistentes
                    id_obra = obra if obra.isdigit() else None
                    if id_obra is not None:
                        if not self.obras_model.existe_obra_por_id(int(id_obra)):
                            self._feedback("No existe una obra con el ID especificado. No se puede reservar material.", tipo='error')
                            self._registrar_evento_auditoria('reserva_material', f"Intento de reserva a obra inexistente: {obra}", exito=False)
                            return
                    # Si se usa nombre, se podría agregar validación adicional aquí
                    try:
                        self.model.db.ejecutar_query(
                            """
                            INSERT INTO reservas_materiales (referencia_obra, id_item, cantidad, codigo_reserva, estado)
                            VALUES (?, ?, ?, ?, 'activa')
                            """,
                            (obra, id_item, cantidad_int, codigo_reserva)
                        )
                        self._registrar_evento_auditoria('reserva_material', f"Reserva creada: {codigo_reserva} para obra {obra} y material {id_item}")
                        self._feedback(f"Reserva creada correctamente para obra {obra} y material {id_item}.", tipo='success')
                        self.actualizar_inventario()
                        dialog.accept()
                    except Exception as e:
                        log_error(f"Error al crear reserva: {e}")
                        self._feedback(f"Error al crear la reserva: {e}", tipo='error')
                        self._registrar_evento_auditoria('error', f"Error al crear reserva: {e}", exito=False)
                reservar_button.clicked.connect(on_reservar)
                cancelar_button.clicked.connect(dialog.reject)
                dialog.setLayout(layout)
                dialog.exec()
            except Exception as e:
                log_error(f"Error al abrir la ventana de reserva: {e}")
                self._feedback(f"Error al abrir la ventana de reserva: {e}", tipo='error')
                self._registrar_evento_auditoria('error', f"Error al abrir ventana reserva: {e}", exito=False)
        return self._solicitud_aprobacion_o_ejecucion('reservar', {}, ejecutar)

    @permiso_auditoria_inventario('editar')
    def ajustar_stock(self):
        def ejecutar():
            try:
                dialog = QDialog(self.view)
                dialog.setWindowTitle("Ajustar stock de material")
                layout = QVBoxLayout()
                form_layout = QFormLayout()
                id_item_input = QLineEdit()
                cantidad_input = QLineEdit()
                motivo_input = QLineEdit()
                stock_actual_label = QLabel("")
                form_layout.addRow("ID o código de material:", id_item_input)
                form_layout.addRow("Stock actual:", stock_actual_label)
                form_layout.addRow("Nuevo stock (valor absoluto):", cantidad_input)
                form_layout.addRow("Motivo del ajuste:", motivo_input)
                layout.addLayout(form_layout)
                botones_layout = QHBoxLayout()
                ajustar_button = QPushButton("Ajustar")
                cancelar_button = QPushButton("Cancelar")
                botones_layout.addWidget(ajustar_button)
                botones_layout.addWidget(cancelar_button)
                layout.addLayout(botones_layout)
                dialog.setLayout(layout)

                def actualizar_stock_label():
                    id_item = id_item_input.text().strip()
                    if not id_item:
                        stock_actual_label.setText("")
                        return
                    item_row = self.model.obtener_item_por_codigo(id_item) if not id_item.isdigit() else self.model.db.ejecutar_query("SELECT id, codigo, nombre, tipo_material, unidad, stock_actual, stock_minimo, ubicacion, descripcion, qr, imagen_referencia FROM inventario_perfiles WHERE id = ?", (id_item,))
                    if item_row and len(item_row) > 0:
                        stock_actual = item_row[0][5]
                        stock_actual_label.setText(str(stock_actual))
                    else:
                        stock_actual_label.setText("No encontrado")

                id_item_input.editingFinished.connect(actualizar_stock_label)

                def on_ajustar():
                    id_item = id_item_input.text().strip()
                    cantidad = cantidad_input.text().strip()
                    motivo = motivo_input.text().strip()
                    if not (id_item and cantidad and motivo):
                        self._feedback("Complete todos los campos para ajustar stock.", tipo='warning')
                        self._registrar_evento_auditoria('ajuste_stock', "Campos incompletos para ajuste", exito=False)
                        return
                    try:
                        nueva_cantidad = int(cantidad)
                    except Exception:
                        self._feedback("Ingrese un número válido para el nuevo stock.", tipo='warning')
                        self._registrar_evento_auditoria('ajuste_stock', "Cantidad no numérica", exito=False)
                        return
                    item_row = self.model.obtener_item_por_codigo(id_item) if not id_item.isdigit() else self.model.db.ejecutar_query("SELECT id, codigo, nombre, tipo_material, unidad, stock_actual, stock_minimo, ubicacion, descripcion, qr, imagen_referencia FROM inventario_perfiles WHERE id = ?", (id_item,))
                    if not item_row:
                        self._feedback("No se encontró el material especificado.", tipo='warning')
                        self._registrar_evento_auditoria('ajuste_stock', f"Material no encontrado: {id_item}", exito=False)
                        return
                    id_perfil = item_row[0][0]
                    try:
                        self.model.ajustar_stock_perfil(id_perfil, nueva_cantidad, self.usuario_actual, self.view)
                        self._registrar_evento_auditoria('ajuste_stock', f"Ajuste de stock: {id_perfil} nuevo valor {nueva_cantidad} motivo {motivo}")
                        self._feedback(f"Stock ajustado correctamente para material {id_perfil}.", tipo='success')
                        self.actualizar_inventario()
                        dialog.accept()
                    except Exception as e:
                        log_error(f"Error al ajustar stock: {e}")
                        self._feedback(f"Error al ajustar stock: {e}", tipo='error')
                        self._registrar_evento_auditoria('error', f"Error al ajustar stock: {e}", exito=False)
                ajustar_button.clicked.connect(on_ajustar)
                cancelar_button.clicked.connect(dialog.reject)
                dialog.exec()
            except Exception as e:
                log_error(f"Error al abrir la ventana de ajuste de stock: {e}")
                self._feedback(f"Error al abrir la ventana de ajuste de stock: {e}", tipo='error')
                self._registrar_evento_auditoria('error', f"Error al abrir ventana ajuste stock: {e}", exito=False)
        return self._solicitud_aprobacion_o_ejecucion('ajustar_stock', {}, ejecutar)

    @permiso_auditoria_inventario('editar')
    def procesar_ajustes_stock(self, ajustes):
        """
        Recibe una lista de dicts: {id, cantidad, motivo} y procesa los ajustes de stock en lote.
        Valida, actualiza la base y registra en auditoría.
        """
        exitos = 0
        errores = []
        for ajuste in ajustes:
            id_item = ajuste.get('id')
            cantidad = ajuste.get('cantidad')
            motivo = ajuste.get('motivo')
            if not id_item or cantidad is None or not motivo:
                errores.append(f"Faltan datos en ajuste: {ajuste}")
                continue
            try:
                self.model.actualizar_stock(id_item, cantidad)
                self.model.registrar_movimiento(id_item, cantidad, 'ajuste', motivo)
                self._registrar_evento_auditoria('ajuste_stock', f"Ajuste de stock: {id_item} cantidad {cantidad} motivo {motivo}")
                exitos += 1
            except Exception as e:
                errores.append(f"Error en id {id_item}: {e}")
        if exitos:
            self._feedback(f"{exitos} ajustes de stock guardados correctamente.", tipo='success')
            self.actualizar_inventario()
        if errores:
            self._feedback("\n".join(errores), tipo='error')

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
            self.view.mostrar_feedback(resultado, tipo="exito" if "exportado" in resultado.lower() else "info")
        except Exception as e:
            self.view.mostrar_feedback(f"Error al exportar inventario: {e}", tipo="error")

    @permiso_auditoria_inventario('editar')
    def generar_qr_para_item(self):
        try:
            id_item = self.view.id_item_input.text()
            if not id_item:
                self.view.mostrar_feedback("Por favor, ingrese un ID de ítem válido.", tipo="advertencia")
                return
            qr_code = self.model.generar_qr(id_item)
            if qr_code:
                self.view.mostrar_feedback(f"Código QR generado: {qr_code}", tipo="exito")
            else:
                self.view.mostrar_feedback("Error al generar el código QR.", tipo="error")
        except Exception as e:
            self.view.mostrar_feedback(f"Error al generar QR: {e}", tipo="error")

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
        self.model.actualizacion_qr_code(id_item, qr_code)
        QMessageBox.information(self.view, "QR asociado", f"QR '{qr_code}' asociado al perfil con código '{codigo}'.")
        self.actualizar_inventario()

    @permiso_auditoria_inventario('ver')
    def ver_qr_item_seleccionado(self):
        id_item = self.view.obtener_id_item_seleccionado()
        usuario = getattr(self, 'usuario_actual', None)
        usuario_id = usuario['id'] if usuario and 'id' in usuario else None
        ip = usuario.get('ip', '') if usuario else ''
        if not id_item:
            QMessageBox.warning(self.view, "QR", "Seleccione un perfil para ver su QR.")
            self._registrar_evento_auditoria('ver_qr_item_seleccionado', "denegado (sin selección)", exito=False)
            return
        item = self.model.obtener_item_por_id(id_item)
        if item and ("qr" in item or "qr_code" in item):
            qr_valor = item.get("qr") or item.get("qr_code")
            QMessageBox.information(self.view, "QR del perfil", f"QR asociado: {qr_valor}")
            self._registrar_evento_auditoria('ver_qr_item_seleccionado', "éxito", exito=True)
        else:
            QMessageBox.warning(self.view, "QR", "No se encontró el QR para este perfil.")
            self._registrar_evento_auditoria('ver_qr_item_seleccionado', "error (no encontrado)", exito=False)

    @permiso_auditoria_inventario('ver')
    def resaltar_items_bajo_stock(self, datos):
        usuario = getattr(self, 'usuario_actual', None)
        usuario_id = usuario['id'] if usuario and 'id' in usuario else None
        ip = usuario.get('ip', '') if usuario else ''
        try:
            for row, item in enumerate(datos):
                stock_actual = item[5]  # Suponiendo que la columna 5 es el stock actual
                stock_minimo = item[6]  # Suponiendo que la columna 6 es el stock mínimo
                if stock_actual < stock_minimo:
                    for col in range(self.view.tabla_inventario.columnCount()):
                        self.view.tabla_inventario.item(row, col).setBackground(QtGui.QColor("red"))
            self._registrar_evento_auditoria('resaltar_items_bajo_stock', '', exito=True)
        except Exception as e:
            # print(f"Error al resaltar ítems bajo stock: {e}")
            self.view.label_estado.setText("Error al resaltar ítems con bajo stock.")
            self._registrar_evento_auditoria('resaltar_items_bajo_stock', f"error: {e}", exito=False)

    @permiso_auditoria_inventario('ver')
    def mostrar_mensaje_confirmacion(self):
        self._feedback("La tabla de inventario se ha actualizado correctamente.", tipo='success')
        self._registrar_evento_auditoria('mostrar_mensaje_confirmacion', '', exito=True)

    @permiso_auditoria_inventario('ver')
    def abrir_reserva_lote_perfiles(self):
        self.view.abrir_reserva_lote_perfiles()
        self._registrar_evento_auditoria('abrir_reserva_lote_perfiles', '', exito=True)

    @permiso_auditoria_inventario('ver')
    def mostrar_feedback_entrega(self, exito, mensaje):
        if exito:
            self.view.label.setText(f"Entrega realizada correctamente: {mensaje}")
        else:
            self.view.label.setText(f"Error en la entrega: {mensaje}")
        self._registrar_evento_auditoria('mostrar_feedback_entrega', mensaje, exito=exito)

    @permiso_auditoria_inventario('editar')
    def transformar_reserva_en_entrega(self, id_reserva):
        try:
            resultado = self.model.transformar_reserva_en_entrega(id_reserva)
            if resultado is True:
                self._feedback("Entrega realizada correctamente.", tipo='success')
            elif resultado is False:
                self._feedback("Stock insuficiente para entregar la cantidad solicitada.", tipo='warning')
            else:
                self._feedback("No se pudo entregar la reserva (verifique el estado o los datos).", tipo='error')
        except Exception as e:
            self._feedback(f"Error al entregar reserva: {e}", tipo='error')

    def actualizar_por_obra(self, datos_obra):
        """
        Método para refrescar la vista de inventario cuando se agrega una nueva obra.
        Se puede usar para actualizar la lista de materiales, pedidos pendientes, etc.
        """
        self.actualizar_inventario()
        self._feedback(f"Inventario actualizado por nueva obra: {datos_obra.get('nombre','')} (ID: {datos_obra.get('id','')})", tipo='info')
        if hasattr(self.view, 'mostrar_mensaje'):
            self.view.mostrar_mensaje(f"Inventario actualizado automáticamente por la obra '{datos_obra.get('nombre','')}'.", tipo='info')

    def actualizar_por_pedido(self, datos_pedido):
        """
        Método para refrescar la vista de inventario cuando se actualiza un pedido.
        Se puede usar para actualizar la lista de materiales, stock, etc.
        """
        self.actualizar_inventario()
        self._feedback(f"Inventario actualizado por pedido: {datos_pedido.get('id','')} (Obra: {datos_pedido.get('obra','')})", tipo='info')
        if hasattr(self.view, 'mostrar_mensaje'):
            self.view.mostrar_mensaje(f"Inventario actualizado automáticamente por el pedido '{datos_pedido.get('id','')}'.", tipo='info')

    def actualizar_por_pedido_cancelado(self, datos_pedido):
        """
        Refresca la vista y muestra feedback visual cuando se cancela un pedido.
        """
        self.actualizar_inventario()
        self._feedback(f"Pedido cancelado: {datos_pedido.get('id','')} - Se actualizó el inventario.", tipo='advertencia')
        if hasattr(self.view, 'mostrar_mensaje'):
            self.view.mostrar_mensaje(f"Inventario actualizado por cancelación del pedido '{datos_pedido.get('id','')}'.", tipo='advertencia')

    @permiso_auditoria_inventario('editar')
    def reservar_perfil(self, usuario, id_obra, id_perfil, cantidad):
        """
        Lógica robusta para reservar perfil desde el modal. Llama a model.reservar_perfil y maneja feedback/auditoría.
        """
        try:
            resultado = self.model.reservar_perfil(id_obra, id_perfil, cantidad, usuario=usuario, view=self.view)
            self._registrar_evento_auditoria('reserva_perfil', f"Reserva de {cantidad} del perfil {id_perfil} para obra {id_obra}")
            self._feedback("Reserva realizada correctamente.", tipo='success')
            self.actualizar_inventario()
            return resultado
        except ValueError as e:
            self._feedback(str(e), tipo='warning')
            self._registrar_evento_auditoria('reserva_perfil', f"Error: {e}", exito=False)
            raise
        except Exception as e:
            self._feedback(f"Error inesperado: {e}", tipo='error')
            self._registrar_evento_auditoria('reserva_perfil', f"Error inesperado: {e}", exito=False)
            raise

    def validar_obra_existente(self, id_obra, obras_model):
        """
        Valida que la obra exista en el sistema antes de permitir registrar un pedido de material.
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

    def guardar_pedido_material(self, datos, obras_model=None):
        """
        Guarda el pedido de material solo si la obra existe (validación cruzada).
        Si obras_model es None, no valida (para compatibilidad).
        """
        id_obra = datos.get('id_obra') if isinstance(datos, dict) else None
        if obras_model is not None and not self.validar_obra_existente(id_obra, obras_model):
            if hasattr(self.view, 'mostrar_mensaje'):
                self.view.mostrar_mensaje(f"No se puede registrar el pedido: la obra {id_obra} no existe.", tipo='error')
            return
        self.model.guardar_pedido_material(datos)
        self.auditoria_model.registrar_evento(
            usuario_id=self.usuario_actual,
            modulo="Inventario",
            tipo_evento="Guardar pedido material",
            detalle=f"Guardó pedido de material: {datos}",
            ip_origen="127.0.0.1"
        )
        # Refrescar la tabla de obras y pedidos si existe el método en la vista
        if hasattr(self.view, 'mostrar_resumen_obras'):
            self.view.mostrar_resumen_obras(self.model.obtener_obras_con_estado_pedido())
        elif hasattr(self.view, 'mostrar_pedidos_usuario'):
            self.view.mostrar_pedidos_usuario(self.model.obtener_pedidos_por_usuario(self.usuario_actual))
