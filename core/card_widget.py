from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGraphicsDropShadowEffect
from PyQt6.QtGui import QFont, QIcon, QColor
from PyQt6.QtCore import Qt

class CardWidget(QWidget):
    def __init__(self, title: str, content: str, parent=None):
        super().__init__(parent)
        # Establecer tamaño sugerido y padding
        self.setFixedSize(300, 160)
        self.setStyleSheet("background-color: white; border-radius: 12px; padding: 20px;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # Los márgenes externos se asignarán en el layout contenedor
        self.title_label = QLabel(title)
        # Fuente Segoe UI 16px bold
        self.title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self.content_label = QLabel(content)
        # Fuente Segoe UI 13px
        self.content_label.setFont(QFont("Segoe UI", 13))
        layout.addWidget(self.title_label)
        layout.addWidget(self.content_label)
        # Aplicar sombra sutil según parámetros solicitados
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 40))
        self.setGraphicsEffect(shadow)

class TarjetaMetrica(QWidget):
    def __init__(self, icon_path: str, value: str, description: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: white; border-radius: 8px; padding: 10px;")
        layout = QHBoxLayout(self)
        self.icon_label = QLabel()
        self.icon_label.setPixmap(QIcon(icon_path).pixmap(32, 32))
        text_layout = QVBoxLayout()
        self.value_label = QLabel(value)
        self.value_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.desc_label = QLabel(description)
        self.desc_label.setFont(QFont("Arial", 10))
        text_layout.addWidget(self.value_label)
        text_layout.addWidget(self.desc_label)
        layout.addWidget(self.icon_label)
        layout.addLayout(text_layout)
        # Aplicar sombra sutil
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(0, 0, 0, 50))
        self.setGraphicsEffect(shadow)

class EstadoLabel(QLabel):
    def __init__(self, online: bool = True, parent=None):
        super().__init__(parent)
        # Establecer objeto de nombre para QSS
        self.setObjectName("estadoOnline" if online else "estadoOffline")
        # Establecer tamaño fijo de altura 28px, ancho automático y centrado
        self.setFixedHeight(28)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Aplicar estilo base vía QSS
        base_style = """
            QLabel {
                border-radius: 6px;
                padding-left: 6px;
                padding-right: 6px;
                font-family: 'Segoe UI';
                font-size: 14px;
            }
        """
        if online:
            extra = "background-color: #dcfce7; color: #065f46;"
        else:
            extra = "background-color: #fee2e2; color: #991b1b;"
        self.setStyleSheet(base_style + extra)
