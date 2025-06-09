from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFrame, QSizePolicy, QLabel, QHBoxLayout, QPushButton
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QIcon
from components.sidebar_button import SidebarButton
from utils.icon_loader import get_icon

class Sidebar(QWidget):
    estado_cambiado = pyqtSignal(bool)  # True=online, False=offline
    pageChanged = pyqtSignal(int)  # Nueva señal para cambiar de página
    def __init__(self, sections, mostrar_nombres=False, online=True, modo_oscuro=False, widget_tema_target=None):
        super().__init__()
        self._widget_tema_target = widget_tema_target  # Widget donde se aplicará el QSS
        self.setObjectName("sidebar")
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)

        # --- INDICADOR DE ESTADO ONLINE/OFFLINE (solo círculo, sin texto) ---
        estado_layout = QHBoxLayout()
        estado_layout.setContentsMargins(0, 0, 0, 0)
        estado_layout.setSpacing(0)
        self.estado_label = QLabel()
        self.estado_label.setFixedSize(14, 14)
        self.estado_label.setObjectName("estadoOnline" if online else "estadoOffline")
        self._set_estado_online(online)
        estado_layout.addStretch()
        estado_layout.addWidget(self.estado_label)
        layout.addLayout(estado_layout)
        layout.addSpacing(8)

        # --- BLOQUE 1: módulos principales ---
        self._sidebar_buttons = []
        for idx, (title, icon) in enumerate(sections):
            btn = SidebarButton(icon=icon, text=title if mostrar_nombres else "")
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            btn.setFixedHeight(40)
            btn.setIconSize(QSize(24, 24))
            btn.setObjectName("sidebarButton")
            btn.clicked.connect(lambda checked, ix=idx: self._on_sidebar_button_clicked(ix))
            layout.addWidget(btn)
            self._sidebar_buttons.append(btn)

        layout.addStretch()

        # --- SEPARADOR VISUAL ---
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #DDDDDD;")
        layout.addSpacing(16)
        layout.addWidget(separator)
        layout.addSpacing(16)

        # --- BLOQUE 2: Configuración, Logs, Ayuda ---
        # Solo agregar extras si hay módulos principales
        if self._sidebar_buttons:
            extras = ["Configuración", "Logs", "Ayuda"]
            titulos_existentes = [btn.text() for btn in self._sidebar_buttons]
            iconos_secciones = {title: icon for (title, icon) in sections}
            for extra_nombre in extras:
                # Solo agregar si NO está ya en las secciones principales
                if extra_nombre not in titulos_existentes:
                    icon_extra = iconos_secciones.get(extra_nombre, get_icon(extra_nombre.lower()))
                    btn_extra = SidebarButton(icon=icon_extra, text=extra_nombre)
                    btn_extra.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                    btn_extra.setFixedHeight(40)
                    btn_extra.setIconSize(QSize(24, 24))
                    btn_extra.setObjectName("sidebarButton")
                    layout.addWidget(btn_extra)
                    self._sidebar_buttons.append(btn_extra)

        layout.addSpacing(12)

        # --- SWITCH DE TEMA ANIMADO ---
        switch_layout = QHBoxLayout()
        switch_layout.setContentsMargins(0, 0, 0, 0)
        switch_layout.setSpacing(0)
        self.switch_container = QWidget()
        self.switch_container.setFixedSize(56, 28)
        self.switch_container.setObjectName("sidebarThemeSwitchContainer")
        self.btn_tema = QPushButton(self.switch_container)
        self.btn_tema.setFixedSize(28, 28)
        self.btn_tema.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_tema.setObjectName("sidebarThemeSwitch")
        self._modo_oscuro = modo_oscuro
        self._animando = False
        self._set_icono_tema()
        # Posición inicial
        self.btn_tema.move(27 if self._modo_oscuro else 3, 0)
        self.btn_tema.clicked.connect(self._toggle_tema)
        switch_layout.addStretch()
        switch_layout.addWidget(self.switch_container)
        switch_layout.addStretch()
        layout.addLayout(switch_layout)
        layout.addSpacing(8)
        self.setLayout(layout)

        # Refuerzo de accesibilidad: todos los QLabel hijos reciben accessibleDescription y accessibleName si no lo tienen
        self._reforzar_accesibilidad_labels()

    def _reforzar_accesibilidad_labels(self):
        for widget in self.findChildren(QLabel):
            if not widget.accessibleDescription():
                widget.setAccessibleDescription("Label informativo o decorativo en Sidebar")
            if not widget.accessibleName():
                widget.setAccessibleName("Label de Sidebar")

    def set_estado_online(self, online: bool):
        self._set_estado_online(online)
        self.estado_cambiado.emit(online)

    def _set_estado_online(self, online: bool):
        if online:
            self.estado_label.setStyleSheet("background:#22c55e; border-radius:7px;")
            self.estado_label.setObjectName("estadoOnline")
            self.estado_label.setToolTip("Conectado a la base de datos")
        else:
            self.estado_label.setStyleSheet("background:#ef4444; border-radius:7px;")
            self.estado_label.setObjectName("estadoOffline")
            self.estado_label.setToolTip("Sin conexión a la base de datos")

    def _on_sidebar_button_clicked(self, idx):
        # Emitir señal para que MainWindow cambie el stack
        if hasattr(self, 'pageChanged'):
            self.pageChanged.emit(idx)

    def _set_icono_tema(self):
        icon_tema = get_icon("moon") if self._modo_oscuro else get_icon("sun_custom")
        self.btn_tema.setIcon(icon_tema)
        self.btn_tema.setIconSize(QSize(18, 18))

    def _toggle_tema(self):
        if self._animando:
            return
        self._modo_oscuro = not self._modo_oscuro
        self._animando = True
        from PyQt6.QtCore import QPropertyAnimation, QPoint
        start_pos = self.btn_tema.pos()
        end_pos = QPoint(27, 0) if self._modo_oscuro else QPoint(3, 0)
        anim = QPropertyAnimation(self.btn_tema, b"pos")
        anim.setDuration(180)
        anim.setStartValue(start_pos)
        anim.setEndValue(end_pos)
        def on_anim_finished():
            self._set_icono_tema()
            self._animando = False
            # Cambiar el tema real de la app usando QApplication.instance()
            from utils.theme_manager import set_theme, guardar_modo_tema
            from PyQt6.QtWidgets import QApplication
            app = QApplication.instance()
            if app:
                set_theme(app, "dark" if self._modo_oscuro else "light")
                guardar_modo_tema("dark" if self._modo_oscuro else "light")
        anim.finished.connect(on_anim_finished)
        anim.start()
