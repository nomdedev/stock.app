from PyQt6.QtWidgets import QTableWidgetItem, QDialog
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
        except Exception as e:
            print(f"Error al actualizar inventario: {e}")
            self.view.label.setText("Error al cargar el inventario.")

    def agregar_item(self):
        try:
            datos = self.view.obtener_datos_nuevo_item()
            if not datos:
                self.view.label.setText("Error: Datos incompletos para agregar el ítem.")
                return

            codigo = datos.get("codigo")
            if not codigo:
                self.view.label.setText("Error: El código del ítem es obligatorio.")
                return

            if self.model.obtener_item_por_codigo(codigo):
                self.view.label.setText("Error: Ya existe un ítem con el mismo código.")
                self.view.buscar_input.setStyleSheet("border: 1px solid red;")
                return

            self.model.agregar_item(datos)
            self.view.label.setText("Ítem agregado exitosamente.")
            self.view.buscar_input.setStyleSheet("")
            self.actualizar_inventario()
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
        datos_reserva = self.view.obtener_datos_reserva()
        if datos_reserva:
            self.model.registrar_reserva(datos_reserva)
            self.view.label.setText("Reserva registrada exitosamente.")
            self.actualizar_inventario()
        else:
            self.view.label.setText("Error: Datos incompletos para registrar la reserva.")

    def ajustar_stock(self):
        dialog = self.view.abrir_ajustar_stock_dialog()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            datos_ajuste = dialog.obtener_datos_ajuste_stock()
            for ajuste in datos_ajuste:
                codigo = ajuste["codigo"]
                cantidad = ajuste["cantidad"]

                # Actualizar la tabla de inventario
                for row in range(self.view.tabla_inventario.rowCount()):
                    item_codigo = self.view.tabla_inventario.item(row, 1)  # Columna de código
                    item_stock = self.view.tabla_inventario.item(row, 11)  # Columna de stock
                    if item_codigo and item_codigo.text() == codigo:
                        stock_actual = int(item_stock.text()) if item_stock and item_stock.text().isdigit() else 0
                        nuevo_stock = stock_actual + cantidad
                        self.view.tabla_inventario.setItem(row, 11, QTableWidgetItem(str(nuevo_stock)))

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

    def resaltar_items_bajo_stock(self):
        try:
            items_bajo_stock = self.model.obtener_items_bajo_stock()
            for row in range(self.view.tabla_inventario.rowCount()):
                codigo_item = self.view.tabla_inventario.item(row, 0).text()
                for item in items_bajo_stock:
                    if codigo_item == item[1]:  # Suponiendo que el código está en la columna 1 del resultado
                        for col in range(self.view.tabla_inventario.columnCount()):
                            self.view.tabla_inventario.item(row, col).setBackground(QtGui.QColor("red"))
        except Exception as e:
            print(f"Error al resaltar ítems bajo stock: {e}")
            self.view.label.setText("Error al resaltar ítems con bajo stock.")

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
