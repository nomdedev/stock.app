from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QFormLayout, QMessageBox

class VidriosView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()

        self.label = QLabel("Gestión de Vidrios")
        self.layout.addWidget(self.label)

        self.form_layout = QFormLayout()
        self.tipo_input = QLineEdit()
        self.dimensiones_input = QLineEdit()
        self.cantidad_input = QLineEdit()
        self.form_layout.addRow("Tipo:", self.tipo_input)
        self.form_layout.addRow("Dimensiones:", self.dimensiones_input)
        self.form_layout.addRow("Cantidad:", self.cantidad_input)
        self.layout.addLayout(self.form_layout)

        self.boton_agregar = QPushButton("Agregar Vidrio")
        self.layout.addWidget(self.boton_agregar)
        self.boton_agregar.clicked.connect(self.agregar_vidrio_placeholder)

        self.setLayout(self.layout)

    def agregar_vidrio_placeholder(self):
        QMessageBox.information(self, "En desarrollo", "La función 'Agregar Vidrio' está en desarrollo.")
