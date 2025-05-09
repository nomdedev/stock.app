from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QFormLayout, QLineEdit, QComboBox, QPushButton, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt

class PedidosView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Aplicar estilos globales desde los temas
        try:
            with open("themes/light.qss", "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"No se pudo cargar el archivo de estilos: {e}")

        # Tabla de pedidos
        self.tabla_pedidos = QTableWidget()
        self.tabla_pedidos.setColumnCount(5)
        self.tabla_pedidos.setHorizontalHeaderLabels(["ID", "Obra", "Fecha", "Estado", "Observaciones"])
        self.layout.addWidget(self.tabla_pedidos)

        # Formulario para nuevo pedido
        self.form_layout = QFormLayout()
        self.obra_combo = QComboBox()
        self.fecha_pedido = QLineEdit()
        self.materiales_input = QLineEdit()
        self.observaciones_input = QLineEdit()
        self.form_layout.addRow("Obra Asociada:", self.obra_combo)
        self.form_layout.addRow("Fecha de Pedido:", self.fecha_pedido)
        self.form_layout.addRow("Lista de Materiales:", self.materiales_input)
        self.form_layout.addRow("Observaciones:", self.observaciones_input)
        self.layout.addLayout(self.form_layout)

        # Botones
        self.botones_layout = QHBoxLayout()
        self.boton_nuevo = QPushButton("+")
        self.boton_eliminar = QPushButton("🗑️")
        self.boton_actualizar = QPushButton("🔄")
        self.boton_aprobar = QPushButton("✔️")
        self.boton_rechazar = QPushButton("❌")
        self.botones_layout.addWidget(self.boton_nuevo)
        self.botones_layout.addWidget(self.boton_eliminar)
        self.botones_layout.addWidget(self.boton_actualizar)
        self.botones_layout.addWidget(self.boton_aprobar)
        self.botones_layout.addWidget(self.boton_rechazar)
        self.layout.addLayout(self.botones_layout)

        # Ajustar espaciado y alineación para asegurar visibilidad
        self.botones_layout.setSpacing(10)
        self.botones_layout.setContentsMargins(0, 10, 0, 10)
        self.layout.setSpacing(15)

        # Verificar estilos aplicados
        print("Estilos aplicados correctamente a PedidosView.")

        # Señales
        self.boton_nuevo.clicked.connect(self.crear_pedido)
        self.boton_eliminar.clicked.connect(self.eliminar_pedido)
        self.boton_actualizar.clicked.connect(self.cargar_pedidos)
        self.boton_aprobar.clicked.connect(self.aprobar_pedido)
        self.boton_rechazar.clicked.connect(self.rechazar_pedido)

    def crear_pedido(self):
        pass

    def eliminar_pedido(self):
        pass

    def cargar_pedidos(self):
        pass

    def aprobar_pedido(self):
        pass

    def rechazar_pedido(self):
        pass
