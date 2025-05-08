from PyQt6.QtWidgets import QWidget, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QTabWidget, QLabel, QLineEdit, QHBoxLayout
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize
from modules.compras.pedidos.view import PedidosView  # Importar desde el módulo correcto

class ComprasView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.inicializar_botones()

        # Crear QTabWidget para las pestañas
        self.tab_widget = QTabWidget()

        # Crear pestaña de Pedidos
        self.tab_pedidos = PedidosView()
        self.tab_widget.addTab(self.tab_pedidos, "Pedidos")

        # Agregar el QTabWidget al layout principal
        self.layout.addWidget(self.tab_widget)

    def inicializar_botones(self):
        # Botones principales como iconos
        botones_layout = QHBoxLayout()
        botones = [
            QPushButton(),  # Nuevo Pedido
            QPushButton(),  # Comparar Presupuestos
            QPushButton(),  # Exportar a Excel
        ]
        iconos = [
            ("plus_icon.svg", "Nuevo pedido"),
            ("search_icon.svg", "Comparar presupuestos"),
            ("excel_icon.svg", "Exportar pedidos a Excel"),
        ]
        for boton, (icono, tooltip) in zip(botones, iconos):
            boton.setIcon(QIcon(f"img/{icono}"))
            boton.setIconSize(QSize(32, 32))
            boton.setToolTip(tooltip)
            boton.setText("")
            boton.setFixedSize(48, 48)
            boton.setStyleSheet("""
                QPushButton {
                    background-color: #2563eb;
                    border-radius: 12px;
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

    def mostrar_comparacion_presupuestos(self, presupuestos):
        self.tabla_comparacion = QTableWidget()
        self.tabla_comparacion.setRowCount(len(presupuestos))
        self.tabla_comparacion.setColumnCount(3)
        self.tabla_comparacion.setHorizontalHeaderLabels(["Proveedor", "Precio Total", "Comentarios"])

        for row_idx, presupuesto in enumerate(presupuestos):
            self.tabla_comparacion.setItem(row_idx, 0, QTableWidgetItem(presupuesto[0]))
            self.tabla_comparacion.setItem(row_idx, 1, QTableWidgetItem(str(presupuesto[1])))
            self.tabla_comparacion.setItem(row_idx, 2, QTableWidgetItem(presupuesto[2]))

        self.layout.addWidget(self.tabla_comparacion)

    @property
    def label(self):
        if not hasattr(self, '_label_estado'):
            self._label_estado = QLabel()
        return self._label_estado

    @property
    def buscar_input(self):
        if not hasattr(self, '_buscar_input'):
            self._buscar_input = QLineEdit()
        return self._buscar_input

    @property
    def id_item_input(self):
        if not hasattr(self, '_id_item_input'):
            self._id_item_input = QLineEdit()
        return self._id_item_input