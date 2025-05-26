from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import QSize, pyqtSignal, Qt
from PyQt6.QtGui import QIcon
import os

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

        # Fondo blanco para el modo claro
        self.setStyleSheet("""
            QWidget {
                background-color: white;
            }
            QPushButton#botonMenu {
                background-color: white;
                color: #1f2937;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: 500;
                text-align: center;
            }
            QPushButton#botonMenu:hover {
                background-color: #f3f4f6;
            }
            QPushButton#botonMenuActivo {
                background-color: #2563eb;
                color: white;
            }
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
            button.setObjectName("botonMenu")
            button.setFixedHeight(40)
            if self._expanded:
                button.setFixedWidth(180)
            else:
                button.setFixedSize(180 if self._mostrar_nombres else 44, 40)
            # Usar SVG de utils si existe
            icon_path = icon_file or os.path.join(self._icons_path, f"{section_name.lower()}.svg")
            if not os.path.exists(icon_path):
                icon_path = os.path.join('img', f"{section_name.lower()}.svg")
            if os.path.exists(icon_path):
                button.setIcon(QIcon(icon_path))
                button.setIconSize(QSize(20, 20))
            if self._mostrar_nombres:
                button.setText(section_name)
                button.setStyleSheet("text-align: left; padding-left: 12px;")
            button.clicked.connect(lambda _, idx=index: self.pageChanged.emit(idx))
            self._layout.addWidget(button)
            self._buttons.append(button)

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
