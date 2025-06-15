from PyQt6.QtWidgets import QMainWindow, QFileDialog, QTableWidget, QTableWidgetItem, QMessageBox, QLabel, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QTabWidget, QComboBox
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QSize, pyqtSignal
import pandas as pd
from core.ui_components import estilizar_boton_icono

# --- Definición de constantes globales para literales, tooltips y estilos (restauradas y unificadas) ---
LABEL_GENERAL = "Configuración general del sistema (próximamente)"
LABEL_CONEXION = "Configuración de conexión a base de datos (próximamente)"
LABEL_PERMISOS = "Gestión de permisos de usuario (próximamente)"
LABEL_TEMA = "Tema:"
MSG_NO_ARCHIVO = "Ningún archivo seleccionado"
MSG_NO_CARGA = "No se pudo cargar el archivo o está vacío."
MSG_CONFIRMAR_IMPORT = "Confirmar importación"
FILE_DIALOG_TITLE = "Seleccionar archivo de inventario"
FILE_FILTER = "Archivos CSV (*.csv);;Archivos Excel (*.xlsx *.xls)"
BTN_OFFLINE_TEXT = "Activar modo offline"
BTN_OFFLINE_ICON = "img/offline_icon.svg"
BTN_OFFLINE_ACCESSIBLE = "Botón activar modo offline"
BTN_OFFLINE_DESC = "Activa el modo offline de la aplicación"
BTN_OFFLINE_STYLE = "border-radius: 8px; background: #f1f5f9; font-size: 14px; padding: 8px 24px;"
TOOLTIP_AGREGAR_CONFIG = "Agregar configuración"
TOOLTIP_ACTIVAR_OFFLINE = "Activa el modo offline de la app"
TOOLTIP_SELECCIONAR_CSV = "Seleccionar archivo CSV/Excel"
TOOLTIP_IMPORTAR_CSV = "Importar inventario a la base de datos"
TOOLTIP_TABLA_PREVIEW = "Tabla de previsualización de inventario"
BTN_ACCION_TOOLTIP = "Botón de acción"
BTN_ACCION_ACCESSIBLE = "Botón de acción de configuración"
FOCUS_STYLE = "\nQPushButton:focus { outline: 2px solid #2563eb; border: 2px solid #2563eb; }"
PREVIEW_TABLE_STYLE = "\nQTableWidget:focus { outline: 2px solid #2563eb; border: 2px solid #2563eb; }\nQTableWidget { font-size: 13px; }"
HEADER_STYLE = "background-color: #e3f6fd; color: #2563eb; border-radius: 8px; font-size: 10px; padding: 8px 12px; border: 1px solid #e3e3e3;"
LABEL_FEEDBACK_DESC = "Label informativo o de feedback"
ADVERTENCIAS_LABEL_STYLE = "font-size: 13px; padding: 8px 0; color: #b45309; background: #fef9c3; border-radius: 8px;"
MENSAJE_LABEL_STYLE = "font-size: 13px; padding: 8px 0;"
BTN_IMPORTAR_ICON = "img/finish-check.svg"
BTN_IMPORTAR_TEXT = "Importar inventario"
BTN_IMPORTAR_ACCESSIBLE = "Botón importar inventario"
BTN_IMPORTAR_DESC = "Importa los datos del archivo seleccionado a la base de datos"
BTN_IMPORTAR_STYLE = "border-radius: 12px; background: #d1f7e7; font-size: 16px; font-weight: bold; color: #15803d;"
TAB_GENERAL = "General"
TAB_CONEXION = "Conexión"
TAB_PERMISOS = "Permisos"
TAB_IMPORTAR = "Importar Inventario"
IMPORTAR_INVENTARIO_TITLE = "Importar Inventario desde CSV/Excel"
IMPORTAR_INVENTARIO_STYLE = "font-size: 18px; font-weight: bold; color: #2563eb;"
AYUDA_IMPORT = "Selecciona un archivo CSV o Excel con los datos de inventario. El sistema detectará y completará automáticamente las columnas requeridas. Puedes importar archivos incompletos: los campos faltantes se rellenarán por defecto."
AYUDA_IMPORT_STYLE = "font-size: 13px; color: #64748b; background: #f1f5f9; border-radius: 8px; padding: 8px 12px;"
CSV_INPUT_STYLE = "background: #e3f6fd; border-radius: 8px; padding: 8px 16px; color: #2563eb;"
EXCEL_ICON = "img/excel_icon.svg"
BTN_SELECCIONAR_CSV_ACCESSIBLE = "Botón seleccionar archivo CSV/Excel"
BTN_SELECCIONAR_CSV_DESC = "Selecciona un archivo CSV o Excel para importar inventario"
BTN_SELECCIONAR_CSV_STYLE = "border-radius: 8px; background: #e3f6fd;"
PREVIEW_TABLE_BASE_STYLE = "background: #fff9f3; color: #2563eb; border-radius: 8px;"
PREVIEW_TABLE_DESC = "Muestra una vista previa de los datos a importar"

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

    def setup_ui(self):
        # --- HEADER VISUAL MODERNO: título y barra de botones alineados ---
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(24)
        self.label_titulo = QLabel("Gestión de Configuración")
        header_layout.addWidget(self.label_titulo, alignment=Qt.AlignmentFlag.AlignVCenter)
        # Botón principal (Agregar configuración)
        self.boton_agregar = QPushButton()
        self.boton_agregar.setIcon(QIcon("img/add-material.svg"))
        self.boton_agregar.setIconSize(QSize(24, 24))
        self.boton_agregar.setToolTip(TOOLTIP_AGREGAR_CONFIG)
        self.boton_agregar.setAccessibleName("Botón agregar configuración")
        from core.ui_components import estilizar_boton_icono
        estilizar_boton_icono(self.boton_agregar)
        header_layout.addWidget(self.boton_agregar)
        header_layout.addStretch()
        self.main_layout.addLayout(header_layout)

        # QTabWidget principal
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("QTabWidget::pane { border-radius: 12px; background: #f1f5f9; } QTabBar::tab { min-width: 160px; min-height: 36px; font-size: 14px; font-weight: 600; border-radius: 8px; padding: 8px 24px; margin-right: 8px; } QTabBar::tab:selected { background: #e3f6fd; color: #2563eb; }")
        # Refactor: separar inicialización de pestañas en métodos auxiliares para reducir complejidad
        self._init_tab_general()
        self._init_tab_conexion()
        self._init_tab_permisos()
        self._init_tab_importar()
        self.main_layout.addWidget(self.tabs)
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

        # Refuerzo de accesibilidad y estilos
        self._reforzar_accesibilidad_botones([self.boton_seleccionar_csv, self.boton_importar_csv])
        self._reforzar_accesibilidad_tabla(self.preview_table)
        self._reforzar_header_tabla(self.preview_table)
        self._reforzar_accesibilidad_labels()
        self._aplicar_margenes_layout()

        # EXCEPCIÓN: Este módulo no usa QLineEdit ni QComboBox en la vista principal, por lo que no aplica refuerzo en inputs ni selectores.

    def _reforzar_accesibilidad_botones(self, botones):
        for btn in botones:
            btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            btn.setStyleSheet(btn.styleSheet() + FOCUS_STYLE)
            font = btn.font()
            if font.pointSize() < 12:
                font.setPointSize(12)
            btn.setFont(font)
            if not btn.toolTip():
                btn.setToolTip(BTN_ACCION_TOOLTIP)
            if not btn.accessibleName():
                btn.setAccessibleName(BTN_ACCION_ACCESSIBLE)

    def _reforzar_accesibilidad_tabla(self, tabla):
        tabla.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        tabla.setStyleSheet(tabla.styleSheet() + PREVIEW_TABLE_STYLE)

    def _reforzar_header_tabla(self, tabla):
        h_header = tabla.horizontalHeader() if hasattr(tabla, 'horizontalHeader') else None
        if h_header is not None:
            try:
                h_header.setStyleSheet(HEADER_STYLE)
            except Exception:
                self.documentar_excepciones_visuales(h_header)

    def _reforzar_accesibilidad_labels(self):
        for widget in self.findChildren(QLabel):
            font = widget.font()
            if font.pointSize() < 12:
                font.setPointSize(12)
            widget.setFont(font)
            if not widget.accessibleDescription():
                widget.setAccessibleDescription(LABEL_FEEDBACK_DESC)

    def _aplicar_margenes_layout(self):
        main_widget = self.centralWidget()
        layout = main_widget.layout() if main_widget is not None and hasattr(main_widget, 'layout') else None
        if layout is not None:
            layout.setContentsMargins(24, 20, 24, 20)
            layout.setSpacing(16)

    # --- LIMPIEZA DE DUPLICADOS Y UNIFICACIÓN DE FUNCIONES ---
    # Eliminar todas las funciones duplicadas: dejar solo una definición de cada método.
    # Ya están presentes las funciones correctas y únicas a partir de la línea 101 (después de setup_ui).
    # Elimino cualquier redefinición posterior de:
    # - confirmar_importacion
    # - seleccionar_archivo_csv
    # - conectar_eventos_importacion
    # - mostrar_feedback
    # - ocultar_feedback
    # - documentar_excepciones_visuales
    # - ocultar_pestana_permisos
    # - _emitir_cambio_tema
    # - _init_tab_general
    # - _init_tab_conexion
    # - _init_tab_permisos
    # - _init_tab_importar
    # - mostrar_mensaje
    # - mostrar_advertencias
    # - mostrar_errores
    # - mostrar_exito
    # - mostrar_preview
    #
    # (No se repiten en el archivo tras la limpieza previa, pero si existieran, deben eliminarse y dejar solo la primera aparición tras setup_ui)
    #
    # Además, aseguro que todos los literales y estilos repetidos usen las constantes ya definidas.
    #
    # El archivo queda limpio de duplicados y advertencias de funciones repetidas.

    def confirmar_importacion(self, total_filas):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setWindowTitle(MSG_CONFIRMAR_IMPORT)
        msg.setText(f"¿Deseas importar {total_filas} filas a la base de datos? Se realizará backup antes de modificar.")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        return msg.exec() == QMessageBox.StandardButton.Yes

    def seleccionar_archivo_csv(self):
        file, _ = QFileDialog.getOpenFileName(self, FILE_DIALOG_TITLE, "inventario", FILE_FILTER)
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
            self.csv_file_input.setText(MSG_NO_ARCHIVO)
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
        self.label_feedback.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 13px; border-radius: 8px; padding: 8px; background: #f1f5f9;")
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

    def _init_tab_general(self):
        self.tab_general = QWidget()
        layout_general = QVBoxLayout(self.tab_general)
        label_general = QLabel(LABEL_GENERAL)
        label_general.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_general.addWidget(label_general)
        self.boton_activar_offline = QPushButton()
        self.boton_activar_offline.setText(BTN_OFFLINE_TEXT)
        self.boton_activar_offline.setIcon(QIcon(BTN_OFFLINE_ICON))
        self.boton_activar_offline.setToolTip(TOOLTIP_ACTIVAR_OFFLINE)
        self.boton_activar_offline.setAccessibleName(BTN_OFFLINE_ACCESSIBLE)
        estilizar_boton_icono(self.boton_activar_offline)
        self.boton_activar_offline.setStyleSheet(BTN_OFFLINE_STYLE)
        layout_general.addWidget(self.boton_activar_offline)
        theme_row = QHBoxLayout()
        theme_label = QLabel(LABEL_TEMA)
        self.combo_tema = QComboBox()
        self.combo_tema.addItems(["Claro", "Oscuro"])
        self.combo_tema.setCurrentIndex(0)
        self.combo_tema.currentIndexChanged.connect(self._emitir_cambio_tema)
        theme_row.addWidget(theme_label)
        theme_row.addWidget(self.combo_tema)
        theme_row.addStretch()
        layout_general.insertLayout(0, theme_row)
        self.tabs.addTab(self.tab_general, TAB_GENERAL)

    def _init_tab_conexion(self):
        self.tab_conexion = QWidget()
        layout_conexion = QVBoxLayout(self.tab_conexion)
        label_conexion = QLabel(LABEL_CONEXION)
        label_conexion.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_conexion.addWidget(label_conexion)
        self.tabs.addTab(self.tab_conexion, TAB_CONEXION)

    def _init_tab_permisos(self):
        self.tab_permisos = QWidget()
        layout_permisos = QVBoxLayout(self.tab_permisos)
        label_permisos = QLabel(LABEL_PERMISOS)
        label_permisos.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_permisos.addWidget(label_permisos)
        self.tabs.addTab(self.tab_permisos, TAB_PERMISOS)

    def _init_tab_importar(self):
        self.tab_importar = QWidget()
        layout_importar = QVBoxLayout(self.tab_importar)
        layout_importar.setContentsMargins(0, 0, 0, 0)
        layout_importar.setSpacing(12)

        label_titulo = QLabel(IMPORTAR_INVENTARIO_TITLE)
        label_titulo.setStyleSheet(IMPORTAR_INVENTARIO_STYLE)
        layout_importar.addWidget(label_titulo)

        self.label_ayuda_import = QLabel(AYUDA_IMPORT)
        self.label_ayuda_import.setWordWrap(True)
        self.label_ayuda_import.setStyleSheet(AYUDA_IMPORT_STYLE)
        layout_importar.addWidget(self.label_ayuda_import)

        self._init_importar_file_row(layout_importar)
        self._init_importar_preview_table(layout_importar)
        self._init_importar_labels(layout_importar)
        self._init_importar_import_button(layout_importar)

        layout_importar.addStretch()
        self.tab_importar.setLayout(layout_importar)
        self.tabs.addTab(self.tab_importar, TAB_IMPORTAR)

        self._reforzar_accesibilidad_botones([self.boton_seleccionar_csv, self.boton_importar_csv])
        self._reforzar_accesibilidad_tabla(self.preview_table)
        self._reforzar_header_tabla(self.preview_table)
        self._reforzar_accesibilidad_labels()
        self._aplicar_margenes_layout()

    def _init_importar_file_row(self, layout_importar):
        file_row = QHBoxLayout()
        self.csv_file_input = QLabel(MSG_NO_ARCHIVO)
        self.csv_file_input.setStyleSheet(CSV_INPUT_STYLE)
        self.boton_seleccionar_csv = QPushButton()
        self.boton_seleccionar_csv.setIcon(QIcon(EXCEL_ICON))
        self.boton_seleccionar_csv.setToolTip(TOOLTIP_SELECCIONAR_CSV)
        self.boton_seleccionar_csv.setAccessibleName(BTN_SELECCIONAR_CSV_ACCESSIBLE)
        estilizar_boton_icono(self.boton_seleccionar_csv)
        self.boton_seleccionar_csv.setStyleSheet(BTN_SELECCIONAR_CSV_STYLE)
        file_row.addWidget(self.csv_file_input)
        file_row.addWidget(self.boton_seleccionar_csv)
        file_row.addStretch()
        layout_importar.addLayout(file_row)

    def _init_importar_preview_table(self, layout_importar):
        self.preview_table = QTableWidget()
        self.preview_table.setMinimumHeight(160)
        self.preview_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.preview_table.setStyleSheet(PREVIEW_TABLE_BASE_STYLE)
        self.preview_table.setToolTip(TOOLTIP_TABLA_PREVIEW)
        self.preview_table.setAccessibleName(TOOLTIP_TABLA_PREVIEW)
        self.preview_table.setAccessibleDescription(PREVIEW_TABLE_DESC)
        self.preview_table.setStyleSheet(self.preview_table.styleSheet() + PREVIEW_TABLE_STYLE)
        layout_importar.addWidget(self.preview_table)

    def _init_importar_labels(self, layout_importar):
        self.advertencias_label = QLabel()
        self.advertencias_label.setWordWrap(True)
        self.advertencias_label.setStyleSheet(ADVERTENCIAS_LABEL_STYLE)
        self.advertencias_label.setVisible(False)
        layout_importar.addWidget(self.advertencias_label)
        self.mensaje_label = QLabel()
        self.mensaje_label.setWordWrap(True)
        self.mensaje_label.setStyleSheet(MENSAJE_LABEL_STYLE)
        layout_importar.addWidget(self.mensaje_label)

    def _init_importar_import_button(self, layout_importar):
        self.boton_importar_csv = QPushButton()
        self.boton_importar_csv.setIcon(QIcon(BTN_IMPORTAR_ICON))
        self.boton_importar_csv.setText(BTN_IMPORTAR_TEXT)
        self.boton_importar_csv.setToolTip(TOOLTIP_IMPORTAR_CSV)
        self.boton_importar_csv.setAccessibleName(BTN_IMPORTAR_ACCESSIBLE)
        estilizar_boton_icono(self.boton_importar_csv)
        self.boton_importar_csv.setFixedHeight(48)
        self.boton_importar_csv.setMinimumWidth(220)
        self.boton_importar_csv.setEnabled(False)
        self.boton_importar_csv.setStyleSheet(BTN_IMPORTAR_STYLE)
        layout_importar.addWidget(self.boton_importar_csv, alignment=Qt.AlignmentFlag.AlignCenter)

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
            self.mostrar_mensaje(MSG_NO_CARGA, tipo="error")
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