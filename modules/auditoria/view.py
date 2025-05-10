from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QTableWidget, QSizePolicy, QHBoxLayout, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QColor
import json

class AuditoriaView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)

        # Cargar el stylesheet visual moderno para Auditoría según el tema activo
        try:
            with open("themes/config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
            tema = config.get("tema", "claro")
            archivo_qss = f"themes/{tema}.qss"
            with open(archivo_qss, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"No se pudo cargar el archivo de estilos: {e}")

        # Botón principal de acción (Ver logs)
        botones_layout = QHBoxLayout()
        self.boton_ver_logs = QPushButton()
        self.boton_ver_logs.setIcon(QIcon("img/search_icon.svg"))
        self.boton_ver_logs.setIconSize(QSize(24, 24))
        self.boton_ver_logs.setToolTip("Ver logs de auditoría")
        self.boton_ver_logs.setText("")
        self.boton_ver_logs.setFixedSize(48, 48)
        self.boton_ver_logs.setStyleSheet("")
        sombra = QGraphicsDropShadowEffect()
        sombra.setBlurRadius(15)
        sombra.setXOffset(0)
        sombra.setYOffset(4)
        sombra.setColor(QColor(0, 0, 0, 160))
        self.boton_ver_logs.setGraphicsEffect(sombra)
        botones_layout.addWidget(self.boton_ver_logs)
        botones_layout.addStretch()
        self.layout.addLayout(botones_layout)

        # Tabla de logs (placeholder)
        self.tabla_logs = QTableWidget()
        self.layout.addWidget(self.tabla_logs)

        self.setLayout(self.layout)

class Auditoria(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.label_titulo = QLabel("Vista de Auditoría")
        self.layout.addWidget(self.label_titulo)
        self.setLayout(self.layout)
