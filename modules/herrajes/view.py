from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QFormLayout, QTableWidget, QTableWidgetItem, QHBoxLayout, QGraphicsDropShadowEffect
from PyQt6.QtGui import QIcon, QColor
from PyQt6.QtCore import QSize
import json

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

        # Botón principal de acción (Agregar)
        botones_layout = QHBoxLayout()
        self.boton_agregar = QPushButton()
        self.boton_agregar.setIcon(QIcon("img/add-material.svg"))
        self.boton_agregar.setIconSize(QSize(24, 24))
        self.boton_agregar.setToolTip("Agregar nuevo herraje")
        self.boton_agregar.setText("")
        self.boton_agregar.setFixedSize(48, 48)
        self.boton_agregar.setStyleSheet("")
        sombra = QGraphicsDropShadowEffect()
        sombra.setBlurRadius(15)
        sombra.setXOffset(0)
        sombra.setYOffset(4)
        sombra.setColor(QColor(0, 0, 0, 50))
        self.boton_agregar.setGraphicsEffect(sombra)
        botones_layout.addWidget(self.boton_agregar)
        botones_layout.addStretch()
        self.layout.addLayout(botones_layout)

        # Cargar el stylesheet visual moderno para Herrajes según el tema activo
        try:
            with open("themes/config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
            tema = config.get("tema", "claro")
            archivo_qss = f"themes/{tema}.qss"
            with open(archivo_qss, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"No se pudo cargar el archivo de estilos de Herrajes: {e}")

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

        # Botón principal de acción (Agregar)
        botones_layout = QHBoxLayout()
        self.boton_agregar = QPushButton()
        self.boton_agregar.setIcon(QIcon("img/plus_icon.svg"))
        self.boton_agregar.setIconSize(QSize(32, 32))
        self.boton_agregar.setToolTip("Agregar nuevo material")
        self.boton_agregar.setText("")
        self.boton_agregar.setFixedSize(48, 48)
        self.boton_agregar.setStyleSheet("")
        sombra = QGraphicsDropShadowEffect()
        sombra.setBlurRadius(15)
        sombra.setXOffset(0)
        sombra.setYOffset(4)
        sombra.setColor(QColor(0, 0, 0, 50))
        self.boton_agregar.setGraphicsEffect(sombra)
        botones_layout.addWidget(self.boton_agregar)
        botones_layout.addStretch()
        self.layout.addLayout(botones_layout)

        self.setLayout(self.layout)
