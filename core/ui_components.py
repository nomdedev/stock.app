from PyQt6.QtWidgets import QPushButton, QMessageBox, QWidget
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize, Qt
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
        # El estilo visual se gestiona por QSS de theme global. Solo usar setStyleSheet aquí si se justifica como excepción (ver docs/estandares_visuales.md)
        # self.setStyleSheet(self.default_style())

    def default_style(self):
        # Deprecated: los estilos deben estar en QSS de theme global
        return ""

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
    # Quitar setStyleSheet aquí para evitar advertencias de QSS incompatibles con PyQt6
    # Si se requiere estilo visual, usar QSS global o el método default_style de CustomButton
    # boton.setStyleSheet(...)

def aplicar_qss_global_y_tema(widget, qss_global_path=None, qss_tema_path=None):
    """
    Aplica el QSS global y el QSS de tema (claro/oscuro) al widget.
    Por convención, solo se deben usar los archivos QSS globales: resources/qss/theme_light.qss y resources/qss/theme_dark.qss.
    """
    qss = ""
    if qss_global_path:
        try:
            with open(qss_global_path, encoding="utf-8") as f:
                qss += f.read() + "\n"
        except Exception:
            pass
    if qss_tema_path:
        try:
            with open(qss_tema_path, encoding="utf-8") as f:
                qss += f.read()
        except Exception:
            pass
    if qss:
        widget.setStyleSheet(qss)

class HelpButton(QPushButton):
    """
    Botón de ayuda contextual reutilizable. Al hacer clic, muestra un mensaje o documentación relevante.
    Uso:
        help_btn = HelpButton("Texto de ayuda", parent=self, icon_path="resources/icons/help-circle.svg")
        layout.addWidget(help_btn)
    """
    def __init__(self, help_text, parent=None, icon_path=None, title="Ayuda", tooltip="Ver ayuda contextual"):
        super().__init__(parent)
        self.help_text = help_text
        self.setToolTip(tooltip)
        self.setAccessibleName("Botón de ayuda contextual")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        if icon_path and os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
            self.setIconSize(QSize(22, 22))
        else:
            self.setText("?")
        self.clicked.connect(self.mostrar_ayuda)
        estilizar_boton_icono(self)
        self.title = title

    def mostrar_ayuda(self):
        # Buscar un QWidget válido como parent
        parent = self.parent()
        while parent and not isinstance(parent, QWidget):
            parent = parent.parent() if hasattr(parent, 'parent') else None
        parent_widget = parent if isinstance(parent, QWidget) else None
        QMessageBox.information(parent_widget, self.title, self.help_text)