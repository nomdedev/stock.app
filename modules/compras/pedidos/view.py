from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QFormLayout, QScrollArea, QFrame, QTableWidget, QTableWidgetItem, QPushButton, QSizePolicy, QHBoxLayout
from PyQt6.QtCore import Qt, QSize
from PyQt6 import QtGui, QtCore
from core.ui_components import CustomButton

class Pedidos(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.label_titulo = QLabel("Vista de Pedidos")
        self.layout.addWidget(self.label_titulo)
        self.setLayout(self.layout)

class PedidosView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)

        # Botones principales como iconos
        botones_layout = QHBoxLayout()
        self.boton_crear = QPushButton()
        self.boton_ver_detalles = QPushButton()
        self.boton_cargar_presupuesto = QPushButton()
        botones = [
            (self.boton_crear, "plus_icon.svg", "Crear nuevo pedido"),
            (self.boton_ver_detalles, "search_icon.svg", "Ver detalles del pedido"),
            (self.boton_cargar_presupuesto, "excel_icon.svg", "Cargar presupuesto"),
        ]
        for boton, icono, tooltip in botones:
            boton.setIcon(QtGui.QIcon(f"img/{icono}"))
            boton.setIconSize(QSize(12, 12))
            boton.setToolTip(tooltip)
            boton.setText("")
            boton.setFixedSize(15, 15)
            boton.setStyleSheet("""
                QPushButton {
                    background-color: #2563eb;
                    border-radius: 4px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #1e40af;
                }
                QPushButton:pressed {
                    background-color: #1e3a8a;
                }
            """)
            botones_layout.addWidget(boton)
        self.layout.addLayout(botones_layout)

    def resaltar_items_bajo_stock(self, items):
        for item in items:
            if item.stock is not None and item.stock < item.stock_minimo:
                item.resaltar()
