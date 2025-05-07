class VidriosController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.view.boton_agregar.clicked.connect(self.agregar_vidrio)

    def agregar_vidrio(self):
        campos = {
            "tipo": self.view.tipo_input.text(),
            "ancho": self.view.ancho_input.text(),
            "alto": self.view.alto_input.text(),
            "cantidad": self.view.cantidad_input.text(),
            "proveedor": self.view.proveedor_input.text(),
            "fecha_entrega": self.view.fecha_entrega_input.date().toString("yyyy-MM-dd")
        }

        if all(campos.values()):
            self.model.agregar_vidrio(tuple(campos.values()))
            self.view.label.setText("Vidrio agregado exitosamente.")
            self.actualizar_tabla()
        else:
            self.view.label.setText("Por favor, complete todos los campos.")

    def actualizar_tabla(self):
        self.view.tabla_vidrios.setRowCount(0)
        vidrios = self.model.obtener_vidrios()
        for row, vidrio in enumerate(vidrios):
            self.view.tabla_vidrios.insertRow(row)
            for col, value in enumerate(vidrio):
                self.view.tabla_vidrios.setItem(row, col, QTableWidgetItem(str(value)))
