from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import QSize
import os

# Color crema global para botones
COLOR_BOTON_FONDO = "#F5F5DC"  # Crema
COLOR_BOTON_FONDO_HOVER = "#f3f4f6"  # Crema más claro
COLOR_BOTON_FONDO_PRESSED = "#e0e7ef"  # Crema sutil
COLOR_BOTON_TEXTO = "#1e293b"  # Azul gris oscuro
COLOR_BOTON_BORDE = "#e0e7ef"  # Borde sutil

class CustomButton(QPushButton):
    def __init__(self, text, parent=None, style=None):
        super().__init__(text, parent)
        self.setStyleSheet(self.default_style())

    def default_style(self):
        return f"""
            QPushButton {{
                background-color: {COLOR_BOTON_FONDO};
                color: {COLOR_BOTON_TEXTO};
                font-size: 12px;
                font-weight: bold;
                border-radius: 8px;
                border: 1.5px solid {COLOR_BOTON_BORDE};
                padding: 4px 8px;
            }}
            QPushButton:hover {{
                background-color: {COLOR_BOTON_FONDO_HOVER};
                color: {COLOR_BOTON_TEXTO};
            }}
            QPushButton:pressed {{
                background-color: {COLOR_BOTON_FONDO_PRESSED};
                color: {COLOR_BOTON_TEXTO};
            }}
        """

def estilizar_boton_icono(boton: QPushButton, tam_icono: int = 20, tam_boton: int = 32):
    """
    Aplica tamaño de ícono y botón uniforme a un QPushButton para toda la app.
    Args:
        boton: QPushButton a estilizar.
        tam_icono: tamaño del ícono (por defecto 20).
        tam_boton: tamaño del botón (por defecto 32).
    NOTA: El setStyleSheet de este helper puede causar advertencias o bloqueos si el QSS es incompatible con PyQt6.
    Para depuración, comentar la línea de setStyleSheet si aparecen errores de parseo QSS.
    """
    boton.setIconSize(QSize(tam_icono, tam_icono))
    boton.setFixedSize(tam_boton, tam_boton)
    # Fondo crema global, igual para todos los botones
    # boton.setStyleSheet(
    #     f"""
    #     QPushButton {{
    #         background-color: {COLOR_BOTON_FONDO};
    #         color: {COLOR_BOTON_TEXTO};
    #         border-radius: 8px;
    #         padding: 0px;
    #         border: 1.5px solid {COLOR_BOTON_BORDE};
    #         font-weight: bold;
    #     }}
    #     QPushButton:hover {{
    #         background-color: {COLOR_BOTON_FONDO_HOVER};
    #         color: {COLOR_BOTON_TEXTO};
    #     }}
    #     QPushButton:pressed {{
    #         background-color: {COLOR_BOTON_FONDO_PRESSED};
    #         color: {COLOR_BOTON_TEXTO};
    #     }}
    #     """
    # )

def aplicar_qss_global_y_tema(widget, qss_global_path="style_moderno.qss", qss_tema_path=None):
    """
    Aplica el QSS global y, opcionalmente, un QSS de tema a un widget.
    El QSS global debe contener los estilos base de la app.
    El QSS de tema (oscuro, claro, etc.) puede sobreescribir detalles.
    """
    estilos = ""
    if qss_global_path and os.path.exists(qss_global_path):
        with open(qss_global_path, "r", encoding="utf-8") as f:
            estilos += f.read() + "\n"
    if qss_tema_path and os.path.exists(qss_tema_path):
        with open(qss_tema_path, "r", encoding="utf-8") as f:
            estilos += f.read() + "\n"
    if estilos:
        widget.setStyleSheet(estilos)