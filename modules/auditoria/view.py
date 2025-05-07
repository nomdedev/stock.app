from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QTableWidget, QSizePolicy, QHBoxLayout
from PyQt6.QtCore import Qt

class AuditoriaView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)

        # Crear contenedor para los botones
        botones_layout = QHBoxLayout()
        botones_layout.setSpacing(10)  # Espaciado entre botones
        botones_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Centrar botones

        # Botón "Ver Logs"
        self.boton_ver_logs = self.crear_boton("Ver Logs")
        botones_layout.addWidget(self.boton_ver_logs)

        # Botón "Exportar Logs"
        self.boton_exportar_logs = self.crear_boton("Exportar Logs")
        botones_layout.addWidget(self.boton_exportar_logs)

        # Botón "Filtrar Logs"
        self.boton_filtrar_logs = self.crear_boton("Filtrar Logs")
        botones_layout.addWidget(self.boton_filtrar_logs)

        # Botón "Acción"
        self.boton_accion = QPushButton("Acción")
        self.boton_accion.setFixedSize(150, 30)
        self.boton_accion.setStyleSheet("""
            QPushButton {
                background-color: #2563eb; /* Azul */
                color: white; /* Texto blanco */
                border: none;
                border-radius: 15px; /* Bordes redondeados */
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1e40af; /* Azul más oscuro */
            }
            QPushButton:pressed {
                background-color: #1e3a8a; /* Azul aún más oscuro */
            }
        """)
        botones_layout.addWidget(self.boton_accion)

        # Agregar el layout de botones al layout principal
        self.layout.addLayout(botones_layout)

    def crear_boton(self, texto):
        """Crea un botón estilizado con el texto proporcionado."""
        boton = QPushButton(texto)
        boton.setFixedSize(150, 30)
        boton.setStyleSheet("""
            QPushButton {
                background-color: #2563eb; /* Azul */
                color: white; /* Texto blanco */
                border: none;
                border-radius: 15px; /* Bordes redondeados */
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1e40af; /* Azul más oscuro */
            }
            QPushButton:pressed {
                background-color: #1e3a8a; /* Azul aún más oscuro */
            }
        """)
        return boton

class Auditoria(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.label = QLabel("Vista de Auditoría")
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
