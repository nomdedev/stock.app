class VidriosController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.view.boton_agregar.clicked.connect(self.agregar_vidrio)

    def agregar_vidrio(self):
        campos = {
            "tipo": self.view.tipo_input.text(),
            "dimensiones": self.view.dimensiones_input.text(),
            "cantidad": self.view.cantidad_input.text()
        }

        if all(campos.values()):
            self.model.agregar_vidrio(tuple(campos.values()))
            self.view.label.setText("Vidrio agregado exitosamente.")
        else:
            self.view.label.setText("Por favor, complete todos los campos.")
