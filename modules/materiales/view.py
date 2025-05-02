from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QFormLayout, QMessageBox

class MaterialesView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()

        self.label = QLabel("Gestión de Materiales")
        self.layout.addWidget(self.label)

        self.form_layout = QFormLayout()
        self.nombre_input = QLineEdit()
        self.cantidad_input = QLineEdit()
        self.proveedor_input = QLineEdit()
        self.form_layout.addRow("Nombre:", self.nombre_input)
        self.form_layout.addRow("Cantidad:", self.cantidad_input)
        self.form_layout.addRow("Proveedor:", self.proveedor_input)
        self.layout.addLayout(self.form_layout)

        self.boton_agregar = QPushButton("Agregar Material")
        self.layout.addWidget(self.boton_agregar)

        self.setLayout(self.layout)

    def configurar_eventos(self):
        self.boton_agregar.clicked.connect(self.agregar_material_placeholder)

    def agregar_material_placeholder(self):
        QMessageBox.information(self, "En desarrollo", "La función 'Agregar Material' está en desarrollo.")
