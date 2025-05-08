from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QFormLayout, QComboBox, QCheckBox, QPushButton, QSizePolicy, QTabWidget, QHBoxLayout
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize
from themes.theme_manager import aplicar_tema, guardar_preferencia_tema, cargar_preferencia_tema

class ConfiguracionView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)

        try:
            # Switch para cambiar el tema
            self.switch_tema = QCheckBox("Tema Oscuro")
            
            # Cargar preferencia inicial del tema
            tema_inicial = cargar_preferencia_tema()
            self.switch_tema.setChecked(tema_inicial == "dark")
            aplicar_tema(tema_inicial)

            self.switch_tema.setStyleSheet("""
                QCheckBox::indicator {
                    width: 50px;
                    height: 25px;
                }
                QCheckBox::indicator:unchecked {
                    image: url(assets/switch_off.png);
                }
                QCheckBox::indicator:checked {
                    image: url(assets/switch_on.png);
                }
            """)
            self.layout.addWidget(self.switch_tema)

            # Barra de botones principales como iconos
            botones_layout = QHBoxLayout()
            botones = [
                QPushButton(),  # Guardar configuración
                QPushButton(),  # Restaurar valores
            ]
            iconos = [
                ("plus_icon.svg", "Guardar configuración"),
                ("refresh_icon.svg", "Restaurar valores predeterminados"),
            ]
            for boton, (icono, tooltip) in zip(botones, iconos):
                boton.setIcon(QIcon(f"img/{icono}"))
                boton.setIconSize(QSize(32, 32))
                boton.setToolTip(tooltip)
                boton.setText("")
                boton.setFixedSize(48, 48)
                boton.setStyleSheet("""
                    QPushButton {
                        background-color: #2563eb;
                        border-radius: 12px;
                        border: none;
                    }
                    QPushButton:hover {
                        background-color: #1e40af;
                    }
                    QPushButton:pressed {
                        background-color: #1e3a8a;
                    }
                """)
                botones_layout.addWidget(boton)
            self.layout.addLayout(botones_layout)

            # Conectar el interruptor al cambio de tema
            self.switch_tema.stateChanged.connect(self.cambiar_tema)

            # Crear pestañas
            self.tabs = QTabWidget()
            self.general_tab = QWidget()
            self.database_tab = QWidget()

            # Configuración general
            self.general_layout = QFormLayout()
            self.debug_mode_checkbox = QCheckBox("Modo Depuración")
            self.file_storage_input = QLineEdit()
            self.language_input = QLineEdit()
            self.timezone_input = QLineEdit()
            self.notifications_checkbox = QCheckBox("Notificaciones")
            self.general_layout.addRow("Modo Depuración:", self.debug_mode_checkbox)
            self.general_layout.addRow("Ruta de Archivos:", self.file_storage_input)
            self.general_layout.addRow("Idioma Predeterminado:", self.language_input)
            self.general_layout.addRow("Zona Horaria:", self.timezone_input)
            self.general_layout.addRow("Notificaciones:", self.notifications_checkbox)
            self.general_tab.setLayout(self.general_layout)

            # Configuración de base de datos
            self.database_layout = QFormLayout()
            self.server_input = QLineEdit()
            self.username_input = QLineEdit()
            self.password_input = QLineEdit()
            self.port_input = QLineEdit()
            self.default_db_input = QLineEdit()
            self.timeout_input = QLineEdit()
            self.database_layout.addRow("Servidor:", self.server_input)
            self.database_layout.addRow("Usuario:", self.username_input)
            self.database_layout.addRow("Contraseña:", self.password_input)
            self.database_layout.addRow("Puerto:", self.port_input)
            self.database_layout.addRow("Base de Datos Predeterminada:", self.default_db_input)
            self.database_layout.addRow("Tiempo de Espera:", self.timeout_input)
            self.database_tab.setLayout(self.database_layout)

            # Agregar pestañas al widget
            self.tabs.addTab(self.general_tab, "General")
            self.tabs.addTab(self.database_tab, "Base de Datos")
            self.layout.addWidget(self.tabs)

            # Botón para guardar cambios
            self.save_button = QPushButton("Guardar Cambios")
            self.layout.addWidget(self.save_button)

            # Botón para activar modo offline
            self.boton_activar_offline = QPushButton("Activar Modo Offline")
            self.boton_activar_offline.setObjectName("boton_activar_offline")
            self.boton_activar_offline.setStyleSheet("""
                QPushButton {
                    background-color: #5e81ac;
                    border-radius: 8px;
                    padding: 6px 12px;
                    color: white;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #81a1c1;
                }
            """)
            self.layout.addWidget(self.boton_activar_offline)

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
