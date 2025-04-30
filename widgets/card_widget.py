from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QLabel
from PyQt6.QtGui import QFont, QGraphicsDropShadowEffect, QColor

class CardWidget(QGroupBox):
    def __init__(self, title: str, value: str, parent=None):
        super().__init__(parent)
        self.setFixedSize(300, 160)
        self.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border-radius: 12px;
                padding: 20px;
                margin: 10px;
            }
        """)
        layout = QVBoxLayout(self)
        # Título
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(title_label)
        # Valor
        value_label = QLabel(value)
        value_label.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        layout.addWidget(value_label)
        # Sombra
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setOffset(0, 3)
        shadow.setColor(QColor(0, 0, 0, 40))
        self.setGraphicsEffect(shadow)
