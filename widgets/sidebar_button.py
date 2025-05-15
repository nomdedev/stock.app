from PyQt6.QtWidgets import QPushButton, QSizePolicy
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize, Qt
from core.ui_components import COLOR_BOTON_FONDO, COLOR_BOTON_TEXTO, COLOR_BOTON_BORDE, COLOR_BOTON_FONDO_HOVER, COLOR_BOTON_FONDO_PRESSED

class SidebarButton(QPushButton):
    def __init__(self, texto: str, icono_path: str, parent=None):
        super().__init__(texto, parent)
        self.selected = False
        self.setIcon(QIcon(icono_path))
        self.setIconSize(QSize(20, 20))
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(40)
        self.setStyleSheet(self._get_style())
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.setCheckable(False)

    def setSelected(self, selected: bool):
        self.selected = selected
        self.setStyleSheet(self._get_style())

    def isSelected(self):
        return self.selected

    def _get_style(self):
        if self.selected:
            return (
                f"QPushButton {{"
                f"background-color: {COLOR_BOTON_FONDO};"
                f"color: {COLOR_BOTON_TEXTO};"
                f"font-weight: bold;"
                f"border-radius: 8px;"
                f"border: 1.5px solid {COLOR_BOTON_BORDE};"
                f"padding: 0 12px;"
                f"text-align: left;"
                f"}}"
                f"QPushButton:hover {{background-color: {COLOR_BOTON_FONDO_HOVER};}}"
            )
        else:
            return (
                f"QPushButton {{"
                f"background-color: {COLOR_BOTON_FONDO};"
                f"color: {COLOR_BOTON_TEXTO};"
                f"border-radius: 8px;"
                f"border: 1.5px solid {COLOR_BOTON_BORDE};"
                f"padding: 0 12px;"
                f"text-align: left;"
                f"}}"
                f"QPushButton:hover {{background-color: {COLOR_BOTON_FONDO_HOVER};}}"
            )
