from PyQt6.QtWidgets import QPushButton, QSizePolicy
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize

class SidebarButton(QPushButton):
    def __init__(self, texto, ruta_icono, activo=False, parent=None):
        super().__init__(texto, parent)

        # Configurar ícono
        self.setIcon(QIcon(ruta_icono))
        self.setIconSize(QSize(24, 24))

        # Configurar tamaño y política
        self.setFixedHeight(40)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Configurar estilos
        self.setStyleSheet(self._get_stylesheet(activo))

        # Tooltip si no hay texto
        if not texto:
            self.setToolTip(texto)

    def _get_stylesheet(self, activo):
        if activo:
            return """
                QPushButton {
                    background-color: #21262D; /* Fondo activo */
                    color: #1F6FEB; /* Texto activo */
                    font-weight: bold;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #30363D; /* Hover */
                }
            """
        else:
            return """
                QPushButton {
                    background-color: #0D1117; /* Fondo normal */
                    color: #E6EDF3; /* Texto normal */
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #30363D; /* Hover */
                }
            """

    def set_activo(self, activo):
        """Actualizar el estado activo del botón."""
        self.setStyleSheet(self._get_stylesheet(activo))