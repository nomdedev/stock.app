from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QFormLayout, QLineEdit, QComboBox, QPushButton, QLabel, QHBoxLayout, QGraphicsDropShadowEffect
from PyQt6.QtGui import QIcon, QColor
from PyQt6.QtCore import Qt, QSize
import json

class PedidosView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Cargar el stylesheet visual moderno para Pedidos según el tema activo
        try:
            with open("themes/config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
            tema = config.get("tema", "claro")
            archivo_qss = f"themes/{tema}.qss"
            with open(archivo_qss, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"No se pudo cargar el archivo de estilos: {e}")

        # Tabla de pedidos
        self.tabla_pedidos = QTableWidget()
        self.tabla_pedidos.setColumnCount(5)
        self.tabla_pedidos.setHorizontalHeaderLabels([
            "id", "obra", "fecha", "estado", "observaciones"
        ])
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

        # Botón principal de acción (Agregar pedido)
        self.botones_layout = QHBoxLayout()
        self.boton_nuevo = QPushButton()
        self.boton_nuevo.setIcon(QIcon("img/add-entrega.svg"))
        self.boton_nuevo.setIconSize(QSize(24, 24))
        self.boton_nuevo.setToolTip("Agregar pedido")
        self.boton_nuevo.setText("")
        self.boton_nuevo.setFixedSize(48, 48)
        self.boton_nuevo.setStyleSheet("")
        sombra = QGraphicsDropShadowEffect()
        sombra.setBlurRadius(15)
        sombra.setXOffset(0)
        sombra.setYOffset(4)
        sombra.setColor(QColor(0, 0, 0, 50))
        self.boton_nuevo.setGraphicsEffect(sombra)
        self.botones_layout.addWidget(self.boton_nuevo)
        self.botones_layout.addStretch()
        self.layout.addLayout(self.botones_layout)

        # Ajustar espaciado y alineación para asegurar visibilidad
        self.botones_layout.setSpacing(10)
        self.botones_layout.setContentsMargins(0, 10, 0, 10)
        self.layout.setSpacing(15)

        # Verificar estilos aplicados
        print("Estilos aplicados correctamente a PedidosView.")

        # Señales
        self.boton_nuevo.clicked.connect(self.crear_pedido)

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
