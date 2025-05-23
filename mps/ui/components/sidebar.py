from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import QSize, pyqtSignal, Qt
from PyQt6.QtGui import QIcon
import os

# --- ESTÁNDAR VISUAL Y DE INTERACCIÓN DEL SIDEBAR ---
# 1. Fondo: blanco puro (#fff) en todo el sidebar.
# 2. Botones:
#    - Fondo: crema (#F5F5DC) en estado normal y activo.
#    - Borde: 1.5px sólido #e0e7ef en normal y hover, 2px #e0e7ef en activo.
#    - Borde izquierdo: 3px sólido #2563eb solo en el botón activo.
#    - Radio de borde: 8px.
#    - Padding: 4px vertical, 10px horizontal.
#    - Texto: #1e293b, tamaño 12px, peso 500, alineado a la izquierda si hay texto.
#    - Hover: fondo #f3f4f6, borde igual o apenas más oscuro, nunca azul eléctrico.
#    - Activo: fondo igual, texto #2563eb solo si se requiere destacar, nunca saturado.
#    - Iconos: SVG/PNG, tamaño 20x20, alineados a la izquierda, padding mínimo 8px respecto al texto.
#    - No usar colores saturados ni efectos de sombra.
# 3. Estado Online/Offline:
#    - Online: fondo #dcfce7, texto #065f46, radio 8px, padding 0 10px.
#    - Offline: fondo #fee2e2, texto #991b1b, radio 8px, padding 0 10px.
# 4. Espaciado:
#    - Entre botones: 8px vertical.
#    - Márgenes internos: 10px laterales, 20px arriba, 10px abajo.
# 5. Accesibilidad:
#    - Contraste alto entre texto y fondo.
#    - Tamaño de fuente nunca menor a 12px.
#    - Iconos descriptivos y visibles.
#    - Feedback visual inmediato al hacer hover o seleccionar.
# 6. Interacción:
#    - El botón activo se resalta solo con borde y color de texto, sin cambiar el fondo.
#    - No usar animaciones ni transiciones llamativas.
#    - El sidebar puede expandirse para mostrar nombres de módulos, manteniendo el mismo estándar visual.
# 7. Código:
#    - Todos los estilos deben estar centralizados en el setStyleSheet del Sidebar.
#    - No hardcodear colores fuera de este archivo salvo helpers globales.
#    - Documentar cualquier excepción a estos estándares.
# --- FIN ESTÁNDAR VISUAL Y DE INTERACCIÓN DEL SIDEBAR ---

class Sidebar(QWidget):
    """
    Sidebar modular y dinámica para navegación de módulos.
    - Soporta íconos SVG, nombres, expansión y feedback de estado.
    - Usar: Sidebar(icons_path, sections, parent=None, mostrar_nombres=False)
    - Migrada desde widgets/sidebar.py para uso global.
    """
    pageChanged = pyqtSignal(int)  # Señal para cambiar página del stackedWidget

    def __init__(self, icons_path, sections, parent=None, mostrar_nombres=False):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 20, 10, 10)
        layout.setSpacing(8)
        self._expanded = False
        self._sections = sections
        self._buttons = []
        self._mostrar_nombres = mostrar_nombres
        self._icons_path = icons_path
        self._layout = layout
        self.current_index = None

        # Fondo blanco para el modo claro
        self.setStyleSheet(f"""
            QWidget {{
                background-color: white;
            }}
            QPushButton#botonMenu {{
                background-color: #F5F5DC;
                color: #1e293b;
                border-radius: 8px;
                padding: 4px 10px 4px 26px; /* padding izquierdo extra para icono + texto */
                font-size: 12px;
                font-weight: 500;
                text-align: left;
                border: 1.5px solid #e0e7ef;
                border-left: 3px solid transparent;
                min-height: 32px;
                min-width: 120px;
                max-width: 160px;
                outline: none;
            }}
            QPushButton#botonMenu:hover, QPushButton#botonMenu:focus {{
                background-color: #f3f4f6;
                border: 1.5px solid #e0e7ef;
                border-left: 3px solid #e0e7ef;
                outline: 2px solid #2563eb; /* foco accesible */
            }}
            QPushButton#botonMenuActivo {{
                background-color: #F5F5DC;
                color: #2563eb;
                border-radius: 8px;
                border: 2px solid #e0e7ef;
                border-left: 3px solid #2563eb;
                font-weight: bold;
                text-align: left;
                outline: 2px solid #2563eb;
            }}
        """)

        # Estado Online/Offline
        self.estado_label = QLabel("Online")
        self.estado_label.setObjectName("estadoOnline")
        self.estado_label.setFixedHeight(28)
        self.estado_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.estado_label.setStyleSheet("""
            QLabel#estadoOnline {
                background-color: #dcfce7;
                color: #065f46;
                font-family: 'Segoe UI';
                font-size: 12px;
                font-weight: bold;
                border-radius: 8px;
                padding: 0 10px;
            }
            QLabel#estadoOffline {
                background-color: #fee2e2;
                color: #991b1b;
                font-family: 'Segoe UI';
                font-size: 12px;
                font-weight: bold;
                border-radius: 8px;
            }
        """)
        self._layout.addWidget(self.estado_label)

        self._create_buttons()

    def _create_buttons(self):
        # Limpiar botones existentes
        for btn in getattr(self, '_buttons', []):
            self._layout.removeWidget(btn)
            btn.deleteLater()
        self._buttons = []
        for index, section in enumerate(self._sections):
            if isinstance(section, tuple):
                section_name = section[0]
                icon_file = section[1] if len(section) > 1 else None
            else:
                section_name = section
                icon_file = None
            button = QPushButton()
            # Marcar el botón activo con el objectName especial
            if hasattr(self, 'current_index') and index == self.current_index:
                button.setObjectName("botonMenuActivo")
            else:
                button.setObjectName("botonMenu")
            button.setFixedHeight(40)
            if self._expanded:
                button.setFixedWidth(180)
            else:
                button.setFixedSize(180 if self._mostrar_nombres else 44, 40)
            icon_path = icon_file or os.path.join(self._icons_path, f"{section_name.lower()}.svg")
            if not os.path.exists(icon_path):
                icon_path = os.path.join('img', f"{section_name.lower()}.svg")
            if os.path.exists(icon_path):
                button.setIcon(QIcon(icon_path))
                button.setIconSize(QSize(20, 20))
            if self._mostrar_nombres or self._expanded:
                button.setText(section_name)
                # Padding izquierdo extra para icono + texto, alineación izquierda
                button.setStyleSheet("text-align: left; padding-left: 26px;")
            button.clicked.connect(lambda _, idx=index: self._on_button_clicked(idx))
            self._layout.addWidget(button)
            self._buttons.append(button)

    def _on_button_clicked(self, idx):
        self.current_index = idx
        self._create_buttons()
        self.pageChanged.emit(idx)

    def set_expanded(self, expanded: bool):
        if self._expanded != expanded:
            self._expanded = expanded
            self._create_buttons()

    @property
    def sections(self):
        return self._sections

    def set_sections(self, sections):
        self._sections = sections
        self._create_buttons()
