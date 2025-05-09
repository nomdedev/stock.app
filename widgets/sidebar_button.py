from PyQt6.QtWidgets import QPushButton, QSizePolicy
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize, Qt

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
                "QPushButton {"
                "background-color: #C0D4EB;"
                "color: #222;"
                "font-weight: bold;"
                "border-radius: 8px;"
                "padding: 0 12px;"
                "text-align: left;"
                "}"
            )
        else:
            return (
                "QPushButton {"
                "background-color: #E4ECF7;"
                "color: #222;"
                "font-weight: normal;"
                "border-radius: 8px;"
                "padding: 0 12px;"
                "text-align: left;"
                "}"
                "QPushButton:hover {"
                "background-color: #D3E0F2;"
                "}"
            )
