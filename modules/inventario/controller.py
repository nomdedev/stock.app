from PyQt6.QtWidgets import QTableWidgetItem, QDialog, QVBoxLayout, QTableWidget, QFormLayout, QLineEdit, QHBoxLayout, QPushButton, QMessageBox
from PyQt6 import QtGui

class InventarioController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        if self.view and hasattr(self.view, 'boton_actualizar'):
            self.view.boton_actualizar.clicked.connect(self.actualizar_inventario)
        if self.view and hasattr(self.view, 'boton_nuevo_item'):
            self.view.boton_nuevo_item.clicked.connect(self.agregar_item)
        if self.view and hasattr(self.view, 'boton_ver_movimientos'):
            self.view.boton_ver_movimientos.clicked.connect(self.ver_movimientos)
        if self.view and hasattr(self.view, 'boton_reservar'):
            self.view.boton_reservar.clicked.connect(self.reservar_item)
        if self.view and hasattr(self.view, 'boton_ajustar_stock'):
            self.view.boton_ajustar_stock.clicked.connect(self.ajustar_stock)
        if self.view and hasattr(self.view, 'boton_exportar_excel'):
            self.view.boton_exportar_excel.clicked.connect(lambda: self.exportar_inventario("excel"))
        if self.view and hasattr(self.view, 'boton_exportar_pdf'):
            self.view.boton_exportar_pdf.clicked.connect(lambda: self.exportar_inventario("pdf"))
        if self.view and hasattr(self.view, 'boton_buscar'):
            self.view.boton_buscar.clicked.connect(self.buscar_item)
        if self.view and hasattr(self.view, 'boton_generar_qr'):
            self.view.boton_generar_qr.clicked.connect(self.generar_qr_para_item)

        self.actualizar_inventario()

    def actualizar_inventario(self, offset=0, limite=500):
        try:
            datos = self.model.obtener_items_por_lotes(offset, limite)
            self.view.tabla_inventario.setRowCount(len(datos))
            for row, item in enumerate(datos):
                for col, value in enumerate(item):
                    self.view.tabla_inventario.setItem(row, col, QTableWidgetItem(str(value)))
            # Resaltar ítems bajo stock sin volver a llamar al modelo
            self.resaltar_items_bajo_stock(datos)
        except Exception as e:
            print(f"Error al actualizar inventario: {e}")
            self.view.label_estado.setText("Error al cargar el inventario.")

    def cargar_datos_inventario(self):
        try:
            self.actualizar_inventario()
            self.view.label.setText("Inventario actualizado correctamente.")
        except Exception as e:
            print(f"Error al actualizar el inventario: {e}")
            self.view.label.setText("Error al actualizar el inventario.")

    def agregar_item(self):
        try:
            datos = self.view.obtener_datos_nuevo_item()
            if not datos:
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

            # Registro en auditoría
            self.model.registrar_auditoria("Carga", codigo, datos.get("cantidad", 0), self.usuario_actual)
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Error al agregar el ítem: {e}")

    def mostrar_mensaje_confirmacion(self):
        """Muestra un mensaje de confirmación al usuario indicando que el inventario se ha actualizado."""
        QMessageBox.information(self.view, "Inventario actualizado", "La tabla de inventario se ha actualizado correctamente.")

    def abrir_formulario_nuevo(self):
        datos = self.view.abrir_formulario_nuevo_item()
        if datos:
            try:
                self.model.agregar_item(datos)
                self.view.label.setText("Ítem agregado exitosamente.")
                self.actualizar_inventario()
                self.mostrar_mensaje_confirmacion()
            except Exception as e:
                print(f"Error al agregar ítem: {e}")
                self.view.label.setText("Error al agregar el ítem.")

    def ver_movimientos(self):
        id_item = self.view.obtener_id_item_seleccionado()
        if id_item:
            movimientos = self.model.obtener_movimientos(id_item)
            self.view.mostrar_movimientos(movimientos)
        else:
            self.view.label.setText("Seleccione un ítem para ver sus movimientos.")

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

    def procesar_reserva(self, dialog, obra, cantidad):
        try:
            id_item = self.view.obtener_id_item_seleccionado()
            if not id_item:
                self.view.label.setText("Seleccione un ítem para reservar.")
                return

            if not obra or not cantidad.isdigit() or int(cantidad) <= 0:
                self.view.label.setText("Datos de reserva inválidos.")
                return

            self.model.registrar_reserva({
                "id_item": id_item,
                "obra": obra,
                "cantidad": int(cantidad)
            })

            self.view.label.setText("Reserva registrada exitosamente.")
            self.actualizar_inventario()
            dialog.accept()
        except Exception as e:
            print(f"Error al procesar la reserva: {e}")
            self.view.label.setText("Error al procesar la reserva.")

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

                # Registro en auditoría
                for ajuste in datos_ajuste:
                    self.model.registrar_auditoria("Ajuste", ajuste["codigo"], ajuste["cantidad"], self.usuario_actual)
        except Exception as e:
            QMessageBox.critical(self.view, "Error", f"Error al ajustar el stock: {e}")

    def buscar_item(self):
        codigo = self.view.buscar_input.text()
        if codigo:
            item = self.model.obtener_item_por_codigo(codigo)
            if item:
                self.view.tabla_inventario.setRowCount(1)
                for col, value in enumerate(item[0]):
                    self.view.tabla_inventario.setItem(0, col, QTableWidgetItem(str(value)))
            else:
                self.view.label.setText("Ítem no encontrado.")

    def filtrar_resultados(self):
        try:
            criterio = self.view.buscar_input.text().lower()
            for row in range(self.view.tabla_inventario.rowCount()):
                mostrar_fila = False
                for col in range(self.view.tabla_inventario.columnCount()):
                    item = self.view.tabla_inventario.item(row, col)
                    if item and criterio in item.text().lower():
                        mostrar_fila = True
                        break
                self.view.tabla_inventario.setRowHidden(row, not mostrar_fila)
            self.view.label.setText("Filtro aplicado.")
        except Exception as e:
            print(f"Error al filtrar resultados: {e}")
            self.view.label.setText("Error al aplicar el filtro.")

    def exportar_inventario(self, formato):
        resultado = self.model.exportar_inventario(formato)
        self.view.label.setText(resultado)

    def generar_qr_para_item(self):
        id_item = self.view.id_item_input.text()
        if id_item:
            qr_code = self.model.generar_qr(id_item)
            if qr_code:
                self.view.label.setText(f"Código QR generado: {qr_code}")
            else:
                self.view.label.setText("Error al generar el código QR.")
        else:
            self.view.label.setText("Por favor, ingrese un ID de ítem válido.")

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

    def activar_modo_lectura(self):
        self.view.set_modo_lectura(True)

    def desactivar_modo_lectura(self):
        self.view.set_modo_lectura(False)

    def cancelar_reserva(self, id_reserva):
        resultado = self.model.cancelar_reserva(id_reserva)
        if resultado:
            self.view.label.setText("Reserva cancelada exitosamente.")
            self.actualizar_inventario()
        else:
            self.view.label.setText("Error al cancelar la reserva.")

    def transformar_reserva_en_entrega(self, id_reserva):
        resultado = self.model.transformar_reserva_en_entrega(id_reserva)
        if resultado:
            self.view.label.setText("Reserva transformada en entrega exitosamente.")
            self.actualizar_inventario()
        else:
            self.view.label.setText("Error al transformar la reserva en entrega.")

    def exportar_excel(self):
        try:
            from PyQt6.QtWidgets import QFileDialog
            import pandas as pd

            path, _ = QFileDialog.getSaveFileName(self.view, "Guardar como", "", "Archivos Excel (*.xlsx)")
            if not path:
                return

            data = []
            for row in range(self.view.tabla_inventario.rowCount()):
                row_data = []
                for col in range(self.view.tabla_inventario.columnCount()):
                    item = self.view.tabla_inventario.item(row, col)
                    row_data.append(item.text() if item else "")
                data.append(row_data)

            df = pd.DataFrame(data, columns=[self.view.tabla_inventario.horizontalHeaderItem(i).text() for i in range(self.view.tabla_inventario.columnCount())])
            df.to_excel(path, index=False)
            self.view.label.setText("Inventario exportado a Excel exitosamente.")
        except Exception as e:
            print(f"Error al exportar a Excel: {e}")
            self.view.label.setText("Error al exportar a Excel.")

    def exportar_pdf(self):
        try:
            from PyQt6.QtWidgets import QFileDialog
            from fpdf import FPDF

            path, _ = QFileDialog.getSaveFileName(self.view, "Guardar como", "", "Archivos PDF (*.pdf)")
            if not path:
                return

            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)

            # Agregar encabezados
            headers = [self.view.tabla_inventario.horizontalHeaderItem(i).text() for i in range(self.view.tabla_inventario.columnCount())]
            pdf.set_fill_color(200, 220, 255)
            for header in headers:
                pdf.cell(40, 10, header, 1, 0, 'C', fill=True)
            pdf.ln()

            # Agregar datos
            for row in range(self.view.tabla_inventario.rowCount()):
                for col in range(self.view.tabla_inventario.columnCount()):
                    item = self.view.tabla_inventario.item(row, col)
                    pdf.cell(40, 10, item.text() if item else "", 1)
                pdf.ln()

            pdf.output(path)
            self.view.label.setText("Inventario exportado a PDF exitosamente.")
        except Exception as e:
            print(f"Error al exportar a PDF: {e}")
            self.view.label.setText("Error al exportar a PDF.")

    def mostrar_historial(self):
        try:
            id_item = self.view.obtener_id_item_seleccionado()
            if not id_item:
                self.view.label.setText("Seleccione un ítem para ver sus movimientos.")
                return

            movimientos = self.model.obtener_movimientos(id_item)
            if not movimientos:
                self.view.label.setText("No se encontraron movimientos para este ítem.")
                return

            dialog = QDialog(self.view)
            dialog.setWindowTitle("Historial de Movimientos")

            layout = QVBoxLayout()
            tabla = QTableWidget()
            tabla.setColumnCount(5)
            tabla.setHorizontalHeaderLabels(["Fecha", "Usuario", "Acción", "Cantidad", "Observaciones"])

            tabla.setRowCount(len(movimientos))
            for row, movimiento in enumerate(movimientos):
                for col, value in enumerate(movimiento):
                    tabla.setItem(row, col, QTableWidgetItem(str(value)))

            layout.addWidget(tabla)
            dialog.setLayout(layout)
            dialog.exec()
        except Exception as e:
            print(f"Error al mostrar historial: {e}")
            self.view.label.setText("Error al mostrar el historial de movimientos.")

    def generar_codigo_qr(self):
        try:
            import qrcode
            from PyQt6.QtWidgets import QLabel, QVBoxLayout, QFileDialog
            from PyQt6.QtGui import QPixmap
            from PIL.ImageQt import ImageQt

            id_item = self.view.obtener_id_item_seleccionado()
            if not id_item:
                self.view.label.setText("Seleccione un ítem para generar el código QR.")
                return

            datos_item = self.model.obtener_item_por_id(id_item)
            if not datos_item:
                self.view.label.setText("No se encontraron datos para el ítem seleccionado.")
                return

            qr_data = f"ID: {datos_item['id']}, Código: {datos_item['codigo']}, Nombre: {datos_item['nombre']}"
            qr_image = qrcode.make(qr_data)

            dialog = QDialog(self.view)
            dialog.setWindowTitle("Código QR")

            layout = QVBoxLayout()
            qr_label = QLabel()

            qt_image = ImageQt(qr_image)
            pixmap = QPixmap.fromImage(qt_image)
            qr_label.setPixmap(pixmap)

            layout.addWidget(qr_label)

            guardar_button = QPushButton("Guardar como imagen")
            layout.addWidget(guardar_button)

            guardar_button.clicked.connect(lambda: self.guardar_qr_como_imagen(qr_image))

            dialog.setLayout(layout)
            dialog.exec()
        except Exception as e:
            print(f"Error al generar el código QR: {e}")
            self.view.label.setText("Error al generar el código QR.")

    def guardar_qr_como_imagen(self, qr_image):
        try:
            path, _ = QFileDialog.getSaveFileName(self.view, "Guardar como", "", "Archivos PNG (*.png)")
            if not path:
                return

            qr_image.save(path)
            self.view.label.setText("Código QR guardado exitosamente.")
        except Exception as e:
            print(f"Error al guardar el código QR: {e}")
            self.view.label.setText("Error al guardar el código QR.")
