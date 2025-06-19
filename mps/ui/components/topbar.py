from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt

class TopBar(QWidget):
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(8)
        self.label = QLabel(title)
        self.label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.label.setStyleSheet("font-size: 18px; font-weight: 600;")
        layout.addWidget(self.label)
        layout.addStretch()

    def set_title(self, title):
        self.label.setText(title)
