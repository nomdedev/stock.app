from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QFormLayout, QScrollArea, QFrame, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox
from PyQt6.QtCore import QSize

class PedidosView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()

        self.label = QLabel("Gestión de Pedidos")
        self.layout.addWidget(self.label)

        self.form_layout = QFormLayout()
        self.nombre_cliente_input = QLineEdit()
        self.fecha_pedido_input = QLineEdit()
        self.estado_pedido_input = QLineEdit()
        self.form_layout.addRow("Nombre del Cliente:", self.nombre_cliente_input)
        self.form_layout.addRow("Fecha del Pedido:", self.fecha_pedido_input)
        self.form_layout.addRow("Estado del Pedido:", self.estado_pedido_input)
        self.layout.addLayout(self.form_layout)

        self.boton_crear = QPushButton("Crear Pedido")
        self.layout.addWidget(self.boton_crear)

        self.boton_ver_detalles = QPushButton("Ver Detalles del Pedido")
        self.layout.addWidget(self.boton_ver_detalles)

        self.boton_cargar_presupuesto = QPushButton("Cargar Presupuesto")
        self.layout.addWidget(self.boton_cargar_presupuesto)

        self.tabla_pedidos = QTableWidget()
        self.tabla_pedidos.setColumnCount(3)
        self.tabla_pedidos.setHorizontalHeaderLabels(["Cliente", "Fecha", "Estado"])
        self.layout.addWidget(self.tabla_pedidos)

        self.setLayout(self.layout)

        self.boton_crear.clicked.connect(self.crear_pedido_placeholder)
        self.boton_ver_detalles.clicked.connect(self.ver_detalles_placeholder)
        self.boton_cargar_presupuesto.clicked.connect(self.cargar_presupuesto_placeholder)

    def crear_pedido_placeholder(self):
        QMessageBox.information(self, "En desarrollo", "La función 'Crear Pedido' está en desarrollo.")

    def ver_detalles_placeholder(self):
        QMessageBox.information(self, "En desarrollo", "La función 'Ver Detalles del Pedido' está en desarrollo.")

    def cargar_presupuesto_placeholder(self):
        QMessageBox.information(self, "En desarrollo", "La función 'Cargar Presupuesto' está en desarrollo.")
