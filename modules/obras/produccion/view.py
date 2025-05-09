from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QFormLayout, QTableWidget, QScrollArea, QFrame, QHBoxLayout, QSizePolicy, QGraphicsDropShadowEffect
from PyQt6.QtGui import QIcon, QColor
from PyQt6.QtCore import Qt, QSize
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class ProduccionView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()

        # Cargar el stylesheet visual moderno para Producción
        try:
            with open("styles/inventario_styles.qss", "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"No se pudo cargar inventario_styles.qss: {e}")

        self.label_titulo = QLabel("Gestión de Producción")
        self.label_titulo.setStyleSheet("font-size: 10px; font-weight: bold; margin-bottom: 10px;")
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
        self.tabla_aberturas.setStyleSheet("border: 1px solid #e5e7eb; border-radius: 8px;")
        self.tabla_aberturas.horizontalHeader().setStyleSheet("")
        self.layout.addWidget(self.tabla_aberturas)

        # Tabla de etapas de fabricación (para detalles y finalizar etapa)
        self.tabla_etapas = QTableWidget()
        self.tabla_etapas.setColumnCount(5)
        self.tabla_etapas.setHorizontalHeaderLabels(["ID", "Etapa", "Estado", "Fecha Inicio", "Fecha Fin"])
        self.tabla_etapas.setStyleSheet("border: 1px solid #e5e7eb; border-radius: 8px;")
        self.tabla_etapas.horizontalHeader().setStyleSheet("")
        self.layout.addWidget(self.tabla_etapas)

        # Botones principales como iconos (ahora como atributos de instancia)
        botones_layout = QHBoxLayout()
        self.boton_agregar = QPushButton()
        self.boton_ver_detalles = QPushButton()
        self.boton_finalizar_etapa = QPushButton()
        botones = [
            (self.boton_agregar, "plus_icon.svg", "Agregar etapa"),
            (self.boton_ver_detalles, "search_icon.svg", "Ver detalles de abertura"),
            (self.boton_finalizar_etapa, "refresh_icon.svg", "Finalizar etapa"),
        ]
        for boton, icono, tooltip in botones:
            boton.setIcon(QIcon(f"img/{icono}"))
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

        # Botón principal de acción estándar (para compatibilidad con el controlador)
        self.boton_accion = QPushButton()
        self.boton_accion.setIcon(QIcon("utils/produccion.svg"))
        self.boton_accion.setToolTip("Agregar etapa")
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
