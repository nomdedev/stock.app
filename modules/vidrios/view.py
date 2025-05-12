from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QFormLayout, QTableWidget, QTableWidgetItem, QDateEdit, QHBoxLayout, QGraphicsDropShadowEffect
from PyQt6.QtGui import QIcon, QColor
from PyQt6.QtCore import QSize
import json

class VidriosView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)

        self.setWindowTitle("Gestión de Vidrios")

        # Encabezado
        self.label_titulo = QLabel("Gestión de Vidrios")
        self.layout.addWidget(self.label_titulo)

        # Formulario de entrada
        self.form_layout = self.create_form_layout()
        self.layout.addLayout(self.form_layout)

        # Tabla para mostrar los vidrios
        self.tabla_vidrios = self.create_table()
        self.layout.addWidget(self.tabla_vidrios)

        # Cargar el stylesheet visual moderno para Vidrios según el tema activo
        try:
            with open("themes/config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
            tema = config.get("tema", "claro")
            archivo_qss = f"themes/{tema}.qss"
            with open(archivo_qss, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"No se pudo cargar el archivo de estilos: {e}")

        # Botones principales como iconos
        botones_layout = QHBoxLayout()
        self.boton_agregar = QPushButton()
        self.boton_agregar.setIcon(QIcon("img/add-material.svg"))
        self.boton_agregar.setIconSize(QSize(24, 24))
        self.boton_agregar.setToolTip("Agregar vidrio")
        self.boton_agregar.setText("")
        self.boton_agregar.setFixedSize(48, 48)
        self.boton_agregar.setStyleSheet("")
        self.boton_buscar = QPushButton()
        self.boton_buscar.setIcon(QIcon("img/search_icon.svg"))
        self.boton_buscar.setIconSize(QSize(24, 24))
        self.boton_buscar.setToolTip("Buscar vidrio")
        self.boton_buscar.setText("")
        self.boton_buscar.setFixedSize(48, 48)
        self.boton_buscar.setStyleSheet("")
        self.boton_exportar_excel = QPushButton()
        self.boton_exportar_excel.setIcon(QIcon("img/excel_icon.svg"))
        self.boton_exportar_excel.setIconSize(QSize(24, 24))
        self.boton_exportar_excel.setToolTip("Exportar vidrios a Excel")
        self.boton_exportar_excel.setText("")
        self.boton_exportar_excel.setFixedSize(48, 48)
        self.boton_exportar_excel.setStyleSheet("")
        botones_layout.addWidget(self.boton_agregar)
        botones_layout.addWidget(self.boton_buscar)
        botones_layout.addWidget(self.boton_exportar_excel)
        botones_layout.addStretch()
        self.layout.addLayout(botones_layout)

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
            "tipo", "ancho", "alto", "cantidad", "proveedor", "fecha_entrega"
        ])
        return table
