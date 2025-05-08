from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QFormLayout, QTableWidget, QTableWidgetItem, QHBoxLayout
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize

class HerrajesView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()

        self.label_titulo = QLabel("Gestión de Herrajes")
        self.layout.addWidget(self.label_titulo)

        self.form_layout = QFormLayout()
        self.nombre_input = QLineEdit()
        self.cantidad_input = QLineEdit()
        self.proveedor_input = QLineEdit()
        self.form_layout.addRow("Nombre:", self.nombre_input)
        self.form_layout.addRow("Cantidad:", self.cantidad_input)
        self.form_layout.addRow("Proveedor:", self.proveedor_input)
        self.layout.addLayout(self.form_layout)

        # Botones principales como iconos
        botones_layout = QHBoxLayout()
        self.boton_agregar = QPushButton()
        self.boton_buscar = QPushButton()
        self.boton_exportar_excel = QPushButton()
        botones = [
            self.boton_agregar,
            self.boton_buscar,
            self.boton_exportar_excel,
        ]
        iconos = [
            ("plus_icon.svg", "Agregar nuevo herraje"),
            ("buscar.png", "Buscar herraje"),
            ("excel_icon.svg", "Exportar herrajes a Excel"),
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

        self.setLayout(self.layout)

    @property
    def label_estado(self):
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

class MaterialesView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()

        # Tabla de materiales
        self.tabla_materiales = QTableWidget()
        self.tabla_materiales.setColumnCount(7)
        self.tabla_materiales.setHorizontalHeaderLabels([
            "ID", "Código", "Descripción", "Cantidad", "Ubicación", "Fecha Ingreso", "Observaciones"
        ])
        self.layout.addWidget(self.tabla_materiales)

        # Botones principales como iconos
        botones_layout = QHBoxLayout()
        self.boton_agregar = QPushButton()
        self.boton_modificar = QPushButton()
        self.boton_eliminar = QPushButton()
        self.boton_buscar = QPushButton()
        self.boton_exportar_excel = QPushButton()
        self.boton_exportar_pdf = QPushButton()
        self.boton_ver_movimientos = QPushButton()

        botones = [
            self.boton_agregar, self.boton_modificar, self.boton_eliminar,
            self.boton_buscar, self.boton_exportar_excel, self.boton_exportar_pdf,
            self.boton_ver_movimientos
        ]

        iconos = [
            ("plus_icon.svg", "Agregar nuevo material"),
            ("edit_icon.svg", "Modificar material"),
            ("delete_icon.svg", "Eliminar material"),
            ("buscar.png", "Buscar material"),
            ("excel_icon.svg", "Exportar materiales a Excel"),
            ("pdf_icon.svg", "Exportar materiales a PDF"),
            ("movements_icon.svg", "Ver movimientos de materiales"),
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
        self.setLayout(self.layout)
