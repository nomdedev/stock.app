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
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)  # Accesibilidad: permite foco por tabulación
        self.setToolTip(texto)  # Accesibilidad: tooltip claro por defecto
        self.setStyleSheet(self._get_style())
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.setCheckable(False)
        # EXCEPCIÓN: Si se requiere otro color/fuente, justificar aquí y en docs/estandares_visuales.md

    def setSelected(self, selected: bool):
        self.selected = selected
        self.setStyleSheet(self._get_style())

    def isSelected(self):
        return self.selected

    def _get_style(self):
        base_style = (
            f"QPushButton {{"
            f"background-color: {COLOR_BOTON_FONDO};"
            f"color: {COLOR_BOTON_TEXTO};"
            f"font-size: 12px;"
            f"border-radius: 8px;"
            f"border: 1.5px solid {COLOR_BOTON_BORDE};"
            f"padding: 0 12px;"
            f"text-align: left;"
            f"}}"
            f"QPushButton:focus {{"
            f"border: 2px solid #3B82F6; outline: none;"
            f"}}"
            f"QPushButton:hover {{background-color: {COLOR_BOTON_FONDO_HOVER};}}"
        )
        if self.selected:
            return base_style + f"QPushButton {{font-weight: bold;}}"
        else:
            return base_style
