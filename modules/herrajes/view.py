from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QFormLayout, QTableWidget, QTableWidgetItem, QHBoxLayout, QGraphicsDropShadowEffect
from PyQt6.QtGui import QIcon, QColor
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
        self.boton_agregar.setIcon(QIcon("img/plus_icon.svg"))
        self.boton_agregar.setIconSize(QSize(24, 24))
        self.boton_agregar.setToolTip("Agregar nuevo herraje")
        self.boton_agregar.setText("")
        self.boton_agregar.setFixedSize(48, 48)
        self.boton_agregar.setStyleSheet("")
        self.boton_buscar = QPushButton()
        self.boton_buscar.setIcon(QIcon("img/buscar.png"))
        self.boton_buscar.setIconSize(QSize(24, 24))
        self.boton_buscar.setToolTip("Buscar herraje")
        self.boton_buscar.setText("")
        self.boton_buscar.setFixedSize(48, 48)
        self.boton_buscar.setStyleSheet("")
        self.boton_exportar_excel = QPushButton()
        self.boton_exportar_excel.setIcon(QIcon("img/excel_icon.svg"))
        self.boton_exportar_excel.setIconSize(QSize(24, 24))
        self.boton_exportar_excel.setToolTip("Exportar herrajes a Excel")
        self.boton_exportar_excel.setText("")
        self.boton_exportar_excel.setFixedSize(48, 48)
        self.boton_exportar_excel.setStyleSheet("")
        botones_layout.addWidget(self.boton_agregar)
        botones_layout.addWidget(self.boton_buscar)
        botones_layout.addWidget(self.boton_exportar_excel)
        botones_layout.addStretch()
        self.layout.addLayout(botones_layout)

        # Botón principal de acción estándar (para compatibilidad con el controlador)
        self.boton_accion = QPushButton()
        self.boton_accion.setIcon(QIcon("utils/herrajes.svg"))
        self.boton_accion.setToolTip("Agregar nuevo herraje")
        self.boton_accion.setFixedSize(48, 48)
        self.boton_accion.setIconSize(QSize(32, 32))
        self.boton_accion.setObjectName("boton_accion")
        self.layout.addWidget(self.boton_accion)

        # Sombra visual profesional para el botón principal
        def aplicar_sombra(widget):
            sombra = QGraphicsDropShadowEffect()
            sombra.setBlurRadius(15)
            sombra.setXOffset(0)
            sombra.setYOffset(4)
            sombra.setColor(QColor(0, 0, 0, 160))
            widget.setGraphicsEffect(sombra)
        aplicar_sombra(self.boton_accion)

        # Cargar el stylesheet visual moderno para Herrajes según el tema activo
        try:
            with open("themes/light.qss", "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"No se pudo cargar el archivo de estilos: {e}")

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
            boton.setStyleSheet("")
            botones_layout.addWidget(boton)

        self.layout.addLayout(botones_layout)
        self.setLayout(self.layout)
