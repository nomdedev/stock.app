class MaterialesController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.view.boton_agregar.clicked.connect(self.agregar_material)

    def agregar_material(self):
        nombre = self.view.nombre_input.text()
        cantidad = self.view.cantidad_input.text()
        proveedor = self.view.proveedor_input.text()

        if nombre and cantidad and proveedor:
            self.model.agregar_material((nombre, cantidad, proveedor))
            self.view.label.setText("Material agregado exitosamente.")
        else:
            self.view.label.setText("Por favor, complete todos los campos.")
