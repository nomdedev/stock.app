from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QFormLayout, QScrollArea, QFrame, QTableWidget, QTableWidgetItem, QPushButton, QSizePolicy, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6 import QtGui, QtCore
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
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)

        # Crear lista para almacenar los botones
        self.botones = []

        # Crear contenedor para los botones
        botones_layout = QHBoxLayout()
        botones_layout.setSpacing(10)  # Espaciado entre botones
        botones_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Centrar botones

        # Botón "Crear Pedido"
        self.boton_crear = QPushButton("Crear Pedido")
        self.boton_crear.setFixedSize(150, 30)
        self.boton_crear.setStyleSheet("""
            QPushButton {
                background-color: #2563eb; /* Azul */
                color: white; /* Texto blanco */
                border: none;
                border-radius: 15px; /* Bordes redondeados */
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1e40af; /* Azul más oscuro */
            }
            QPushButton:pressed {
                background-color: #1e3a8a; /* Azul aún más oscuro */
            }
        """)
        botones_layout.addWidget(self.boton_crear)
        self.botones.append(self.boton_crear)

        # Botón "Ver Detalles del Pedido"
        self.boton_ver_detalles = QPushButton("Ver Detalles del Pedido")
        self.boton_ver_detalles.setFixedSize(120, 25)
        self.boton_ver_detalles.setStyleSheet("""
            QPushButton {
                background-color: #2563eb; /* Azul */
                color: white; /* Texto blanco */
                border: none;
                border-radius: 15px; /* Bordes redondeados */
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1e40af; /* Azul más oscuro */
            }
            QPushButton:pressed {
                background-color: #1e3a8a; /* Azul aún más oscuro */
            }
        """)
        botones_layout.addWidget(self.boton_ver_detalles)
        self.botones.append(self.boton_ver_detalles)

        # Botón "Cargar Presupuesto"
        self.boton_cargar_presupuesto = QPushButton("Cargar Presupuesto")
        self.boton_cargar_presupuesto.setFixedSize(125, 25)
        self.boton_cargar_presupuesto.setStyleSheet("""
            QPushButton {
                background-color: #2563eb; /* Azul */
                color: white; /* Texto blanco */
                border: none;
                border-radius: 15px; /* Bordes redondeados */
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1e40af; /* Azul más oscuro */
            }
            QPushButton:pressed {
                background-color: #1e3a8a; /* Azul aún más oscuro */
            }
        """)
        botones_layout.addWidget(self.boton_cargar_presupuesto)
        self.botones.append(self.boton_cargar_presupuesto)

        # Ajustar los botones para que utilicen imágenes de la carpeta img
        botones = [
            ("Nuevo Ítem", "plus_icon.svg"),
            ("Ver Movimientos", "search_icon.svg"),
            ("Reservar", "reservar-mas.png"),
            ("Exportar a Excel", "excel_icon.svg"),
            ("Exportar a PDF", "pdf_icon.svg"),
            ("Buscar", "buscar.png"),
            ("Generar QR", "qr_icon.svg"),
            ("Actualizar Inventario", "refresh_icon.svg")
        ]

        for boton, (texto, icono) in zip(self.botones, botones):
            boton.setText("")  # Eliminar texto del botón
            boton.setIcon(QtGui.QIcon(f"img/{icono}"))
            boton.setIconSize(QtCore.QSize(24, 24))  # Tamaño del ícono
            boton.setStyleSheet("""
                QPushButton {
                    background-color: #2563eb; /* Azul */
                    border-radius: 8px; /* Bordes redondeados */
                    border: none;
                }
                QPushButton:hover {
                    background-color: #1e40af; /* Azul más oscuro */
                }
                QPushButton:pressed {
                    background-color: #1e3a8a; /* Azul aún más oscuro */
                }
            """)

        # Agregar el layout de botones al layout principal
        self.layout.addLayout(botones_layout)

    def resaltar_items_bajo_stock(self, items):
        for item in items:
            if item.stock is not None and item.stock < item.stock_minimo:
                item.resaltar()
