from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox
from PyQt6 import QtCore

class ObrasController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.view.boton_agregar.clicked.connect(self.agregar_obra)
        self.view.boton_ver_cronograma.clicked.connect(self.ver_cronograma)
        self.view.boton_asignar_materiales.clicked.connect(self.asignar_materiales)
        self.view.boton_exportar_excel.clicked.connect(lambda: self.exportar_cronograma_seleccionada("excel"))
        self.view.boton_exportar_pdf.clicked.connect(lambda: self.exportar_cronograma_seleccionada("pdf"))
        self.cargar_datos_obras()  # Cargar datos al iniciar

    def cargar_datos_obras(self):
        """Carga los datos de la tabla de obras en la vista."""
        try:
            datos = self.model.obtener_datos_obras()
            self.view.tabla_obras.setRowCount(len(datos))
            for row_idx, row_data in enumerate(datos):
                for col_idx, value in enumerate(row_data):
                    self.view.tabla_obras.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
        except Exception as e:
            self.view.label.setText(f"Error al cargar datos: {e}")

    def cargar_datos_cronograma(self, id_obra):
        """Carga los datos del cronograma de una obra en la pestaña de cronograma."""
        try:
            cronograma = self.model.obtener_cronograma_por_obra(id_obra)
            self.view.tabla_cronograma.setRowCount(len(cronograma))
            for row_idx, row_data in enumerate(cronograma):
                for col_idx, value in enumerate(row_data):
                    self.view.tabla_cronograma.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
        except Exception as e:
            self.view.label.setText(f"Error al cargar cronograma: {e}")

    def actualizar_calendario(self):
        """Actualiza el calendario con las fechas del cronograma."""
        try:
            cronograma = self.model.obtener_todas_las_fechas()
            for fecha in cronograma:
                # Aquí puedes agregar lógica para resaltar fechas en el calendario
                print(f"Fecha programada: {fecha}")
        except Exception as e:
            self.view.label.setText(f"Error al actualizar calendario: {e}")

    def agregar_obra(self):
        """Agrega una nueva obra con los datos ingresados."""
        nombre = self.view.nombre_input.text()
        cliente = self.view.cliente_input.text()
        estado = self.view.estado_input.currentText()  # Obtener el estado seleccionado

        if not (nombre and cliente and estado):
            self.view.label.setText("Por favor, complete todos los campos.")
            return

        if self.model.verificar_obra_existente(nombre, cliente):
            QMessageBox.warning(
                self.view,
                "Obra Existente",
                "Ya existe una obra con el mismo nombre y cliente."
            )
            self.view.nombre_input.setStyleSheet("border: 1px solid red;")
            self.view.cliente_input.setStyleSheet("border: 1px solid red;")
            return

        # Guardar la obra con el estado seleccionado y la fecha actual
        fecha_actual = QtCore.QDate.currentDate().toString("yyyy-MM-dd")
        self.model.agregar_obra((nombre, cliente, estado, fecha_actual))
        self.view.label.setText("Obra agregada exitosamente.")
        self.view.nombre_input.setStyleSheet("")
        self.view.cliente_input.setStyleSheet("")
        self.cargar_datos_obras()  # Recargar la tabla de obras

    def ver_cronograma(self):
        fila_seleccionada = self.view.tabla_obras.currentRow()
        if fila_seleccionada != -1:
            id_obra = self.view.tabla_obras.item(fila_seleccionada, 0).text()
            cronograma = self.model.obtener_cronograma_por_obra(id_obra)
            # Crear ventana emergente
            dialog = QDialog(self.view)
            dialog.setWindowTitle(f"Cronograma de Obra {id_obra}")
            layout = QVBoxLayout(dialog)
            label = QLabel(f"Cronograma de la obra seleccionada (ID: {id_obra})")
            layout.addWidget(label)
            tabla = QTableWidget()
            tabla.setColumnCount(6)
            tabla.setHorizontalHeaderLabels(["Etapa", "Fecha Programada", "Fecha Realizada", "Observaciones", "Responsable", "Estado"])
            tabla.setRowCount(len(cronograma))
            for row, etapa in enumerate(cronograma):
                for col, value in enumerate(etapa):
                    tabla.setItem(row, col, QTableWidgetItem(str(value)))
            layout.addWidget(tabla)
            btn_cerrar = QPushButton("Cerrar")
            btn_cerrar.clicked.connect(dialog.accept)
            layout.addWidget(btn_cerrar)
            dialog.exec()
        else:
            self.view.label.setText("Seleccione una obra para ver su cronograma.")

    def asignar_materiales(self):
        fila_seleccionada = self.view.tabla_obras.currentRow()
        if fila_seleccionada != -1:
            id_obra = self.view.tabla_obras.item(fila_seleccionada, 0).text()
            id_item = 1  # Ejemplo, debería seleccionarse dinámicamente
            cantidad_necesaria = 10
            cantidad_reservada = 5
            estado = "pendiente"
            self.model.asignar_material_a_obra((id_obra, id_item, cantidad_necesaria, cantidad_reservada, estado))
            self.view.label.setText(f"Material asignado a la obra {id_obra}.")

    def exportar_cronograma(self, id_obra, formato):
        mensaje = self.model.exportar_cronograma(formato, id_obra)
        self.view.label.setText(mensaje)

    def exportar_cronograma_seleccionada(self, formato):
        fila_seleccionada = self.view.tabla_obras.currentRow()
        if fila_seleccionada != -1:
            id_obra = self.view.tabla_obras.item(fila_seleccionada, 0).text()
            self.exportar_cronograma(id_obra, formato)
        else:
            self.view.label.setText("Seleccione una obra para exportar su cronograma.")

    def sincronizar_materiales_con_inventario(self, id_obra):
        materiales = self.model.obtener_materiales_por_obra(id_obra)
        for material in materiales:
            id_item = material[1]  # Suponiendo que el ID del ítem está en la columna 1
            cantidad_reservada = material[3]  # Suponiendo que la cantidad reservada está en la columna 3
            self.inventario_model.actualizar_stock(id_item, -cantidad_reservada)  # Reducir stock
        self.view.label.setText(f"Materiales de la obra {id_obra} sincronizados con el inventario.")
