from PyQt6.QtWidgets import QPushButton, QSizePolicy
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize, Qt
from core.ui_components import COLOR_BOTON_FONDO, COLOR_BOTON_TEXTO, COLOR_BOTON_BORDE, COLOR_BOTON_FONDO_HOVER, COLOR_BOTON_FONDO_PRESSED

class SidebarButton(QPushButton):
    def __init__(self, icon=None, text=""):
        super().__init__()
        if icon is not None:
            self.setIcon(icon)
        self.setText(text)
        self.setIconSize(QSize(24, 24))
        self.setStyleSheet("""
            QPushButton#sidebarButton {
                background-color: transparent;
                color: #333333;
                text-align: left;
                padding-left: 12px;
                padding-right: 12px;
                border: none;
                font-size: 14px;
            }
            QPushButton#sidebarButton:hover {
                background-color: #E0E7FF;
            }
            QPushButton#sidebarButton:pressed {
                background-color: #C7D2FE;
            }
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)