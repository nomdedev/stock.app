from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QHBoxLayout, QGraphicsDropShadowEffect
from PyQt6.QtGui import QIcon, QColor
from PyQt6.QtCore import QSize
import json

class NotificacionesView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)

        self.label_titulo = QLabel("Gestión de Notificaciones")
        self.layout.addWidget(self.label_titulo)

        # Cargar el stylesheet visual moderno para Notificaciones según el tema activo
        try:
            with open("themes/config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
            tema = config.get("tema", "claro")
            archivo_qss = f"themes/{tema}.qss"
            with open(archivo_qss, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"No se pudo cargar el archivo de estilos: {e}")

        # Botón principal de acción (Marcar como leído)
        botones_layout = QHBoxLayout()
        self.boton_marcar_leido = QPushButton()
        self.boton_marcar_leido.setIcon(QIcon("img/check_icon.svg"))
        self.boton_marcar_leido.setIconSize(QSize(24, 24))
        self.boton_marcar_leido.setToolTip("Marcar como leído")
        self.boton_marcar_leido.setText("")
        self.boton_marcar_leido.setFixedSize(48, 48)
        self.boton_marcar_leido.setStyleSheet("")
        sombra = QGraphicsDropShadowEffect()
        sombra.setBlurRadius(15)
        sombra.setXOffset(0)
        sombra.setYOffset(4)
        sombra.setColor(QColor(0, 0, 0, 50))
        self.boton_marcar_leido.setGraphicsEffect(sombra)
        botones_layout.addWidget(self.boton_marcar_leido)
        botones_layout.addStretch()
        self.layout.addLayout(botones_layout)

        # Tabla de notificaciones (placeholder)
        self.tabla_notificaciones = QTableWidget()
        self.layout.addWidget(self.tabla_notificaciones)

        self.setLayout(self.layout)
