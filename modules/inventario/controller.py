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
                    auditoria_model.registrar_evento(usuario, self.modulo, accion)
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

    @permiso_auditoria_inventario('editar')
    def agregar_item(self):
        try:
            datos = self.view.abrir_formulario_nuevo_item()
            if not datos or not all(datos.values()):
                QMessageBox.warning(self.view, "Error", "Todos los campos son obligatorios para agregar un ítem.")
                return
            codigo = datos.get("codigo")
            if not codigo:
                QMessageBox.warning(self.view, "Error", "El código del ítem es obligatorio.")
                return
            if self.model.obtener_item_por_codigo(codigo):
                QMessageBox.warning(self.view, "Error", "Ya existe un ítem con el mismo código.")
                return
            self.model.agregar_item(datos)
            self.actualizar_inventario()
            self.mostrar_mensaje_confirmacion()
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Error al agregar ítem: {e}")

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

    @permiso_auditoria_inventario('editar')
    def reservar_item(self):
        try:
            dialog = QDialog(self.view)
            dialog.setWindowTitle("Reservar Ítem")

            layout = QVBoxLayout()

            form_layout = QFormLayout()
            obra_input = QLineEdit()
            cantidad_input = QLineEdit()

            form_layout.addRow("Obra:", obra_input)
            form_layout.addRow("Cantidad:", cantidad_input)

            layout.addLayout(form_layout)

            botones_layout = QHBoxLayout()
            reservar_button = QPushButton("Reservar")
            cancelar_button = QPushButton("Cancelar")
            botones_layout.addWidget(reservar_button)
            botones_layout.addWidget(cancelar_button)

            layout.addLayout(botones_layout)
            dialog.setLayout(layout)

            reservar_button.clicked.connect(lambda: self.procesar_reserva(dialog, obra_input.text(), cantidad_input.text()))
            cancelar_button.clicked.connect(dialog.reject)

            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Error al abrir la ventana de reserva: {e}")

    @permiso_auditoria_inventario('editar')
    def ajustar_stock(self):
        try:
            dialog = self.view.abrir_ajustar_stock_dialog()
            if dialog.exec() == QDialog.DialogCode.Accepted:
                datos_ajuste = dialog.obtener_datos_ajuste_stock()
                for ajuste in datos_ajuste:
                    codigo = ajuste["codigo"]
                    cantidad = ajuste["cantidad"]

                    if not codigo or cantidad is None:
                        QMessageBox.warning(self.view, "Error", "Datos incompletos en el ajuste de stock.")
                        continue

                    self.model.ajustar_stock(codigo, cantidad)

                self.actualizar_inventario()
                self.mostrar_mensaje_confirmacion()
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Error al ajustar el stock: {e}")

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
