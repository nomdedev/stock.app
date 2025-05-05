from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTableWidget, QSizePolicy
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

        # Botón "Filtrar"
        self.boton_filtrar = QPushButton("Filtrar")  # Definir el botón
        self.boton_filtrar.setFixedSize(100, 30)
        self.boton_filtrar.setStyleSheet("""
            QPushButton {
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #f0f0f0;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        botones_layout.addWidget(self.boton_filtrar, alignment=Qt.AlignmentFlag.AlignLeft)

        # Botón "Exportar"
        self.boton_exportar = QPushButton("Exportar")
        self.boton_exportar.setFixedSize(150, 30)
        self.boton_exportar.setStyleSheet("""
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
        botones_layout.addWidget(self.boton_exportar)

        # Agregar el layout de botones al layout principal
        self.layout.addLayout(botones_layout)

        # Tabla para auditorías
        self.tabla_auditorias = QTableWidget()
        self.layout.addWidget(self.tabla_auditorias)

        # Tabla para errores
        self.tabla_errores = QTableWidget()
        self.layout.addWidget(self.tabla_errores)

        # Etiqueta para mensajes
        self.label = QLabel("")
        self.layout.addWidget(self.label)

class Auditoria(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.label = QLabel("Vista de Auditoría")
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
