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
                    background-color: #FFFFFF; /* Fondo activo blanco */
                    color: #1F6FEB; /* Texto activo */
                    font-weight: bold;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #F0F0F0; /* Hover blanco */
                }
            """
        else:
            return """
                QPushButton {
                    background-color: #FFFFFF; /* Fondo normal blanco */
                    color: #000000; /* Texto normal negro */
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #F0F0F0; /* Hover blanco */
                }
            """

    def set_activo(self, activo):
        """Actualizar el estado activo del botón."""
        self.setStyleSheet(self._get_stylesheet(activo))