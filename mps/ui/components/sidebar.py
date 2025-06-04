from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QFrame, QSizePolicy, QGraphicsDropShadowEffect, QSpacerItem
from PyQt6.QtCore import QSize, pyqtSignal, Qt, QPropertyAnimation, QRect
from PyQt6.QtGui import QIcon, QColor
from PyQt6.QtWidgets import QApplication
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from utils.theme_manager import set_theme, guardar_modo_tema
from components.sidebar_button import SidebarButton

class Sidebar(QFrame):
    """
    Sidebar modular y dinámica para navegación de módulos.
    - Soporta íconos SVG, nombres, expansión y feedback de estado.
    - Usar: Sidebar(icons_path, sections, parent=None, mostrar_nombres=False)
    - Migrada desde widgets/sidebar.py para uso global.
    """
    pageChanged = pyqtSignal(int)  # Señal para cambiar página del stackedWidget

    def __init__(self, icons_path, sections, parent=None, mostrar_nombres=False):
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setFixedWidth(220)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        # Sombra sutil
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(37, 99, 235, 30))
        self.setGraphicsEffect(shadow)
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 32, 0, 32)  # Más aire arriba y abajo
        layout.setSpacing(0)
        self._expanded = False
        self._sections = sections
        self._buttons = []
        self._mostrar_nombres = mostrar_nombres
        self._icons_path = icons_path
        self._layout = layout

        # HEADER: Logo + Estado
        header = QFrame(self)
        header.setObjectName("sidebar-header")
        header.setFixedHeight(80)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(32, 0, 32, 0)
        header_layout.setSpacing(12)
        logo_label = QLabel()
        logo_label.setPixmap(QIcon(os.path.join(os.path.dirname(__file__), '../../../resources/icons/MPS_inicio_sesion.png')).pixmap(44, 44))
        logo_label.setFixedSize(44, 44)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.estado_label = QLabel("Online")
        self.estado_label.setObjectName("estadoOnline")
        self.estado_label.setFixedHeight(32)
        self.estado_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(logo_label, alignment=Qt.AlignmentFlag.AlignLeft)
        header_layout.addStretch(1)
        header_layout.addWidget(self.estado_label, alignment=Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(header)
        layout.addSpacing(18)
        # Eliminado bloque de usuario
        # Separador visual
        sep = QFrame(self)
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFrameShadow(QFrame.Shadow.Plain)
        sep.setStyleSheet("color: #e3e3e3; background: #e3e3e3; min-height: 1px; max-height: 1px;")
        layout.addWidget(sep)
        layout.addSpacing(10)
        # Sección de botones principales
        self.buttons_frame = QFrame(self)
        self.buttons_frame.setObjectName("sidebar-buttons")
        buttons_layout = QVBoxLayout(self.buttons_frame)
        buttons_layout.setContentsMargins(16, 0, 16, 0)
        buttons_layout.setSpacing(0)  # Separación solo por QSS
        self._buttons_layout = buttons_layout
        layout.addWidget(self.buttons_frame)
        self._create_buttons()
        layout.addSpacing(10)
        layout.addStretch(1)

        # Sección de herramientas (Logs, Ayuda)
        tools_frame = QFrame(self)
        tools_frame.setObjectName("sidebar-tools")
        tools_layout = QVBoxLayout(tools_frame)
        tools_layout.setContentsMargins(24, 0, 24, 0)
        tools_layout.setSpacing(18)
        btn_logs = QPushButton("Logs")
        btn_logs.setObjectName("botonMenu")
        btn_logs.setProperty("class", "sidebar-button")
        btn_logs.setIcon(QIcon(os.path.join(self._icons_path, "logs.svg")))
        btn_logs.setIconSize(QSize(24, 24))
        btn_logs.setFixedHeight(36)
        tools_layout.addWidget(btn_logs)
        btn_ayuda = QPushButton("Ayuda")
        btn_ayuda.setObjectName("botonMenu")
        btn_ayuda.setProperty("class", "sidebar-button")
        btn_ayuda.setIcon(QIcon(os.path.join(self._icons_path, "help.svg")))
        btn_ayuda.setIconSize(QSize(24, 24))
        btn_ayuda.setFixedHeight(36)
        tools_layout.addWidget(btn_ayuda)
        layout.addWidget(tools_frame)
        layout.addSpacing(18)

        # Switch de tema
        class ThemeSwitch(QFrame):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setFixedSize(56, 32)
                self.is_dark = False
                self.btn = QPushButton(self)
                self.btn.setCursor(Qt.CursorShape.PointingHandCursor)
                self.btn.setStyleSheet("")
                self.btn.setIcon(QIcon(os.path.join(os.path.dirname(__file__), '../../../resources/icons/sun_custom.svg')))
                self.btn.setIconSize(QSize(22, 22))
                self.btn.setGeometry(3, 3, 26, 26)
                self.btn.clicked.connect(self.toggle_theme)
                self.anim = QPropertyAnimation(self.btn, b"geometry")
                self.anim.setDuration(180)
                self.update_visual()
                # Inicializar según preferencia guardada
                try:
                    from utils.theme_manager import cargar_modo_tema
                    modo = cargar_modo_tema()
                    self.is_dark = (modo == "dark" or modo == "oscuro")
                    self.update_visual(animated=False)
                except Exception:
                    pass
            def toggle_theme(self):
                self.is_dark = not self.is_dark
                self.update_visual(animated=True)
                # Lógica real de cambio de tema en vivo
                app = QApplication.instance()
                if self.is_dark:
                    set_theme(app, "dark")
                    guardar_modo_tema("dark")
                else:
                    set_theme(app, "light")
                    guardar_modo_tema("light")
            def update_visual(self, animated=False):
                if self.is_dark:
                    self.btn.setIcon(QIcon(os.path.join(os.path.dirname(__file__), '../../../resources/icons/moon_custom.svg')))
                    end_rect = QRect(27, 3, 26, 26)
                else:
                    self.btn.setIcon(QIcon(os.path.join(os.path.dirname(__file__), '../../../resources/icons/sun_custom.svg')))
                    end_rect = QRect(3, 3, 26, 26)
                if animated:
                    self.anim.stop()
                    self.anim.setStartValue(self.btn.geometry())
                    self.anim.setEndValue(end_rect)
                    self.anim.start()
                else:
                    self.btn.setGeometry(end_rect)
        theme_switch_layout = QHBoxLayout()
        theme_switch_layout.setContentsMargins(36, 0, 0, 0)
        theme_switch_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.theme_switch = ThemeSwitch()
        theme_switch_layout.addWidget(self.theme_switch)
        theme_switch_widget = QWidget()
        theme_switch_widget.setLayout(theme_switch_layout)
        layout.addWidget(theme_switch_widget)
        layout.addSpacing(18)
        layout.addStretch(2)  # Espaciador expansivo antes del footer

        # Footer
        footer = QFrame(self)
        footer.setObjectName("sidebar-footer")
        footer.setFixedHeight(24)
        layout.addWidget(footer)
        # layout.addStretch(1)  # El footer queda pegado abajo

    def set_estado(self, online=True):
        if online:
            self.estado_label.setObjectName("estadoOnline")
            self.estado_label.setText("Online")
        else:
            self.estado_label.setObjectName("estadoOffline")
            self.estado_label.setText("Offline")

    def _create_buttons(self):
        # Limpiar botones existentes
        for i in reversed(range(self._buttons_layout.count())):
            item = self._buttons_layout.itemAt(i)
            if item is not None:
                widget = item.widget()
                if widget:
                    widget.setParent(None)
        self._buttons = []
        for index, section in enumerate(self._sections):
            if isinstance(section, tuple):
                section_name = section[0]
                icon_file = section[1] if len(section) > 1 else None
            else:
                section_name = section
                icon_file = None
            icon_path = icon_file or os.path.join(self._icons_path, f"{section_name.lower()}.svg")
            if not os.path.exists(icon_path):
                icon_path = os.path.join('resources/icons', f"placeholder.svg")
            button = SidebarButton(section_name, icon_path)
            button.clicked.connect(lambda _, idx=index: self.pageChanged.emit(idx))
            self._buttons_layout.addWidget(button)
            # Espaciador vertical fijo entre botones
            if index < len(self._sections) - 1:
                self._buttons_layout.addItem(QSpacerItem(0, 80, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
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
