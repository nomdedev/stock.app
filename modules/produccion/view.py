from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QFormLayout, QTableWidget, QScrollArea, QFrame, QHBoxLayout, QSizePolicy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtCore import Qt

class ProduccionView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()

        self.label = QLabel("Gestión de Producción")
        self.label.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 20px;")
        self.layout.addWidget(self.label)

        # Formulario de entrada
        self.form_layout = QFormLayout()
        self.abertura_input = QLineEdit()
        self.etapa_input = QLineEdit()
        self.estado_input = QLineEdit()
        self.form_layout.addRow("Abertura:", self.abertura_input)
        self.form_layout.addRow("Etapa:", self.etapa_input)
        self.form_layout.addRow("Estado:", self.estado_input)
        self.layout.addLayout(self.form_layout)

        # Botones estilizados en una fila
        botones_layout = QHBoxLayout()
        botones_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Centrar los botones

        self.boton_agregar = QPushButton("Agregar Etapa")
        self.boton_agregar.setFixedHeight(30)
        self.boton_agregar.setFixedWidth(150)
        self.boton_agregar.setStyleSheet("""
            QPushButton {
                background-color: #2563eb; /* Azul */
                color: white; /* Texto blanco */
                padding: 5px;
                border-radius: 6px; /* Bordes redondeados */
                font-size: 12px; /* Tamaño de letra */
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1e40af; /* Azul más oscuro */
            }
            QPushButton:pressed {
                background-color: #1e3a8a; /* Azul aún más oscuro */
            }
        """)
        botones_layout.addWidget(self.boton_agregar)

        self.boton_ver_detalles = QPushButton("Ver Detalles de Abertura")
        self.boton_ver_detalles.setFixedHeight(30)
        self.boton_ver_detalles.setFixedWidth(150)
        self.boton_ver_detalles.setStyleSheet("""
            QPushButton {
                background-color: #2563eb; /* Azul */
                color: white; /* Texto blanco */
                padding: 5px;
                border-radius: 6px; /* Bordes redondeados */
                font-size: 12px; /* Tamaño de letra */
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

        self.boton_finalizar_etapa = QPushButton("Finalizar Etapa")
        self.boton_finalizar_etapa.setFixedHeight(30)
        self.boton_finalizar_etapa.setFixedWidth(150)
        self.boton_finalizar_etapa.setStyleSheet("""
            QPushButton {
                background-color: #2563eb; /* Azul */
                color: white; /* Texto blanco */
                padding: 5px;
                border-radius: 6px; /* Bordes redondeados */
                font-size: 12px; /* Tamaño de letra */
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1e40af; /* Azul más oscuro */
            }
            QPushButton:pressed {
                background-color: #1e3a8a; /* Azul aún más oscuro */
            }
        """)
        botones_layout.addWidget(self.boton_finalizar_etapa)

        self.layout.addLayout(botones_layout)  # Agregar el layout de botones al layout principal

        # Tabla de aberturas
        self.tabla_aberturas = QTableWidget()
        self.tabla_aberturas.setColumnCount(5)
        self.tabla_aberturas.setHorizontalHeaderLabels(["ID", "Código", "Tipo", "Estado", "Fecha Inicio"])
        self.tabla_aberturas.setStyleSheet("border: 1px solid #e5e7eb; border-radius: 8px;")
        self.tabla_aberturas.horizontalHeader().setStyleSheet("")
        self.layout.addWidget(self.tabla_aberturas)

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
