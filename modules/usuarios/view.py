from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QHBoxLayout, QGraphicsDropShadowEffect, QTabWidget, QComboBox
from PyQt6.QtGui import QIcon, QColor
from PyQt6.QtCore import QSize
import json

class UsuariosView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)

        # Cargar el stylesheet visual moderno para Usuarios según el tema activo
        try:
            with open("themes/config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
            tema = config.get("tema", "claro")
            archivo_qss = f"themes/{tema}.qss"
            with open(archivo_qss, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"No se pudo cargar el archivo de estilos: {e}")

        # Tabs principales
        self.tabs = QTabWidget()
        self.tab_usuarios = QWidget()
        self.tab_permisos = QWidget()
        self.tabs.addTab(self.tab_usuarios, "Usuarios")
        self.tabs.addTab(self.tab_permisos, "Permisos de módulos")
        self.layout.addWidget(self.tabs)

        # --- Tab Usuarios ---
        tab_usuarios_layout = QVBoxLayout(self.tab_usuarios)
        botones_layout = QHBoxLayout()
        self.boton_agregar = QPushButton()
        self.boton_agregar.setIcon(QIcon("img/agregar-user.svg"))
        self.boton_agregar.setIconSize(QSize(24, 24))
        self.boton_agregar.setToolTip("Agregar usuario")
        self.boton_agregar.setText("")
        self.boton_agregar.setFixedSize(48, 48)
        sombra = QGraphicsDropShadowEffect()
        sombra.setBlurRadius(15)
        sombra.setXOffset(0)
        sombra.setYOffset(4)
        sombra.setColor(QColor(0, 0, 0, 50))
        self.boton_agregar.setGraphicsEffect(sombra)
        botones_layout.addWidget(self.boton_agregar)
        botones_layout.addStretch()
        tab_usuarios_layout.addLayout(botones_layout)
        self.tabla_usuarios = QTableWidget()
        tab_usuarios_layout.addWidget(self.tabla_usuarios)

        # --- Tab Permisos (solo admin) ---
        tab_permisos_layout = QVBoxLayout(self.tab_permisos)
        self.label_permisos = QLabel("Asignar módulos permitidos a usuarios normales:")
        tab_permisos_layout.addWidget(self.label_permisos)
        self.combo_usuario = QComboBox()
        tab_permisos_layout.addWidget(self.combo_usuario)
        self.tabla_permisos_modulos = QTableWidget()
        tab_permisos_layout.addWidget(self.tabla_permisos_modulos)
        self.boton_guardar_permisos = QPushButton("Guardar permisos")
        tab_permisos_layout.addWidget(self.boton_guardar_permisos)

        self.setLayout(self.layout)

    def mostrar_tab_permisos(self, visible):
        # Muestra u oculta la pestaña de permisos según el rol
        idx = self.tabs.indexOf(self.tab_permisos)
        if visible and idx == -1:
            self.tabs.addTab(self.tab_permisos, "Permisos de módulos")
        elif not visible and idx != -1:
            self.tabs.removeTab(idx)

class Usuarios(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.label_titulo = QLabel("Vista de Usuarios")
        self.layout.addWidget(self.label_titulo)
        self.setLayout(self.layout)
