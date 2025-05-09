from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QFormLayout, QComboBox, QCheckBox, QPushButton, QSizePolicy, QTabWidget, QHBoxLayout
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize
from themes.theme_manager import aplicar_tema, guardar_preferencia_tema, cargar_preferencia_tema

class ConfiguracionView(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("configuracionView")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(32, 32, 32, 32)
        self.layout.setSpacing(0)
        try:
            import json
            with open("themes/config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
            tema = config.get("tema", "claro")
            archivo_qss = f"themes/{tema}.qss"
            with open(archivo_qss, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"No se pudo cargar el archivo de estilos de Configuración según el tema: {e}")
        # Título
        self.label_titulo = QLabel("SETTINGS")
        self.layout.addWidget(self.label_titulo)

        try:
            # Switch para cambiar el tema
            self.switch_tema = QCheckBox("")
            self.switch_tema.setToolTip("Cambiar entre tema claro y oscuro")
            tema_inicial = cargar_preferencia_tema()
            self.switch_tema.setChecked(tema_inicial == "dark")
            aplicar_tema(tema_inicial)
            self.switch_tema.setStyleSheet("""
                QCheckBox::indicator {
                    width: 32px;
                    height: 16px;
                }
                QCheckBox::indicator:unchecked {
                    image: url(assets/switch_off.png);
                }
                QCheckBox::indicator:checked {
                    image: url(assets/switch_on.png);
                }
            """)
            switch_layout = QHBoxLayout()
            switch_layout.addWidget(QLabel("Tema Oscuro"))
            switch_layout.addWidget(self.switch_tema)
            switch_layout.addStretch()
            self.layout.addLayout(switch_layout)

            # Botones principales solo icono
            botones_layout = QHBoxLayout()
            self.boton_guardar = QPushButton()
            self.boton_guardar.setIcon(QIcon("img/plus_icon.svg"))
            self.boton_guardar.setIconSize(QSize(24, 24))
            self.boton_guardar.setToolTip("Guardar configuración")
            self.boton_guardar.setText("")
            self.boton_guardar.setFixedSize(48, 48)
            self.boton_guardar.setStyleSheet("")
            self.boton_restaurar = QPushButton()
            self.boton_restaurar.setIcon(QIcon("img/refresh_icon.svg"))
            self.boton_restaurar.setIconSize(QSize(24, 24))
            self.boton_restaurar.setToolTip("Restaurar valores predeterminados")
            self.boton_restaurar.setText("")
            self.boton_restaurar.setFixedSize(48, 48)
            self.boton_restaurar.setStyleSheet("")
            botones_layout.addWidget(self.boton_guardar)
            botones_layout.addWidget(self.boton_restaurar)
            # Botón para activar modo offline (compacto, solo icono)
            self.boton_activar_offline = QPushButton()
            self.boton_activar_offline.setIcon(QIcon("img/offline_icon.svg"))
            self.boton_activar_offline.setIconSize(QSize(24, 24))
            self.boton_activar_offline.setToolTip("Activar Modo Offline")
            self.boton_activar_offline.setText("")
            self.boton_activar_offline.setFixedSize(48, 48)
            self.boton_activar_offline.setStyleSheet("")
            botones_layout.addWidget(self.boton_activar_offline)
            botones_layout.addStretch()
            self.layout.addLayout(botones_layout)

            # Crear pestañas
            self.tabs = QTabWidget()
            self.general_tab = QWidget()
            self.database_tab = QWidget()

            # Configuración general
            self.general_layout = QFormLayout()
            self.general_layout.setHorizontalSpacing(8)
            self.general_layout.setVerticalSpacing(4)
            self.debug_mode_checkbox = QCheckBox()
            self.file_storage_input = QLineEdit()
            self.language_input = QLineEdit()
            self.timezone_input = QLineEdit()
            self.notifications_checkbox = QCheckBox()
            self.general_layout.addRow(QLabel("Modo Depuración:"), self.debug_mode_checkbox)
            self.general_layout.addRow(QLabel("Ruta de Archivos:"), self.file_storage_input)
            self.general_layout.addRow(QLabel("Idioma Predeterminado:"), self.language_input)
            self.general_layout.addRow(QLabel("Zona Horaria:"), self.timezone_input)
            self.general_layout.addRow(QLabel("Notificaciones:"), self.notifications_checkbox)
            self.general_tab.setLayout(self.general_layout)

            # Configuración de base de datos
            self.database_layout = QFormLayout()
            self.database_layout.setHorizontalSpacing(8)
            self.database_layout.setVerticalSpacing(4)
            self.server_input = QLineEdit()
            self.username_input = QLineEdit()
            self.password_input = QLineEdit()
            self.port_input = QLineEdit()
            self.default_db_input = QLineEdit()
            self.timeout_input = QLineEdit()
            self.database_layout.addRow(QLabel("Servidor:"), self.server_input)
            self.database_layout.addRow(QLabel("Usuario:"), self.username_input)
            self.database_layout.addRow(QLabel("Contraseña:"), self.password_input)
            self.database_layout.addRow(QLabel("Puerto:"), self.port_input)
            self.database_layout.addRow(QLabel("Base de Datos Predeterminada:"), self.default_db_input)
            self.database_layout.addRow(QLabel("Tiempo de Espera:"), self.timeout_input)
            self.database_tab.setLayout(self.database_layout)

            # Agregar pestañas al widget
            self.tabs.addTab(self.general_tab, "General")
            self.tabs.addTab(self.database_tab, "Base de Datos")
            self.layout.addWidget(self.tabs)

            self.setLayout(self.layout)
        except Exception as e:
            print(f"Error al inicializar ConfiguracionView: {e}")

    def cambiar_tema(self, estado):
        """Cambia el tema de la aplicación y guarda la preferencia."""
        nuevo_tema = "dark" if estado == 2 else "light"
        aplicar_tema(nuevo_tema)
        guardar_preferencia_tema(nuevo_tema)

class Configuracion(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.label_titulo = QLabel("Vista de Configuración")
        self.layout.addWidget(self.label_titulo)
        self.setLayout(self.layout)
