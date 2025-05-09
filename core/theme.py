# core/theme.py
from PyQt6.QtWidgets import QGraphicsDropShadowEffect
from PyQt6.QtGui import QColor

# Paleta de colores minimalista y moderna
PRIMARY_COLOR = "#ffffff"  # Blanco puro para fondo
SECONDARY_COLOR = "#f5f5f5"  # Gris claro para secciones
ACCENT_COLOR = "#0078d4"  # Azul moderno para elementos destacados
TEXT_COLOR = "#333333"  # Gris oscuro para texto
BORDER_COLOR = "#e0e0e0"  # Gris claro para bordes
FONT_FAMILY = "Segoe UI, Arial, sans-serif"
BORDER_RADIUS = "8px"

# Estilo global para widgets
GLOBAL_STYLE = f'''
QWidget {{
    background-color: {PRIMARY_COLOR};
    color: {TEXT_COLOR};
    font-family: {FONT_FAMILY};
    border-radius: {BORDER_RADIUS};
}}
QPushButton {{
    background-color: {SECONDARY_COLOR};
    color: {TEXT_COLOR};
    font-family: {FONT_FAMILY};
    font-size: 14px;
    font-weight: 500;
    border-radius: {BORDER_RADIUS};
    border: 1px solid {BORDER_COLOR};
    padding: 8px 16px;
}}
QPushButton:hover {{
    background-color: {ACCENT_COLOR};
    color: #ffffff;
}}
QLineEdit, QComboBox, QTableWidget, QTextEdit {{
    background-color: {SECONDARY_COLOR};
    color: {TEXT_COLOR};
    border-radius: {BORDER_RADIUS};
    border: 1px solid {BORDER_COLOR};
    padding: 6px;
}}
QTableWidget::item:selected {{
    background-color: {ACCENT_COLOR};
    color: #ffffff;
    border-radius: {BORDER_RADIUS};
}}
QHeaderView::section {{
    background-color: {SECONDARY_COLOR};
    color: {TEXT_COLOR};
    font-weight: bold;
    border-radius: {BORDER_RADIUS};
    border: 1px solid {BORDER_COLOR};
    padding: 8px;
}}
QFrame {{
    background-color: {SECONDARY_COLOR};
    border-radius: {BORDER_RADIUS};
    border: 1px solid {BORDER_COLOR};
}}
QLabel {{
    color: {TEXT_COLOR};
    font-size: 14px;
}}
'''

# Function to apply shadow effect globally to QPushButton

def apply_shadow_to_button(button):
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(15)
    shadow.setXOffset(0)
    shadow.setYOffset(4)
    shadow.setColor(QColor(0, 0, 0, 160))
    button.setGraphicsEffect(shadow)

def aplicar_sombra_css():
    """Devuelve un estilo CSS para aplicar sombra a los botones."""
    return """
    QPushButton {
        box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.2);
    }
    """
