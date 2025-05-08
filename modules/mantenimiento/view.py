from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTabWidget

class MantenimientoView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.label_titulo = QLabel("Gestión de Mantenimiento")
        self.label_titulo.setStyleSheet("font-size: 10px; font-weight: bold; margin-bottom: 10px;")
        self.layout.addWidget(self.label_titulo)

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
