from PyQt6.QtWidgets import QPushButton, QSizePolicy
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize, Qt
from core.ui_components import COLOR_BOTON_FONDO, COLOR_BOTON_TEXTO, COLOR_BOTON_BORDE, COLOR_BOTON_FONDO_HOVER, COLOR_BOTON_FONDO_PRESSED

class SidebarButton(QPushButton):
    def __init__(self, texto: str, icono_path: str, parent=None):
        super().__init__(texto, parent)
        self.selected = False
        self.setIcon(QIcon(icono_path))
        self.setIconSize(QSize(20, 20))  # Forzar icono 20x20
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(40)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)  # Accesibilidad: permite foco por tabulación
        self.setToolTip(texto)  # Accesibilidad: tooltip claro por defecto
        self.setStyleSheet(self._get_style())
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.setCheckable(False)
        # EXCEPCIÓN: Si se requiere otro color/fuente, justificar aquí y en docs/estandares_visuales.md

    def _get_style(self):
        base_style = f"""
            QPushButton {{
                background-color: {COLOR_BOTON_FONDO};
                color: {COLOR_BOTON_TEXTO};
                font-size: 12px;
                border-radius: 8px;
                border: 1.5px solid {COLOR_BOTON_BORDE};
                padding: 0 12px;
                text-align: left;
            }}
            QPushButton:focus {{
                border: 2px solid #3B82F6; outline: none; box-shadow: 0 0 0 2px #3DE6B1;
            }}
            QPushButton:hover {{
                background-color: {COLOR_BOTON_FONDO_HOVER};
            }}
        """
        if self.selected:
            return base_style + "QPushButton {font-weight: bold;}"
        else:
            return base_style

    def set_activo(self, activo):
        """Actualizar el estado activo del botón."""
        self.selected = activo
        self.setStyleSheet(self._get_style())