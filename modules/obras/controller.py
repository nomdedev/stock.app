from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton

class ObrasController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.view.boton_agregar.clicked.connect(self.agregar_obra)
        self.view.boton_ver_cronograma.clicked.connect(self.ver_cronograma)
        self.view.boton_asignar_materiales.clicked.connect(self.asignar_materiales)
        self.view.boton_exportar_excel.clicked.connect(lambda: self.exportar_cronograma_seleccionada("excel"))
        self.view.boton_exportar_pdf.clicked.connect(lambda: self.exportar_cronograma_seleccionada("pdf"))

    def agregar_obra(self):
        nombre = self.view.nombre_input.text()
        cliente = self.view.cliente_input.text()
        estado = self.view.estado_input.text()

        if nombre and cliente and estado:
            self.model.agregar_obra((nombre, cliente, estado))
            self.view.label.setText("Obra agregada exitosamente.")
        else:
            self.view.label.setText("Por favor, complete todos los campos.")

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
