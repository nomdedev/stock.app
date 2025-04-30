from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QFormLayout

class NotificacionesView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()

        self.label = QLabel("Gestión de Notificaciones")
        self.layout.addWidget(self.label)

        self.form_layout = QFormLayout()
        self.mensaje_input = QLineEdit()
        self.fecha_input = QLineEdit()
        self.tipo_input = QLineEdit()
        self.form_layout.addRow("Mensaje:", self.mensaje_input)
        self.form_layout.addRow("Fecha:", self.fecha_input)
        self.form_layout.addRow("Tipo:", self.tipo_input)
        self.layout.addLayout(self.form_layout)

        self.boton_agregar = QPushButton("Agregar Notificación")
        self.layout.addWidget(self.boton_agregar)

        self.setLayout(self.layout)
