from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QFormLayout, QComboBox, QCheckBox, QPushButton, QSizePolicy, QTabWidget, QHBoxLayout, QGraphicsDropShadowEffect, QTableWidget, QTableWidgetItem
from PyQt6.QtGui import QIcon, QColor
from PyQt6.QtCore import QSize, Qt
from themes.theme_manager import aplicar_tema, guardar_preferencia_tema, cargar_preferencia_tema
import json
from core.ui_components import estilizar_boton_icono

class ConfiguracionView(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("configuracionView")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(32, 32, 32, 32)
        self.layout.setSpacing(0)
        # Cargar el stylesheet visual moderno para Configuración según el tema activo
        try:
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

            # Botón principal de acción (Guardar)
            botones_layout = QHBoxLayout()
            self.boton_guardar = QPushButton()
            self.boton_guardar.setIcon(QIcon("img/settings_icon.svg"))
            self.boton_guardar.setIconSize(QSize(24, 24))
            self.boton_guardar.setToolTip("Guardar configuración")
            self.boton_guardar.setText("")
            self.boton_guardar.setFixedSize(48, 48)
            self.boton_guardar.setStyleSheet("")
            sombra = QGraphicsDropShadowEffect()
            sombra.setBlurRadius(15)
            sombra.setXOffset(0)
            sombra.setYOffset(4)
            sombra.setColor(QColor(0, 0, 0, 50))
            self.boton_guardar.setGraphicsEffect(sombra)
            estilizar_boton_icono(self.boton_guardar)
            botones_layout.addWidget(self.boton_guardar)
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
            self.server_input.setPlaceholderText("Ej: 192.168.1.100 o NOMBREPC\\SQLEXPRESS")
            self.server_input.setToolTip("Dirección IP o nombre del servidor SQL Server")
            self.database_layout.addRow(QLabel("Servidor:"), self.server_input)
            self.server_help = QLabel("<span style='color:#64748b;font-size:11px'>IP o nombre de la PC donde está SQL Server</span>")
            self.database_layout.addRow(QLabel(""), self.server_help)

            self.username_input = QLineEdit()
            self.username_input.setPlaceholderText("Ej: sa")
            self.username_input.setToolTip("Usuario de SQL Server")
            self.database_layout.addRow(QLabel("Usuario:"), self.username_input)
            self.username_help = QLabel("<span style='color:#64748b;font-size:11px'>Usuario con permisos en la base de datos</span>")
            self.database_layout.addRow(QLabel(""), self.username_help)

            self.password_input = QLineEdit()
            self.password_input.setPlaceholderText("Contraseña segura")
            self.password_input.setToolTip("Contraseña del usuario de SQL Server")
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.database_layout.addRow(QLabel("Contraseña:"), self.password_input)
            self.password_help = QLabel("<span style='color:#64748b;font-size:11px'>No se mostrará ni almacenará en texto plano</span>")
            self.database_layout.addRow(QLabel(""), self.password_help)

            self.port_input = QLineEdit()
            self.port_input.setPlaceholderText("1433")
            self.port_input.setToolTip("Puerto de SQL Server (por defecto 1433)")
            self.database_layout.addRow(QLabel("Puerto:"), self.port_input)
            self.port_help = QLabel("<span style='color:#64748b;font-size:11px'>Puerto TCP/IP, normalmente 1433</span>")
            self.database_layout.addRow(QLabel(""), self.port_help)

            self.default_db_input = QLineEdit()
            self.default_db_input.setPlaceholderText("Ej: inventario")
            self.default_db_input.setToolTip("Nombre de la base de datos a usar por defecto")
            self.database_layout.addRow(QLabel("Base de Datos Predeterminada:"), self.default_db_input)
            self.db_help = QLabel("<span style='color:#64748b;font-size:11px'>Nombre exacto de la base de datos</span>")
            self.database_layout.addRow(QLabel(""), self.db_help)

            self.timeout_input = QLineEdit()
            self.timeout_input.setPlaceholderText("10")
            self.timeout_input.setToolTip("Tiempo de espera de conexión en segundos")
            self.database_layout.addRow(QLabel("Tiempo de Espera:"), self.timeout_input)
            self.timeout_help = QLabel("<span style='color:#64748b;font-size:11px'>Recomendado: 10 segundos</span>")
            self.database_layout.addRow(QLabel(""), self.timeout_help)

            # --- BOTÓN PROBAR CONEXIÓN ---
            self.boton_probar_conexion = QPushButton("Probar conexión")
            self.boton_probar_conexion.setIcon(QIcon("img/search_icon.svg"))
            self.boton_probar_conexion.setIconSize(QSize(20, 20))
            self.boton_probar_conexion.setFixedHeight(32)
            self.boton_probar_conexion.setStyleSheet("font-size:13px; font-weight:600; border-radius:8px; background:#2563eb; color:white;")
            self.database_layout.addRow(QLabel(""), self.boton_probar_conexion)
            self.resultado_conexion_label = QLabel("")
            self.resultado_conexion_label.setStyleSheet("font-size:12px; font-weight:500; padding:4px 0 0 0;")
            self.database_layout.addRow(QLabel(""), self.resultado_conexion_label)

            self.boton_probar_conexion.clicked.connect(self.probar_conexion_sql)

            # --- VALIDACIÓN VISUAL AL GUARDAR ---
            def resaltar_campos_obligatorios():
                campos = [self.server_input, self.username_input, self.password_input, self.default_db_input]
                for campo in campos:
                    if not campo.text().strip():
                        campo.setStyleSheet("border:2px solid #ef4444; border-radius:6px;")
                    else:
                        campo.setStyleSheet("")
            self.boton_guardar.clicked.connect(resaltar_campos_obligatorios)

            self.database_tab.setLayout(self.database_layout)

            # Agregar pestañas al widget
            self.tabs.addTab(self.general_tab, "General")
            self.tabs.addTab(self.database_tab, "Base de Datos")

            # --- NUEVA PESTAÑA: Importar Inventario/Herrajes desde CSV ---
            self.import_tab = QWidget()
            self.import_layout = QVBoxLayout()
            self.import_tab.setLayout(self.import_layout)

            self.import_label = QLabel("Importar Inventario/Herrajes desde CSV")
            self.import_layout.addWidget(self.import_label)

            self.csv_file_input = QLineEdit()
            self.csv_file_input.setPlaceholderText("Selecciona el archivo CSV...")
            self.import_layout.addWidget(self.csv_file_input)

            self.boton_seleccionar_csv = QPushButton()
            self.boton_seleccionar_csv.setIcon(QIcon("img/excel_icon.svg"))
            self.boton_seleccionar_csv.setIconSize(QSize(24, 24))
            self.boton_seleccionar_csv.setToolTip("Seleccionar archivo CSV")
            self.boton_seleccionar_csv.setText("")
            self.boton_seleccionar_csv.setFixedSize(48, 48)
            self.boton_seleccionar_csv.setStyleSheet("")
            sombra_csv = QGraphicsDropShadowEffect()
            sombra_csv.setBlurRadius(15)
            sombra_csv.setXOffset(0)
            sombra_csv.setYOffset(4)
            sombra_csv.setColor(QColor(0, 0, 0, 50))
            self.boton_seleccionar_csv.setGraphicsEffect(sombra_csv)
            estilizar_boton_icono(self.boton_seleccionar_csv)
            self.import_layout.addWidget(self.boton_seleccionar_csv)

            self.boton_importar_csv = QPushButton()
            self.boton_importar_csv.setIcon(QIcon("img/add-material.svg"))
            self.boton_importar_csv.setIconSize(QSize(24, 24))
            self.boton_importar_csv.setToolTip("Importar y actualizar inventario/herrajes")
            self.boton_importar_csv.setText("")
            self.boton_importar_csv.setFixedSize(48, 48)
            self.boton_importar_csv.setStyleSheet("")
            sombra_import = QGraphicsDropShadowEffect()
            sombra_import.setBlurRadius(15)
            sombra_import.setXOffset(0)
            sombra_import.setYOffset(4)
            sombra_import.setColor(QColor(0, 0, 0, 50))
            self.boton_importar_csv.setGraphicsEffect(sombra_import)
            estilizar_boton_icono(self.boton_importar_csv)
            self.import_layout.addWidget(self.boton_importar_csv)

            self.import_result_label = QLabel("")
            self.import_layout.addWidget(self.import_result_label)

            self.import_layout.addStretch()
            self.tabs.addTab(self.import_tab, "Importar CSV")
            # --- FIN NUEVA PESTAÑA ---

            # --- NUEVA PESTAÑA: Permisos y visibilidad ---
            self.permisos_tab = QWidget()
            self.permisos_layout = QVBoxLayout()
            self.permisos_tab.setLayout(self.permisos_layout)

            self.permisos_label = QLabel("Gestión de permisos y visibilidad de módulos por usuario/rol")
            self.permisos_layout.addWidget(self.permisos_label)

            # Tabla de permisos: usuarios/roles en filas, módulos en columnas, checkboxes por acción
            self.tabla_permisos = QTableWidget()
            self.tabla_permisos.setColumnCount(5)  # Usuario/Rol, Módulo, Ver, Modificar, Aprobar
            self.tabla_permisos.setHorizontalHeaderLabels([
                "Usuario/Rol", "Módulo", "Ver", "Modificar", "Aprobar"
            ])
            self.tabla_permisos.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            self.permisos_layout.addWidget(self.tabla_permisos)

            # Botón para guardar cambios de permisos
            self.boton_guardar_permisos = QPushButton()
            self.boton_guardar_permisos.setIcon(QIcon("img/settings_icon.svg"))
            self.boton_guardar_permisos.setIconSize(QSize(24, 24))
            self.boton_guardar_permisos.setToolTip("Guardar cambios de permisos")
            self.boton_guardar_permisos.setText("")
            self.boton_guardar_permisos.setFixedSize(48, 48)
            sombra_perm = QGraphicsDropShadowEffect()
            sombra_perm.setBlurRadius(15)
            sombra_perm.setXOffset(0)
            sombra_perm.setYOffset(4)
            sombra_perm.setColor(QColor(0, 0, 0, 50))
            self.boton_guardar_permisos.setGraphicsEffect(sombra_perm)
            estilizar_boton_icono(self.boton_guardar_permisos)
            self.permisos_layout.addWidget(self.boton_guardar_permisos)

            self.permisos_result_label = QLabel("")
            self.permisos_layout.addWidget(self.permisos_result_label)

            self.permisos_layout.addStretch()
            self.tabs.addTab(self.permisos_tab, "Permisos y visibilidad")
            # --- FIN NUEVA PESTAÑA ---

            # --- TUTORIAL DE CONEXIÓN ---
            self.tutorial_tab = QWidget()
            self.tutorial_layout = QVBoxLayout()
            self.tutorial_tab.setLayout(self.tutorial_layout)
            tutorial_text = (
                "<h2>¿Cómo conectarse al servidor de base de datos?</h2>"
                "<ul>"
                "<li><b>1. Encontrar la IP del servidor:</b> En la PC donde está SQL Server, abre una terminal y ejecuta <code>ipconfig</code>. Copia la dirección IPv4 (ej: 192.168.1.100).</li>"
                "<li><b>2. Configura los campos:</b>"
                "<ul>"
                "<li><b>Servidor:</b> Pon la IP encontrada o el nombre de la PC (ej: 192.168.1.100 o NOMBREPC\\SQLEXPRESS).</li>"
                "<li><b>Usuario:</b> El usuario de SQL Server (ej: sa).</li>"
                "<li><b>Contraseña:</b> La contraseña de ese usuario.</li>"
                "<li><b>Puerto:</b> 1433 (por defecto).</li>"
                "<li><b>Base de Datos:</b> Elige la base a la que te quieres conectar (ej: inventario).</li>"
                "</ul>"
                "<li><b>3. Prueba la conexión:</b> Usa el botón de 'Probar conexión'. Si falla, revisa firewall, usuario, contraseña y que SQL Server acepte conexiones remotas.</li>"
                "<li><b>4. Guarda los cambios:</b> Si la conexión es exitosa, guarda la configuración. Se usará en todos los inicios y computadoras.</li>"
                "</ul>"
            )
            self.tutorial_label = QLabel()
            self.tutorial_label.setTextFormat(Qt.TextFormat.RichText)
            self.tutorial_label.setText(tutorial_text)
            self.tutorial_label.setWordWrap(True)
            self.tutorial_layout.addWidget(self.tutorial_label)
            self.tutorial_layout.addStretch()
            self.tabs.addTab(self.tutorial_tab, "Tutorial conexión")
            # --- FIN TUTORIAL ---

            self.layout.addWidget(self.tabs)
        except Exception as e:
            print(f"Error al inicializar ConfiguracionView: {e}")

    def cambiar_tema(self, estado):
        """Cambia el tema de la aplicación y guarda la preferencia."""
        nuevo_tema = "dark" if estado == 2 else "light"
        aplicar_tema(nuevo_tema)
        guardar_preferencia_tema(nuevo_tema)

    def probar_conexion_sql(self):
        """Prueba la conexión a SQL Server con los datos ingresados en la pestaña Base de Datos."""
        import pyodbc
        driver = "ODBC Driver 17 for SQL Server"
        server = self.server_input.text().strip()
        user = self.username_input.text().strip()
        pwd = self.password_input.text().strip()
        db = self.default_db_input.text().strip()
        port = self.port_input.text().strip() or "1433"
        timeout = int(self.timeout_input.text().strip() or "10")
        connection_string = (
            f"DRIVER={{{driver}}};"
            f"SERVER={server},{port};"
            f"DATABASE={db};"
            f"UID={user};"
            f"PWD={pwd};"
            f"TrustServerCertificate=yes;"
        )
        try:
            with pyodbc.connect(connection_string, timeout=timeout) as conn:
                self.resultado_conexion_label.setText("<span style='color:#22c55e'>✅ Conexión exitosa</span>")
        except Exception as e:
            self.resultado_conexion_label.setText(f"<span style='color:#ef4444'>❌ Error: {e}</span>")
