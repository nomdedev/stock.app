from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QFormLayout, QTableWidget, QTabWidget, QCalendarWidget, QPushButton, QHBoxLayout, QComboBox
from PyQt6.QtCore import Qt
from core.ui_components import CustomButton
from modules.obras.produccion.view import ProduccionView  # Importar ProduccionView desde el módulo correcto

class ObrasView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()

        self.label = QLabel("Gestión de Obras")
        self.label.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 20px;")
        self.layout.addWidget(self.label)

        # Botones estilizados en una fila
        botones_layout = QHBoxLayout()
        botones_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Centrar los botones

        self.boton_agregar = QPushButton("Agregar Obra")
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

        self.boton_ver_detalles = QPushButton("Ver Detalles de Obra")
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

        self.boton_ver_cronograma = QPushButton("Ver Cronograma")
        self.boton_ver_cronograma.setFixedHeight(30)
        self.boton_ver_cronograma.setFixedWidth(150)
        self.boton_ver_cronograma.setStyleSheet("""
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
        botones_layout.addWidget(self.boton_ver_cronograma)

        self.boton_asignar_herrajes = QPushButton("Asignar Herrajes")
        self.boton_asignar_herrajes.setFixedHeight(30)
        self.boton_asignar_herrajes.setFixedWidth(150)
        self.boton_asignar_herrajes.setStyleSheet("""
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
        botones_layout.addWidget(self.boton_asignar_herrajes)

        self.boton_finalizar = QPushButton("Finalizar Obra")
        self.boton_finalizar.setFixedHeight(30)
        self.boton_finalizar.setFixedWidth(150)
        self.boton_finalizar.setStyleSheet("""
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
        botones_layout.addWidget(self.boton_finalizar)

        self.boton_exportar_excel = QPushButton("Exportar Excel")
        self.boton_exportar_excel.setFixedHeight(30)
        self.boton_exportar_excel.setFixedWidth(150)
        self.boton_exportar_excel.setStyleSheet("""
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
        botones_layout.addWidget(self.boton_exportar_excel)

        self.boton_exportar_pdf = QPushButton("Exportar PDF")
        self.boton_exportar_pdf.setFixedHeight(30)
        self.boton_exportar_pdf.setFixedWidth(150)
        self.boton_exportar_pdf.setStyleSheet("""
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
        botones_layout.addWidget(self.boton_exportar_pdf)

        self.layout.addLayout(botones_layout)  # Agregar el layout de botones al layout principal

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

        self.setLayout(self.layout)
