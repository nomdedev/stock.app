from PyQt6.QtWidgets import QMessageBox

class HerrajesController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.view.boton_agregar.clicked.connect(self.agregar_material)

    def agregar_material(self):
        nombre = self.view.nombre_input.text()
        cantidad = self.view.cantidad_input.text()
        proveedor = self.view.proveedor_input.text()

        if not (nombre and cantidad and proveedor):
            self.view.label.setText("Por favor, complete todos los campos.")
            return

        if self.model.verificar_material_existente(nombre):
            QMessageBox.warning(
                self.view,
                "Material Existente",
                "Ya existe un material con el mismo nombre."
            )
            self.view.nombre_input.setStyleSheet("border: 1px solid red;")
            return

        self.model.agregar_material((nombre, cantidad, proveedor))
        self.view.label.setText("Material agregado exitosamente.")
        self.view.nombre_input.setStyleSheet("")
