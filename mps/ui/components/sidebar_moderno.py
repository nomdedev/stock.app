from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFrame, QSizePolicy, QLabel, QHBoxLayout, QPushButton
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QIcon
from components.sidebar_button import SidebarButton
from utils.icon_loader import get_icon

class Sidebar(QWidget):
    estado_cambiado = pyqtSignal(bool)  # True=online, False=offline
    def __init__(self, sections, mostrar_nombres=False, online=True, modo_oscuro=False):
        super().__init__()
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
        for title, icon in sections:
            btn = SidebarButton(icon=icon, text=title if mostrar_nombres else "")
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            btn.setFixedHeight(40)
            btn.setIconSize(QSize(24, 24))
            btn.setObjectName("sidebarButton")
            layout.addWidget(btn)

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
        nombres_modulos = [title.lower() for title, _ in sections]
        if "configuración".lower() not in nombres_modulos:
            btn_conf = SidebarButton(icon=get_icon("configuracion"), text="Configuración")
            btn_conf.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            btn_conf.setFixedHeight(40)
            btn_conf.setIconSize(QSize(24, 24))
            btn_conf.setObjectName("sidebarButton")
            layout.addWidget(btn_conf)
        if "logs" not in nombres_modulos:
            btn_logs = SidebarButton(icon=get_icon("logs"), text="Logs")
            btn_logs.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            btn_logs.setFixedHeight(40)
            btn_logs.setIconSize(QSize(24, 24))
            btn_logs.setObjectName("sidebarButton")
            layout.addWidget(btn_logs)
        if "ayuda" not in nombres_modulos:
            btn_ayuda = SidebarButton(icon=get_icon("ayuda"), text="Ayuda")
            btn_ayuda.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            btn_ayuda.setFixedHeight(40)
            btn_ayuda.setIconSize(QSize(24, 24))
            btn_ayuda.setObjectName("sidebarButton")
            layout.addWidget(btn_ayuda)

        layout.addSpacing(12)

        # --- SWITCH DE TEMA MINIMALISTA ---
        switch_layout = QHBoxLayout()
        switch_layout.setContentsMargins(0, 0, 0, 0)
        switch_layout.setSpacing(0)
        self.btn_tema = QPushButton()
        self.btn_tema.setFixedSize(28, 28)
        self.btn_tema.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_tema.setObjectName("sidebarThemeSwitch")
        icon_tema = get_icon("moon") if modo_oscuro else get_icon("sun_custom")
        self.btn_tema.setIcon(icon_tema)
        self.btn_tema.setIconSize(QSize(18, 18))
        self.btn_tema.setToolTip("Cambiar modo claro/oscuro")
        switch_layout.addStretch()
        switch_layout.addWidget(self.btn_tema)
        switch_layout.addStretch()
        layout.addLayout(switch_layout)
        layout.addSpacing(8)

        self.setLayout(layout)

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
