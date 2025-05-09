from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTabWidget, QHBoxLayout, QPushButton, QGraphicsDropShadowEffect
from PyQt6.QtGui import QIcon, QColor
from PyQt6.QtCore import QSize

class MantenimientoView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Cargar el stylesheet visual moderno para Mantenimiento
        try:
            with open("styles/inventario_styles.qss", "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"No se pudo cargar inventario_styles.qss: {e}")

        self.label_titulo = QLabel("Gestión de Mantenimiento")
        self.label_titulo.setStyleSheet("font-size: 10px; font-weight: bold; margin-bottom: 10px;")
        self.layout.addWidget(self.label_titulo)

        # Botones principales como iconos
        botones_layout = QHBoxLayout()
        self.boton_agregar = QPushButton()
        self.boton_agregar.setIcon(QIcon("img/plus_icon.svg"))
        self.boton_agregar.setIconSize(QSize(24, 24))
        self.boton_agregar.setToolTip("Agregar mantenimiento")
        self.boton_agregar.setText("")
        self.boton_agregar.setFixedSize(48, 48)
        self.boton_agregar.setStyleSheet("")
        self.boton_historial = QPushButton()
        self.boton_historial.setIcon(QIcon("img/search_icon.svg"))
        self.boton_historial.setIconSize(QSize(24, 24))
        self.boton_historial.setToolTip("Ver historial")
        self.boton_historial.setText("")
        self.boton_historial.setFixedSize(48, 48)
        self.boton_historial.setStyleSheet("")
        botones_layout.addWidget(self.boton_agregar)
        botones_layout.addWidget(self.boton_historial)
        botones_layout.addStretch()
        self.layout.addLayout(botones_layout)

        # Botón principal de acción estándar (para compatibilidad con el controlador)
        self.boton_accion = QPushButton()
        self.boton_accion.setIcon(QIcon("utils/mantenimiento.svg"))
        self.boton_accion.setToolTip("Agregar mantenimiento")
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

        # Crear un widget de pestañas
        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)

        # Pestaña 1: Ficha técnica
        self.tab_ficha_tecnica = QWidget()
        self.tab_ficha_tecnica_layout = QVBoxLayout()
        self.tab_ficha_tecnica.setLayout(self.tab_ficha_tecnica_layout)
        self.tab_ficha_tecnica_layout.addWidget(QLabel("Contenido de la ficha técnica"))
        self.tab_widget.addTab(self.tab_ficha_tecnica, "Ficha Técnica")

        # Pestaña 2: Historial de mantenimientos
        self.tab_historial = QWidget()
        self.tab_historial_layout = QVBoxLayout()
        self.tab_historial.setLayout(self.tab_historial_layout)
        self.tab_historial_layout.addWidget(QLabel("Contenido del historial de mantenimientos"))
        self.tab_widget.addTab(self.tab_historial, "Historial")

        # Pestaña 3: Registro de mantenimiento
        self.tab_registro = QWidget()
        self.tab_registro_layout = QVBoxLayout()
        self.tab_registro.setLayout(self.tab_registro_layout)
        self.tab_registro_layout.addWidget(QLabel("Contenido del registro de mantenimiento"))
        self.tab_widget.addTab(self.tab_registro, "Registro")

        # Pestaña 4: Mantenimientos recurrentes
        self.tab_recurrentes = QWidget()
        self.tab_recurrentes_layout = QVBoxLayout()
        self.tab_recurrentes.setLayout(self.tab_recurrentes_layout)
        self.tab_recurrentes_layout.addWidget(QLabel("Contenido de mantenimientos recurrentes"))
        self.tab_widget.addTab(self.tab_recurrentes, "Recurrentes")

        # Pestaña 5: Historial general
        self.tab_general = QWidget()
        self.tab_general_layout = QVBoxLayout()
        self.tab_general.setLayout(self.tab_general_layout)
        self.tab_general_layout.addWidget(QLabel("Contenido del historial general"))
        self.tab_widget.addTab(self.tab_general, "General")
