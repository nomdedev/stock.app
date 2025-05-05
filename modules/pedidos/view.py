from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QFormLayout, QScrollArea, QFrame, QTableWidget, QTableWidgetItem, QPushButton, QSizePolicy
from core.ui_components import CustomButton

class Pedidos(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.label = QLabel("Vista de Pedidos")
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

class PedidosView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel("Gestión de Pedidos")
        self.label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        self.layout.addWidget(self.label)

        # Ajustar otros elementos al estilo dashboard
        self.form_layout = QFormLayout()
        self.cliente_input = QLineEdit()
        self.producto_input = QLineEdit()
        self.cantidad_input = QLineEdit()
        self.fecha_input = QLineEdit()
        self.form_layout.addRow("Cliente:", self.cliente_input)
        self.form_layout.addRow("Producto:", self.producto_input)
        self.form_layout.addRow("Cantidad:", self.cantidad_input)
        self.form_layout.addRow("Fecha:", self.fecha_input)
        self.layout.addLayout(self.form_layout)

        self.boton_crear = QPushButton("Crear Pedido")
        self.boton_crear.setStyleSheet("""
            QPushButton {
                background-color: #2563eb; /* Azul */
                color: white; /* Texto blanco */
                text-align: center; /* Centrar texto */
                border: none;
                font-size: 14px; /* Tamaño de letra */
                font-weight: bold; /* Negrita */
                border-radius: 8px; /* Bordes redondeados */
            }
            QPushButton:hover {
                background-color: #1e40af; /* Azul más oscuro */
            }
            QPushButton:pressed {
                background-color: #1e3a8a; /* Azul aún más oscuro */
            }
        """)
        self.boton_crear.setFixedWidth(100)
        self.boton_crear.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.layout.addWidget(self.boton_crear)

        # Botón para ver detalles del pedido
        self.boton_ver_detalles = CustomButton("Ver Detalles del Pedido")
        self.boton_ver_detalles.setStyleSheet("""
            QPushButton {
                background-color: #2563eb; /* Azul */
                color: white; /* Texto blanco */
                text-align: center; /* Centrar texto */
                border: none;
                font-size: 14px; /* Tamaño de letra */
                font-weight: bold; /* Negrita */
                border-radius: 8px; /* Bordes redondeados */
            }
            QPushButton:hover {
                background-color: #1e40af; /* Azul más oscuro */
            }
            QPushButton:pressed {
                background-color: #1e3a8a; /* Azul aún más oscuro */
            }
        """)
        self.boton_ver_detalles.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.layout.addWidget(self.boton_ver_detalles)

        # Botón para cargar presupuesto
        self.boton_cargar_presupuesto = CustomButton("Cargar Presupuesto")
        self.boton_cargar_presupuesto.setStyleSheet("""
            QPushButton {
                background-color: #2563eb; /* Azul */
                color: white; /* Texto blanco */
                text-align: center; /* Centrar texto */
                border: none;
                font-size: 14px; /* Tamaño de letra */
                font-weight: bold; /* Negrita */
                border-radius: 8px; /* Bordes redondeados */
            }
            QPushButton:hover {
                background-color: #1e40af; /* Azul más oscuro */
            }
            QPushButton:pressed {
                background-color: #1e3a8a; /* Azul aún más oscuro */
            }
        """)
        self.boton_cargar_presupuesto.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.layout.addWidget(self.boton_cargar_presupuesto)

        # Botón de ejemplo
        self.boton_ejemplo = QPushButton("Ejemplo Pedidos")
        self.boton_ejemplo.setFixedHeight(40)  # Altura fija
        self.boton_ejemplo.setFixedWidth(150)  # Ancho fijo
        self.boton_ejemplo.setStyleSheet("""
            QPushButton {
                background-color: #2563eb; /* Azul */
                color: white; /* Texto blanco */
                text-align: center; /* Centrar texto */
                border: none;
                font-size: 14px; /* Tamaño de letra */
                font-weight: bold; /* Negrita */
                border-radius: 8px; /* Bordes redondeados */
            }
            QPushButton:hover {
                background-color: #1e40af; /* Azul más oscuro */
            }
            QPushButton:pressed {
                background-color: #1e3a8a; /* Azul aún más oscuro */
            }
        """)
        self.layout.addWidget(self.boton_ejemplo)

        # Tabla principal de pedidos
        self.tabla_pedidos = QTableWidget()
        self.tabla_pedidos.setColumnCount(6)
        self.tabla_pedidos.setHorizontalHeaderLabels([
            "ID del Pedido", "Cliente", "Producto", "Cantidad", "Fecha", "Estado"
        ])
        self.tabla_pedidos.horizontalHeader().setStretchLastSection(True)
        self.tabla_pedidos.setStyleSheet("""
            QTableWidget {
                border: 1px solid #dcdcdc;
                background-color: #f9f9f9;
                font-size: 12px;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                font-weight: bold;
                border: 1px solid #dcdcdc;
            }
        """)
        self.layout.addWidget(self.tabla_pedidos)

        # Tabla de detalles del pedido
        self.tabla_detalle_pedido = QTableWidget()
        self.tabla_detalle_pedido.setColumnCount(5)
        self.tabla_detalle_pedido.setHorizontalHeaderLabels(["Ítem", "Cantidad", "Unidad", "Justificación", "Acción"])
        self.tabla_detalle_pedido.horizontalHeader().setStyleSheet("")
        self.layout.addWidget(self.tabla_detalle_pedido)

        # Tabla de presupuestos
        self.tabla_presupuestos = QTableWidget()
        self.tabla_presupuestos.setColumnCount(6)
        self.tabla_presupuestos.setHorizontalHeaderLabels(["Proveedor", "Fecha", "Archivo", "Comentarios", "Precio Total", "Seleccionado"])
        self.tabla_presupuestos.horizontalHeader().setStyleSheet("")
        self.layout.addWidget(self.tabla_presupuestos)

        # Vista Kanban
        self.kanban_scroll = QScrollArea()
        self.kanban_scroll.setWidgetResizable(True)
        self.kanban_frame = QFrame()
        self.kanban_layout = QVBoxLayout(self.kanban_frame)
        self.kanban_scroll.setWidget(self.kanban_frame)
        self.layout.addWidget(self.kanban_scroll)

        # Agregar un QLabel para mostrar mensajes de estado o error
        self.label = QLabel()
        self.label.setStyleSheet("color: red; font-weight: bold;")
        self.layout.addWidget(self.label)

        self.controller = None

    def agregar_tarjeta_kanban(self, titulo, descripcion):
        tarjeta = QFrame()
        tarjeta.setStyleSheet("""
            QFrame {
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                padding: 10px;
                background-color: #f8f9fc;
            }
        """)
        tarjeta_layout = QVBoxLayout(tarjeta)
        tarjeta_titulo = QLabel(titulo)
        tarjeta_titulo.setStyleSheet("font-weight: bold;")
        tarjeta_descripcion = QLabel(descripcion)
        tarjeta_layout.addWidget(tarjeta_titulo)
        tarjeta_layout.addWidget(tarjeta_descripcion)
        self.kanban_layout.addWidget(tarjeta)

    def mostrar_comparacion_presupuestos(self, comparacion):
        self.tabla_comparacion = QTableWidget()
        self.tabla_comparacion.setColumnCount(6)
        self.tabla_comparacion.setHorizontalHeaderLabels(["Proveedor", "Fecha", "Archivo", "Comentarios", "Precio Total", "Seleccionado"])
        self.tabla_comparacion.setRowCount(len(comparacion))
        self.tabla_comparacion.horizontalHeader().setStyleSheet("")
        for row, presupuesto in enumerate(comparacion):
            for col, value in enumerate(presupuesto):
                self.tabla_comparacion.setItem(row, col, QTableWidgetItem(str(value)))
        self.layout.addWidget(self.tabla_comparacion)
