from PyQt6.QtWidgets import QMainWindow, QFileDialog, QTableWidget, QTableWidgetItem, QMessageBox, QLabel, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QTabWidget, QComboBox, QLineEdit, QFormLayout, QCheckBox
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QSize, pyqtSignal
import pandas as pd
from core.config_manager import ConfigManager
from core.ui_components import HelpButton
import os

class ConfiguracionView(QMainWindow):
    theme_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        # Inicialización de layout y feedback global accesible
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)
        # label_feedback inicializado una sola vez y siempre visible (oculto por defecto)
        self.label_feedback = QLabel()
        self.label_feedback.setVisible(False)
        self.label_feedback.setAccessibleDescription("Mensaje de feedback global")
        self.main_layout.addWidget(self.label_feedback)
        self.setup_ui()
        self._cargar_configuracion_conexion()

    def setup_ui(self):
        # --- HEADER VISUAL MODERNO: título y barra de botones alineados ---
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(24)
        self.label_titulo = QLabel("Gestión de Configuración")
        header_layout.addWidget(self.label_titulo, alignment=Qt.AlignmentFlag.AlignVCenter)
        # Botón principal (Agregar configuración)
        self.boton_agregar = QPushButton()
        self.boton_agregar.setIcon(QIcon("resources/icons/add-material.svg"))
        self.boton_agregar.setIconSize(QSize(24, 24))
        self.boton_agregar.setToolTip("Agregar configuración")
        header_layout.addWidget(self.boton_agregar)
        header_layout.addStretch()
        self.main_layout.addLayout(header_layout)

        # QTabWidget principal
        self.tabs = QTabWidget(self)
        # self.tabs.setStyleSheet("QTabWidget::pane { border-radius: 12px; background: #f1f5f9; } QTabBar::tab { min-width: 160px; min-height: 36px; font-size: 14px; font-weight: 600; border-radius: 8px; padding: 8px 24px; margin-right: 8px; } QTabBar::tab:selected { background: #e3f6fd; color: #2563eb; }")

        # --- Pestaña General ---
        self.tab_general = QWidget()
        layout_general = QVBoxLayout(self.tab_general)
        label_general = QLabel("Configuración general del sistema (próximamente)")
        label_general.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_general.addWidget(label_general)
        # Botón activar offline (para test y funcionalidad real)
        self.boton_activar_offline = QPushButton()
        self.boton_activar_offline.setText("Activar modo offline")
        self.boton_activar_offline.setIcon(QIcon("resources/icons/offline_icon.svg"))
        self.boton_activar_offline.setToolTip("Activa el modo offline de la app")
        self.boton_activar_offline.setAccessibleName("Botón activar modo offline")
        self.boton_activar_offline.setObjectName("boton_activar_offline")
        layout_general.addWidget(self.boton_activar_offline)
        # --- Dropdown de tema visual ---
        theme_row = QHBoxLayout()
        theme_label = QLabel("Tema:")
        self.combo_tema = QComboBox()
        self.combo_tema.addItems(["Claro", "Oscuro"])
        self.combo_tema.setCurrentIndex(0)  # Por defecto claro
        self.combo_tema.currentIndexChanged.connect(self._emitir_cambio_tema)
        theme_row.addWidget(theme_label)
        theme_row.addWidget(self.combo_tema)
        theme_row.addStretch()
        layout_general.insertLayout(0, theme_row)
        self.tabs.addTab(self.tab_general, "General")

        # --- Pestaña Conexión ---
        self.tab_conexion = QWidget()
        layout_conexion = QVBoxLayout(self.tab_conexion)
        self.form_conexion = QFormLayout()
        self.input_db_server = QLineEdit()
        self.input_db_username = QLineEdit()
        self.input_db_password = QLineEdit()
        self.input_db_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_db_database = QLineEdit()
        self.input_db_timeout = QLineEdit()
        self.input_db_timeout.setPlaceholderText("5")
        self.checkbox_mostrar_password = QCheckBox("Mostrar contraseña")
        self.checkbox_mostrar_password.toggled.connect(
            lambda checked: self.input_db_password.setEchoMode(QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password)
        )
        self.form_conexion.addRow("Servidor/IP:", self.input_db_server)
        self.form_conexion.addRow("Usuario:", self.input_db_username)
        self.form_conexion.addRow("Contraseña:", self.input_db_password)
        self.form_conexion.addRow("", self.checkbox_mostrar_password)
        self.form_conexion.addRow("Base de datos:", self.input_db_database)
        self.form_conexion.addRow("Timeout (seg):", self.input_db_timeout)
        # --- Botón de ayuda contextual ---
        ayuda_texto = (
            "<b>Gestión de configuraciones críticas</b><br>"
            "Desde aquí puedes ver y editar los datos de conexión a la base de datos.\n<br><br>"
            "<b>Recomendaciones:</b><ul>"
            "<li>Utiliza siempre 'Probar conexión' antes de guardar cambios.</li>"
            "<li>No compartas el archivo .env fuera del entorno seguro.</li>"
            "<li>Consulta la guía completa para pasos detallados y mejores prácticas.</li>"
            "</ul>"
            "<br>Guía completa: <code>docs/buenas_practicas_configuraciones_criticas.md</code>"
        )
        self.boton_ayuda_config = HelpButton(ayuda_texto, parent=self.tab_conexion, icon_path="resources/icons/help-circle.svg", title="Ayuda - Configuración Crítica")
        ayuda_row = QHBoxLayout()
        ayuda_row.addStretch()
        ayuda_row.addWidget(self.boton_ayuda_config)
        layout_conexion.addLayout(self.form_conexion)
        layout_conexion.addLayout(ayuda_row)
        # Botones de acción para conexión
        self.btn_probar_conexion = QPushButton("Probar conexión")
        self.btn_guardar_conexion = QPushButton("Guardar configuración")
        btn_row = QHBoxLayout()
        btn_row.addWidget(self.btn_probar_conexion)
        btn_row.addWidget(self.btn_guardar_conexion)
        layout_conexion.addLayout(btn_row)
        self.label_estado_conexion = QLabel()
        layout_conexion.addWidget(self.label_estado_conexion)
        self.tab_conexion.setLayout(layout_conexion)
        # Eventos
        self.btn_probar_conexion.clicked.connect(self._probar_conexion)
        self.btn_guardar_conexion.clicked.connect(self._guardar_configuracion_conexion)
        # --- Pestaña Permisos ---
        self.tab_permisos = QWidget()
        layout_permisos = QVBoxLayout(self.tab_permisos)
        label_permisos = QLabel("Gestión de permisos de usuario (próximamente)")
        label_permisos.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_permisos.addWidget(label_permisos)
        self.tabs.addTab(self.tab_permisos, "Permisos")

        # --- Pestaña Importar Inventario ---
        self.tab_importar = QWidget()
        layout_importar = QVBoxLayout(self.tab_importar)
        layout_importar.setContentsMargins(0, 0, 0, 0)
        layout_importar.setSpacing(12)
        label_titulo = QLabel("Importar Inventario desde CSV/Excel")
        # label_titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #2563eb;")
        layout_importar.addWidget(label_titulo)
        # Mensaje de ayuda
        self.label_ayuda_import = QLabel("Selecciona un archivo CSV o Excel con los datos de inventario. El sistema detectará y completará automáticamente las columnas requeridas. Puedes importar archivos incompletos: los campos faltantes se rellenarán por defecto.")
        self.label_ayuda_import.setWordWrap(True)
        # self.label_ayuda_import.setStyleSheet("font-size: 13px; color: #64748b; background: #f1f5f9; border-radius: 8px; padding: 8px 12px;")
        layout_importar.addWidget(self.label_ayuda_import)
        file_row = QHBoxLayout()
        self.csv_file_input = QLabel("Ningún archivo seleccionado")
        # self.csv_file_input.setStyleSheet("background: #e3f6fd; border-radius: 8px; padding: 8px 16px; color: #2563eb;")
        self.boton_seleccionar_csv = QPushButton()
        self.boton_seleccionar_csv.setIcon(QIcon("resources/icons/excel_icon.svg"))
        self.boton_seleccionar_csv.setToolTip("Seleccionar archivo CSV/Excel")
        self.boton_seleccionar_csv.setFixedSize(36, 36)
        # self.boton_seleccionar_csv.setStyleSheet("border-radius: 8px; background: #e3f6fd;")
        file_row.addWidget(self.csv_file_input)
        file_row.addWidget(self.boton_seleccionar_csv)
        file_row.addStretch()
        layout_importar.addLayout(file_row)
        # --- Preview visual ---
        self.preview_table = QTableWidget()
        self.preview_table.setMinimumHeight(160)
        self.preview_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        # self.preview_table.setStyleSheet("background: #fff9f3; color: #2563eb; border-radius: 8px;")
        layout_importar.addWidget(self.preview_table)
        # --- Área de advertencias/errores ---
        self.advertencias_label = QLabel()
        self.advertencias_label.setWordWrap(True)
        # self.advertencias_label.setStyleSheet("font-size: 13px; padding: 8px 0; color: #b45309; background: #fef9c3; border-radius: 8px;")
        self.advertencias_label.setVisible(False)
        layout_importar.addWidget(self.advertencias_label)
        # --- Mensaje de feedback ---
        self.mensaje_label = QLabel()
        self.mensaje_label.setWordWrap(True)
        # self.mensaje_label.setStyleSheet("font-size: 13px; padding: 8px 0;")
        layout_importar.addWidget(self.mensaje_label)
        # --- Botón Importar Inventario ---
        self.boton_importar_csv = QPushButton()
        self.boton_importar_csv.setIcon(QIcon("resources/icons/finish-check.svg"))
        self.boton_importar_csv.setText("Importar inventario")
        self.boton_importar_csv.setToolTip("Importar inventario a la base de datos")
        self.boton_importar_csv.setFixedHeight(48)
        self.boton_importar_csv.setMinimumWidth(220)
        self.boton_importar_csv.setEnabled(False)
        # self.boton_importar_csv.setStyleSheet("border-radius: 12px; background: #d1f7e7; font-size: 16px; font-weight: bold; color: #15803d;")
        layout_importar.addWidget(self.boton_importar_csv, alignment=Qt.AlignmentFlag.AlignCenter)
        layout_importar.addStretch()
        self.tab_importar.setLayout(layout_importar)
        self.tabs.addTab(self.tab_importar, "Importar Inventario")

        self.main_layout.addWidget(self.tabs)
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

        # Refuerzo de accesibilidad en botones principales
        for btn in [self.boton_seleccionar_csv, self.boton_importar_csv]:
            btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            # btn.setStyleSheet(btn.styleSheet() + "\nQPushButton:focus { outline: 2px solid #2563eb; border: 2px solid #2563eb; }")
            font = btn.font()
            if font.pointSize() < 12:
                font.setPointSize(12)
            btn.setFont(font)
            if not btn.toolTip():
                btn.setToolTip("Botón de acción")
            if not btn.accessibleName():
                btn.setAccessibleName("Botón de acción de configuración")
        # Refuerzo de accesibilidad en tabla de preview
        self.preview_table.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        # self.preview_table.setStyleSheet(self.preview_table.styleSheet() + "\nQTableWidget:focus { outline: 2px solid #2563eb; border: 2px solid #2563eb; }\nQTableWidget { font-size: 13px; }")
        self.preview_table.setToolTip("Tabla de previsualización de inventario")
        self.preview_table.setAccessibleName("Tabla de preview de configuración")
        # Refuerzo visual y robustez en header de tabla de preview
        h_header = self.preview_table.horizontalHeader() if hasattr(self.preview_table, 'horizontalHeader') else None
        if h_header is not None:
            try:
                # h_header.setStyleSheet("background-color: #e3f6fd; color: #2563eb; border-radius: 8px; font-size: 10px; padding: 8px 12px; border: 1px solid #e3e3e3;")
                pass
            except Exception as e:
                # EXCEPCIÓN VISUAL: Si el header no soporta setStyleSheet, documentar aquí y en docs/estandares_visuales.md
                pass
        else:
            # EXCEPCIÓN VISUAL: No se puede aplicar refuerzo visual porque el header es None
            pass
        # Refuerzo de accesibilidad en QLabel (incluye label_feedback y mensaje_label)
        for widget in self.findChildren(QLabel):
            font = widget.font()
            if font.pointSize() < 12:
                font.setPointSize(12)
            widget.setFont(font)
            # Refuerzo de accesibilidad descriptiva
            if not widget.accessibleDescription():
                widget.setAccessibleDescription("Label informativo o de feedback")
        # Márgenes y padding en layouts según estándar
        main_widget = self.centralWidget()
        layout = main_widget.layout() if main_widget is not None and hasattr(main_widget, 'layout') else None
        if layout is not None:
            layout.setContentsMargins(24, 20, 24, 20)
            layout.setSpacing(16)
        # EXCEPCIÓN: Este módulo no usa QLineEdit ni QComboBox en la vista principal, por lo que no aplica refuerzo en inputs ni selectores.

    def mostrar_mensaje(self, mensaje, tipo="info", destino="mensaje_label"):
        """
        Muestra un mensaje de feedback en un label específico (por defecto mensaje_label).
        Usar para feedback contextual en la pestaña actual (por ejemplo, importar inventario).
        Para feedback global o persistente, usar mostrar_feedback.
        Oculta el feedback anterior en el label destino antes de mostrar uno nuevo.
        """
        colores = {
            "exito": "#22c55e",
            "error": "#ef4444",
            "advertencia": "#f59e42",
            "info": "#2563eb"
        }
        iconos = {
            "exito": "✅",
            "error": "❌",
            "advertencia": "⚠️",
            "info": "ℹ️"
        }
        color = colores.get(tipo, "#2563eb")
        icono = iconos.get(tipo, "ℹ️")
        label = getattr(self, destino, None)
        if label:
            label.setText("")  # Oculta feedback anterior
            label.setText(f"<span style='color:{color};'>{icono} {mensaje}</span>")
            label.setAccessibleDescription(f"Mensaje de feedback tipo {tipo}")

    def mostrar_advertencias(self, advertencias):
        if advertencias:
            self.advertencias_label.setText("\n".join([f"⚠️ {a}" for a in advertencias]))
            self.advertencias_label.setVisible(True)
        else:
            self.advertencias_label.clear()
            self.advertencias_label.setVisible(False)

    def mostrar_errores(self, errores):
        if errores:
            self.mostrar_mensaje("\n".join(errores), tipo="error")
            self.advertencias_label.setVisible(False)

    def mostrar_exito(self, mensajes):
        if mensajes:
            self.mostrar_mensaje("\n".join(mensajes), tipo="exito")
            self.advertencias_label.setVisible(False)

    def mostrar_preview(self, dataframe):
        if dataframe is None or dataframe.empty:
            self.preview_table.clear()
            self.preview_table.setRowCount(0)
            self.preview_table.setColumnCount(0)
            self.preview_table.setHorizontalHeaderLabels([])
            self.boton_importar_csv.setEnabled(False)
            self.mostrar_mensaje("No se pudo cargar el archivo o está vacío.", tipo="error")
            return
        self.preview_table.setRowCount(min(10, len(dataframe)))
        self.preview_table.setColumnCount(len(dataframe.columns))
        self.preview_table.setHorizontalHeaderLabels([str(c) for c in dataframe.columns])
        for i in range(min(10, len(dataframe))):
            for j, col in enumerate(dataframe.columns):
                val = str(dataframe.iloc[i][col])
                self.preview_table.setItem(i, j, QTableWidgetItem(val))
        self.preview_table.resizeColumnsToContents()
        self.boton_importar_csv.setEnabled(True)
        self.mostrar_mensaje(f"Archivo cargado correctamente. {len(dataframe)} filas detectadas.", tipo="exito")

    def confirmar_importacion(self, total_filas):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setWindowTitle("Confirmar importación")
        msg.setText(f"¿Deseas importar {total_filas} filas a la base de datos? Se realizará backup antes de modificar.")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        return msg.exec() == QMessageBox.StandardButton.Yes

    def seleccionar_archivo_csv(self):
        file, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo de inventario", "inventario", "Archivos CSV (*.csv);;Archivos Excel (*.xlsx *.xls)")
        if file:
            self.csv_file_input.setText(file)
            try:
                if file.endswith('.csv'):
                    df = pd.read_csv(file, sep=';', encoding='utf-8')
                else:
                    df = pd.read_excel(file)
            except Exception as e:
                df = None
                self.mostrar_mensaje(f"Error al leer el archivo: {e}", tipo="error")
            self.mostrar_preview(df)
        else:
            self.csv_file_input.setText("Ningún archivo seleccionado")
            self.mostrar_preview(None)
            self.boton_importar_csv.setEnabled(False)

    def conectar_eventos_importacion(self, controller):
        self.boton_seleccionar_csv.clicked.connect(self.seleccionar_archivo_csv)
        self.boton_importar_csv.clicked.connect(controller.importar_csv_inventario)

    def mostrar_feedback(self, mensaje, tipo="info"):
        """
        Muestra un mensaje de feedback global y accesible en la parte superior de la vista.
        Oculta automáticamente el feedback anterior antes de mostrar uno nuevo.
        Usar para mensajes importantes o persistentes que afectan a todo el módulo.
        """
        self.ocultar_feedback()
        colores = {
            "info": "#2563eb",
            "exito": "#22c55e",
            "advertencia": "#fbbf24",
            "error": "#ef4444"
        }
        color = colores.get(tipo, "#2563eb")
        iconos = {
            "info": "ℹ️ ",
            "exito": "✅ ",
            "advertencia": "⚠️ ",
            "error": "❌ "
        }
        icono = iconos.get(tipo, "ℹ️ ")
        # self.label_feedback.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 13px; border-radius: 8px; padding: 8px; background: #f1f5f9;")
        self.label_feedback.setText(f"{icono}{mensaje}")
        self.label_feedback.setVisible(True)
        self.label_feedback.setAccessibleDescription(f"Mensaje de feedback tipo {tipo}")

    def ocultar_feedback(self):
        if hasattr(self, 'label_feedback'):
            self.label_feedback.setVisible(False)
            self.label_feedback.setText("")

    def documentar_excepciones_visuales(self, h_header):
        """
        Documenta excepciones visuales en el header de la tabla preview.
        Si el header no soporta setStyleSheet, se debe documentar aquí y en docs/estandares_visuales.md
        """
        pass  # Implementar lógica de documentación si es necesario

    def ocultar_pestana_permisos(self, es_admin):
        """
        Oculta la pestaña de permisos si el usuario no es admin.
        Se debe llamar a este método después de inicializar la UI y antes de mostrar la ventana.
        """
        if not es_admin:
            idx = self.tabs.indexOf(self.tab_permisos)
            if idx != -1:
                self.tabs.removeTab(idx)

        # SUGERENCIAS DE MEJORA FUTURA:
        # - Agregar validación visual de columnas requeridas/faltantes en el preview.
        # - Mostrar resumen de filas válidas/erróneas antes de importar.
        # - Permitir descargar plantilla de ejemplo.
        # - Mostrar historial de importaciones recientes.

    def _emitir_cambio_tema(self):
        tema = "light" if self.combo_tema.currentIndex() == 0 else "dark"
        self.theme_changed.emit(tema)

    def _cargar_configuracion_conexion(self):
        keys = ["DB_SERVER", "DB_USERNAME", "DB_PASSWORD", "DB_DATABASE", "DB_TIMEOUT"]
        valores = ConfigManager.get_all(keys)
        self.input_db_server.setText(valores.get("DB_SERVER", ""))
        self.input_db_username.setText(valores.get("DB_USERNAME", ""))
        self.input_db_password.setText(valores.get("DB_PASSWORD", ""))
        self.input_db_database.setText(valores.get("DB_DATABASE", ""))
        self.input_db_timeout.setText(valores.get("DB_TIMEOUT", "5"))

    def _probar_conexion(self):
        import pyodbc
        servidor = self.input_db_server.text().strip()
        usuario = self.input_db_username.text().strip()
        password = self.input_db_password.text()
        database = self.input_db_database.text().strip()
        timeout = int(self.input_db_timeout.text() or 5)
        try:
            conn_str = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={servidor};DATABASE={database};UID={usuario};PWD={password};TrustServerCertificate=yes;"
            )
            with pyodbc.connect(conn_str, timeout=timeout):
                self.label_estado_conexion.setText("<span style='color:#22c55e;'>✅ Conexión exitosa</span>")
        except Exception as e:
            self.label_estado_conexion.setText(f"<span style='color:#ef4444;'>❌ Error: {e}</span>")

    def _guardar_configuracion_conexion(self):
        data = {
            "DB_SERVER": self.input_db_server.text().strip(),
            "DB_USERNAME": self.input_db_username.text().strip(),
            "DB_PASSWORD": self.input_db_password.text(),
            "DB_DATABASE": self.input_db_database.text().strip(),
            "DB_TIMEOUT": self.input_db_timeout.text().strip() or "5"
        }
        errores = ConfigManager.validate(data)
        if errores:
            self.label_estado_conexion.setText("<span style='color:#ef4444;'>❌ " + ", ".join(errores.values()) + "</span>")
            return
        for k, v in data.items():
            ConfigManager.set(k, v)
        self.label_estado_conexion.setText("<span style='color:#22c55e;'>✅ Configuración guardada correctamente</span>")
        # Opcional: recargar conexión global aquí