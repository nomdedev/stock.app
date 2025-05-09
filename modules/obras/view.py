from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QFormLayout, QTableWidget, QTabWidget, QCalendarWidget, QPushButton, QHBoxLayout, QComboBox
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
from core.ui_components import CustomButton
from modules.obras.produccion.view import ProduccionView  # Importar ProduccionView desde el módulo correcto

class ObrasView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()

        # Cargar el stylesheet visual moderno para Obras
        try:
            with open("styles/inventario_styles.qss", "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"No se pudo cargar inventario_styles.qss: {e}")

        self.label_titulo = QLabel("Gestión de Obras")
        self.label_titulo.setStyleSheet("font-size: 10px; font-weight: bold; margin-bottom: 10px;")
        self.layout.addWidget(self.label_titulo)

        # Formulario de entrada
        self.form_layout = QFormLayout()
        self.nombre_input = QLineEdit()
        self.nombre_input.setFixedWidth(500)
        self.cliente_input = QLineEdit()
        self.cliente_input.setFixedWidth(500)
        self.estado_input = QComboBox()  # Cambiar a QComboBox para seleccionar estados
        self.estado_input.addItems(["Medición", "Fabricación", "Entrega"])  # Estados predeterminados
        self.estado_input.setFixedWidth(500)
        self.form_layout.addRow("Nombre:", self.nombre_input)
        self.form_layout.addRow("Cliente:", self.cliente_input)
        self.form_layout.addRow("Estado:", self.estado_input)
        self.layout.addLayout(self.form_layout)

        # Crear pestañas
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # Pestaña de Cronograma
        self.tab_cronograma = QWidget()
        self.tab_cronograma_layout = QVBoxLayout()

        self.tabla_cronograma = QTableWidget()
        self.tabla_cronograma.setColumnCount(6)
        self.tabla_cronograma.setHorizontalHeaderLabels(["Etapa", "Fecha Programada", "Fecha Realizada", "Observaciones", "Responsable", "Estado"])
        self.tabla_cronograma.horizontalHeader().setStretchLastSection(True)
        self.tab_cronograma_layout.addWidget(self.tabla_cronograma)

        self.tab_cronograma.setLayout(self.tab_cronograma_layout)
        self.tabs.addTab(self.tab_cronograma, "Cronograma")

        # Pestaña de Calendario
        self.tab_calendario = QWidget()
        self.tab_calendario_layout = QVBoxLayout()

        self.calendario = QCalendarWidget()
        self.calendario.setGridVisible(True)
        self.tab_calendario_layout.addWidget(self.calendario)

        self.tab_calendario.setLayout(self.tab_calendario_layout)
        self.tabs.addTab(self.tab_calendario, "Calendario")

        # Pestaña de Producción
        self.tab_produccion = ProduccionView()
        self.tabs.addTab(self.tab_produccion, "Producción")

        # Botones principales como iconos
        botones_layout = QHBoxLayout()
        self.boton_agregar = QPushButton()
        self.boton_agregar.setIcon(QIcon("img/plus_icon.svg"))
        self.boton_agregar.setIconSize(QSize(24, 24))
        self.boton_agregar.setToolTip("Agregar nueva obra")
        self.boton_agregar.setText("")
        self.boton_agregar.setFixedSize(48, 48)
        self.boton_agregar.setStyleSheet("")
        self.boton_ver_detalles = QPushButton()
        self.boton_ver_detalles.setIcon(QIcon("img/search_icon.svg"))
        self.boton_ver_detalles.setIconSize(QSize(24, 24))
        self.boton_ver_detalles.setToolTip("Ver detalles de obra")
        self.boton_ver_detalles.setText("")
        self.boton_ver_detalles.setFixedSize(48, 48)
        self.boton_ver_detalles.setStyleSheet("")
        self.boton_ver_cronograma = QPushButton()
        self.boton_ver_cronograma.setIcon(QIcon("img/calendar_icon.svg"))
        self.boton_ver_cronograma.setIconSize(QSize(24, 24))
        self.boton_ver_cronograma.setToolTip("Ver cronograma")
        self.boton_ver_cronograma.setText("")
        self.boton_ver_cronograma.setFixedSize(48, 48)
        self.boton_ver_cronograma.setStyleSheet("")
        self.boton_exportar_excel = QPushButton()
        self.boton_exportar_excel.setIcon(QIcon("img/excel_icon.svg"))
        self.boton_exportar_excel.setIconSize(QSize(24, 24))
        self.boton_exportar_excel.setToolTip("Exportar obras a Excel")
        self.boton_exportar_excel.setText("")
        self.boton_exportar_excel.setFixedSize(48, 48)
        self.boton_exportar_excel.setStyleSheet("")
        botones_layout.addWidget(self.boton_agregar)
        botones_layout.addWidget(self.boton_ver_detalles)
        botones_layout.addWidget(self.boton_ver_cronograma)
        botones_layout.addWidget(self.boton_exportar_excel)
        botones_layout.addStretch()
        self.layout.addLayout(botones_layout)

        self.setLayout(self.layout)

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
