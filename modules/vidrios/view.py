from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QFormLayout, QTableWidget, QTableWidgetItem, QDateEdit

class VidriosView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Gestión de Vidrios")
        self.layout = QVBoxLayout()

        # Encabezado
        self.label_titulo = QLabel("Gestión de Vidrios")
        self.layout.addWidget(self.label_titulo)

        # Formulario de entrada
        self.form_layout = self.create_form_layout()
        self.layout.addLayout(self.form_layout)

        # Botón para agregar vidrio
        self.boton_agregar = QPushButton("Agregar Vidrio")
        self.layout.addWidget(self.boton_agregar)

        # Tabla para mostrar los vidrios
        self.tabla_vidrios = self.create_table()
        self.layout.addWidget(self.tabla_vidrios)

        self.setLayout(self.layout)

    def create_form_layout(self):
        form_layout = QFormLayout()

        self.tipo_input = QLineEdit()
        self.ancho_input = QLineEdit()
        self.alto_input = QLineEdit()
        self.cantidad_input = QLineEdit()
        self.proveedor_input = QLineEdit()
        self.fecha_entrega_input = QDateEdit()
        self.fecha_entrega_input.setCalendarPopup(True)

        form_layout.addRow("Tipo:", self.tipo_input)
        form_layout.addRow("Ancho:", self.ancho_input)
        form_layout.addRow("Alto:", self.alto_input)
        form_layout.addRow("Cantidad:", self.cantidad_input)
        form_layout.addRow("Proveedor:", self.proveedor_input)
        form_layout.addRow("Fecha de Entrega:", self.fecha_entrega_input)

        return form_layout

    def create_table(self):
        table = QTableWidget()
        table.setColumnCount(6)
        table.setHorizontalHeaderLabels([
            "Tipo", "Ancho", "Alto", "Cantidad", "Proveedor", "Fecha de Entrega"
        ])
        return table
