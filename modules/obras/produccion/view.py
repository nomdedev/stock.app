from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QFormLayout, QTableWidget, QScrollArea, QFrame, QHBoxLayout, QSizePolicy, QGraphicsDropShadowEffect
from PyQt6.QtGui import QIcon, QColor
from PyQt6.QtCore import Qt, QSize
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import json

class ProduccionView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)

        # Cargar el stylesheet visual moderno para Producción según el tema activo
        try:
            with open("themes/config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
            tema = config.get("tema", "claro")
            archivo_qss = f"themes/{tema}.qss"
            with open(archivo_qss, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"No se pudo cargar el archivo de estilos: {e}")

        self.label_titulo = QLabel("Gestión de Producción")
        self.layout.addWidget(self.label_titulo)

        self.label = self.label_titulo  # Para compatibilidad con controladores
        self.buscar_input = None  # No hay campo de búsqueda en esta vista
        self.id_item_input = None  # No hay campo de ID explícito en esta vista

        # Formulario de entrada
        self.form_layout = QFormLayout()
        self.abertura_input = QLineEdit()
        self.etapa_input = QLineEdit()
        self.estado_input = QLineEdit()
        self.form_layout.addRow("Abertura:", self.abertura_input)
        self.form_layout.addRow("Etapa:", self.etapa_input)
        self.form_layout.addRow("Estado:", self.estado_input)
        self.layout.addLayout(self.form_layout)

        # Tabla de aberturas
        self.tabla_aberturas = QTableWidget()
        self.tabla_aberturas.setColumnCount(5)
        self.tabla_aberturas.setHorizontalHeaderLabels(["ID", "Código", "Tipo", "Estado", "Fecha Inicio"])
        self.layout.addWidget(self.tabla_aberturas)

        # Tabla de etapas de fabricación (para detalles y finalizar etapa)
        self.tabla_etapas = QTableWidget()
        self.tabla_etapas.setColumnCount(5)
        self.tabla_etapas.setHorizontalHeaderLabels(["ID", "Etapa", "Estado", "Fecha Inicio", "Fecha Fin"])
        self.layout.addWidget(self.tabla_etapas)

        # Botón principal de acción (Agregar)
        botones_layout = QHBoxLayout()
        self.boton_agregar = QPushButton()
        self.boton_agregar.setIcon(QIcon("img/add-etapa.svg"))
        self.boton_agregar.setIconSize(QSize(24, 24))
        self.boton_agregar.setToolTip("Agregar producción")
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

        # Botón Ver Detalles
        self.boton_ver_detalles = QPushButton()
        self.boton_ver_detalles.setIcon(QIcon("img/viewdetails.svg"))
        self.boton_ver_detalles.setIconSize(QSize(24, 24))
        self.boton_ver_detalles.setToolTip("Ver detalles de la abertura seleccionada")
        self.boton_ver_detalles.setText("")
        self.boton_ver_detalles.setFixedSize(48, 48)
        self.boton_ver_detalles.setStyleSheet("")
        sombra_detalles = QGraphicsDropShadowEffect()
        sombra_detalles.setBlurRadius(15)
        sombra_detalles.setXOffset(0)
        sombra_detalles.setYOffset(4)
        sombra_detalles.setColor(QColor(0, 0, 0, 50))
        self.boton_ver_detalles.setGraphicsEffect(sombra_detalles)
        botones_layout.addWidget(self.boton_ver_detalles)

        # Botón Finalizar Etapa
        self.boton_finalizar_etapa = QPushButton()
        self.boton_finalizar_etapa.setIcon(QIcon("img/finish-check.svg"))
        self.boton_finalizar_etapa.setIconSize(QSize(24, 24))
        self.boton_finalizar_etapa.setToolTip("Finalizar etapa seleccionada")
        self.boton_finalizar_etapa.setText("")
        self.boton_finalizar_etapa.setFixedSize(48, 48)
        self.boton_finalizar_etapa.setStyleSheet("")
        sombra_finalizar = QGraphicsDropShadowEffect()
        sombra_finalizar.setBlurRadius(15)
        sombra_finalizar.setXOffset(0)
        sombra_finalizar.setYOffset(4)
        sombra_finalizar.setColor(QColor(0, 0, 0, 50))
        self.boton_finalizar_etapa.setGraphicsEffect(sombra_finalizar)
        botones_layout.addWidget(self.boton_finalizar_etapa)

        botones_layout.addStretch()
        self.layout.addLayout(botones_layout)

        self.setLayout(self.layout)

    def agregar_grafico(self, datos):
        figura = Figure()
        canvas = FigureCanvas(figura)
        ax = figura.add_subplot(111)
        ax.bar([d[0] for d in datos], [d[1] for d in datos])
        ax.set_title("Eficiencia por Etapa")
        self.layout.addWidget(canvas)

    def inicializar_kanban(self):
        self.kanban_scroll = QScrollArea()
        self.kanban_scroll.setWidgetResizable(True)
        self.kanban_frame = QFrame()
        self.kanban_layout = QHBoxLayout(self.kanban_frame)

        # Columnas del Kanban
        self.columnas = {}
        etapas = ["Corte", "Soldadura", "Armado", "Burletes", "Vidrio"]
        for etapa in etapas:
            columna = QVBoxLayout()
            columna_label = QLabel(etapa)
            columna_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            columna.addWidget(columna_label)
            self.columnas[etapa] = columna

            columna_widget = QWidget()
            columna_widget.setLayout(columna)
            self.kanban_layout.addWidget(columna_widget)

        self.kanban_scroll.setWidget(self.kanban_frame)
        self.layout.addWidget(self.kanban_scroll)

    def agregar_tarjeta_kanban(self, etapa, tarjeta_texto):
        if etapa in self.columnas:
            tarjeta = QLabel(tarjeta_texto)
            tarjeta.setStyleSheet("background-color: lightblue; padding: 5px; margin: 5px; border: 1px solid black;")
            self.columnas[etapa].addWidget(tarjeta)

class Produccion(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.label = QLabel("Vista de Producción")
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
