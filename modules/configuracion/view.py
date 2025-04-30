from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QFormLayout, QComboBox, QCheckBox, QPushButton, QSizePolicy

class ConfiguracionView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()

        # Título principal
        self.label_titulo = QLabel("Configuración del Sistema")
        self.label_titulo.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 20px;")
        self.layout.addWidget(self.label_titulo)

        # Sección de configuración general
        self.form_layout_general = QFormLayout()
        self.nombre_app_input = QLineEdit()
        self.zona_horaria_input = QComboBox()
        self.zona_horaria_input.addItems(["UTC-12", "UTC-11", "UTC-10", "UTC-9", "UTC-8", "UTC-7", "UTC-6", "UTC-5", "UTC-4", "UTC-3", "UTC-2", "UTC-1", "UTC", "UTC+1", "UTC+2", "UTC+3", "UTC+4", "UTC+5", "UTC+6", "UTC+7", "UTC+8", "UTC+9", "UTC+10", "UTC+11", "UTC+12"])
        self.modo_mantenimiento_checkbox = QCheckBox("Modo Mantenimiento")
        self.modo_color_input = QComboBox()
        self.modo_color_input.addItems(["Claro", "Oscuro"])
        self.idioma_input = QComboBox()
        self.idioma_input.addItems(["es", "en", "fr", "de"])
        self.notificaciones_checkbox = QCheckBox("Mostrar Notificaciones")
        self.tamano_fuente_input = QComboBox()
        self.tamano_fuente_input.addItems(["Pequeño", "Mediano", "Grande"])

        self.form_layout_general.addRow("Nombre de la Aplicación:", self.nombre_app_input)
        self.form_layout_general.addRow("Zona Horaria:", self.zona_horaria_input)
        self.form_layout_general.addRow("", self.modo_mantenimiento_checkbox)
        self.form_layout_general.addRow("Modo de Color:", self.modo_color_input)
        self.form_layout_general.addRow("Idioma Preferido:", self.idioma_input)
        self.form_layout_general.addRow("", self.notificaciones_checkbox)
        self.form_layout_general.addRow("Tamaño de Fuente:", self.tamano_fuente_input)
        self.layout.addLayout(self.form_layout_general)

        # Botón para guardar cambios
        self.boton_guardar_cambios = QPushButton("Guardar Cambios")
        self.boton_guardar_cambios.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.layout.addWidget(self.boton_guardar_cambios)

        # Separador
        self.layout.addWidget(QLabel(""))

        # Sección de configuración de conexión
        self.label_conexion = QLabel("Configuración de Conexión")
        self.label_conexion.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 20px;")
        self.layout.addWidget(self.label_conexion)

        self.form_layout_conexion = QFormLayout()
        self.base_predeterminada_input = QLineEdit()
        self.servidor_input = QLineEdit()
        self.puerto_input = QLineEdit()
        self.form_layout_conexion.addRow("Base Predeterminada:", self.base_predeterminada_input)
        self.form_layout_conexion.addRow("Servidor:", self.servidor_input)
        self.form_layout_conexion.addRow("Puerto:", self.puerto_input)
        self.layout.addLayout(self.form_layout_conexion)

        # Botones de conexión
        self.botones_conexion_layout = QVBoxLayout()
        self.boton_guardar_conexion = QPushButton("Guardar Configuración de Conexión")
        self.boton_guardar_conexion.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.botones_conexion_layout.addWidget(self.boton_guardar_conexion)

        self.boton_activar_offline = QPushButton("Activar Modo Offline")
        self.boton_activar_offline.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.botones_conexion_layout.addWidget(self.boton_activar_offline)

        self.boton_desactivar_offline = QPushButton("Desactivar Modo Offline")
        self.boton_desactivar_offline.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.botones_conexion_layout.addWidget(self.boton_desactivar_offline)

        self.boton_notificaciones = QPushButton("Activar/Desactivar Notificaciones")
        self.boton_notificaciones.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.botones_conexion_layout.addWidget(self.boton_notificaciones)

        self.layout.addLayout(self.botones_conexion_layout)

        self.setLayout(self.layout)

class Configuracion(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.label = QLabel("Vista de Configuración")
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
