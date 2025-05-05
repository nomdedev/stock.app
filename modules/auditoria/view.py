from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QTableWidget, QSizePolicy
from PyQt6.QtCore import Qt

class AuditoriaView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)

        # Crear el botón "Acción"
        self.boton_accion = QPushButton("Ejecutar Acción")
        self.boton_accion.setObjectName("boton_accion")
        self.boton_accion.setStyleSheet("""
            QPushButton {
                background-color: #5e81ac;
                border-radius: 8px;
                padding: 6px 12px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #81a1c1;
            }
        """)
        self.layout.addWidget(self.boton_accion)

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
