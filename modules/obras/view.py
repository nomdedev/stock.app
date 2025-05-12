from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTabWidget, QCalendarWidget, QPushButton, QHBoxLayout, QFrame
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont
from themes import theme_manager
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from modules.obras.cronograma.view import CronogramaView
from modules.obras.cronograma.controller import CronogramaController

class ObrasView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 10, 20, 10)  # Reducir margen superior
        self.layout.setSpacing(8)  # Menor separación vertical
        try:
            tema = theme_manager.cargar_preferencia_tema()
            theme_manager.aplicar_tema(tema)
        except Exception as e:
            print(f"No se pudo aplicar el tema global: {e}")
        # Título estilizado
        self.label_titulo = QLabel("Gestión de Obras")
        self.label_titulo.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.label_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.label_titulo)
        # Área de estado
        self.label_estado = QLabel("Estado: Listo")
        self.label_estado.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Sunken)
        self.label_estado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.label_estado)
        # Pestañas: solo Cronograma (Gantt) y Calendario
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        # Pestaña de Cronograma (Gantt visual)
        self.tab_cronograma = QWidget()
        self.tab_cronograma_layout = QVBoxLayout()
        self.tab_cronograma.setLayout(self.tab_cronograma_layout)
        self.tabs.addTab(self.tab_cronograma, "Cronograma")
        # --- INTEGRACIÓN DEL NUEVO GANTT ---
        self.cronograma_view = CronogramaView()
        self.cronograma_controller = CronogramaController(self.cronograma_view)
        # Contenedor horizontal para botones de zoom
        zoom_layout = QHBoxLayout()
        self.boton_zoom_in = QPushButton("+")
        self.boton_zoom_in.setFixedSize(32, 32)
        self.boton_zoom_in.setToolTip("Acercar cronograma")
        self.boton_zoom_out = QPushButton("-")
        self.boton_zoom_out.setFixedSize(32, 32)
        self.boton_zoom_out.setToolTip("Alejar cronograma")
        zoom_layout.addWidget(self.boton_zoom_in)
        zoom_layout.addWidget(self.boton_zoom_out)
        zoom_layout.addStretch()
        self.tab_cronograma_layout.addLayout(zoom_layout)
        self.tab_cronograma_layout.addWidget(self.cronograma_view)
        self.boton_zoom_in.clicked.connect(self.cronograma_view.zoom_in)
        self.boton_zoom_out.clicked.connect(self.cronograma_view.zoom_out)
        # --- Botones de acción debajo del cronograma ---
        botones_layout = QHBoxLayout()
        self.boton_agregar = QPushButton()
        self.boton_agregar.setIcon(QIcon("img/add-etapa.svg"))
        self.boton_agregar.setIconSize(QSize(24, 24))
        self.boton_agregar.setToolTip("Agregar obra")
        self.boton_agregar.setText("")
        self.boton_agregar.setFixedSize(48, 48)
        self.boton_agregar.setStyleSheet("background-color: #f0f0f0; border-radius: 5px;")
        botones_layout.addWidget(self.boton_agregar)
        self.boton_verificar_obra = QPushButton()
        self.boton_verificar_obra.setIcon(QIcon("img/search_icon.svg"))
        self.boton_verificar_obra.setIconSize(QSize(24, 24))
        self.boton_verificar_obra.setToolTip("Verificar obra en SQL")
        self.boton_verificar_obra.setText("")
        self.boton_verificar_obra.setFixedSize(48, 48)
        self.boton_verificar_obra.setStyleSheet("background-color: #f0f0f0; border-radius: 5px;")
        botones_layout.addWidget(self.boton_verificar_obra)
        botones_layout.addStretch()
        self.tab_cronograma_layout.addLayout(botones_layout)
        # Pestaña de Calendario
        self.tab_calendario = QWidget()
        self.tab_calendario_layout = QVBoxLayout()
        self.calendario = QCalendarWidget()
        self.calendario.setGridVisible(True)
        self.tab_calendario_layout.addWidget(self.calendario)
        self.tab_calendario.setLayout(self.tab_calendario_layout)
        self.tabs.addTab(self.tab_calendario, "Calendario")
        self.setLayout(self.layout)

    @property
    def label(self):
        return self.label_estado
