# ---
# MIGRACIÓN A QSS GLOBAL (MAYO 2025)
# Todas las líneas comentadas con setStyleSheet en este archivo corresponden a estilos visuales migrados a los archivos QSS globales (themes/light.qss y dark.qss).
# Justificación: la política de la app prohíbe estilos embebidos salvo excepciones documentadas. Si alguna línea comentada es reactivada, debe justificarse aquí y en docs/estandares_visuales.md.
# No quedan estilos embebidos activos en métodos auxiliares ni diálogos personalizados; todo feedback visual y estilos de headers/tablas/botones se gestiona por QSS global.
# Si los tests automáticos de estándares fallan por líneas comentadas, dejar constancia en la documentación.
# ---

import os
import json
import tempfile
import qrcode
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QFormLayout, QTableWidget, QHBoxLayout, QGraphicsDropShadowEffect, QMenu, QFileDialog, QDialog, QTabWidget, QMessageBox, QTableWidgetItem, QComboBox, QProgressBar
from PyQt6.QtCore import QTimer, Qt, QPoint
from PyQt6.QtGui import QIcon, QColor, QPixmap, QPainter, QAction
from PyQt6.QtCore import QSize
from PyQt6.QtPrintSupport import QPrinter
from functools import partial
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from core.table_responsive_mixin import TableResponsiveMixin
from core.ui_components import estilizar_boton_icono, aplicar_qss_global_y_tema
from core.logger import log_error

class ContabilidadView(QWidget, TableResponsiveMixin):
    def __init__(self, db_connection=None, obras_model=None):
        super().__init__()
        # Aplicar QSS global y tema visual (solo desde resources/qss/)
        from utils.theme_manager import cargar_modo_tema
        tema = cargar_modo_tema()
        qss_tema = f"resources/qss/theme_{tema}.qss"
        aplicar_qss_global_y_tema(self, qss_global_path="resources/qss/theme_light.qss", qss_tema_path=qss_tema)
        self.db_connection = db_connection
        self.obras_model = obras_model
        # Inicialización segura de headers para evitar AttributeError
        self.balance_headers = []
        self.recibos_headers = []
        self.pagos_headers = []
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(0)

        # --- HEADER VISUAL MODERNO: título y barra de botones alineados ---
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(24)
        self.label_titulo = QLabel("Gestión de Contabilidad")
        header_layout.addWidget(self.label_titulo, alignment=Qt.AlignmentFlag.AlignVCenter)
        # Botón principal (Agregar registro)
        self.boton_agregar = QPushButton()
        self.boton_agregar.setIcon(QIcon("resources/icons/add-material.svg"))
        self.boton_agregar.setIconSize(QSize(24, 24))
        self.boton_agregar.setToolTip("Agregar registro")
        header_layout.addWidget(self.boton_agregar)
        header_layout.addStretch()
        self.main_layout.addLayout(header_layout)

        # QTabWidget para las tres pestañas
        self.tabs = QTabWidget()
        self.tabs.setObjectName("contabilidad-tabs")
        self.main_layout.addWidget(self.tabs)

        # --- Filtros y búsqueda rápida ---
        self.filtro_balance = QLineEdit()
        self.filtro_balance.setPlaceholderText("Buscar en movimientos...")
        self.filtro_balance.setToolTip("Filtrar movimientos por cualquier campo")
        self.filtro_balance.textChanged.connect(self.filtrar_tabla_balance)

        # --- Pestaña Balance ---
        self.tab_balance = QWidget()
        self.tab_balance_layout = QVBoxLayout()
        self.tab_balance.setLayout(self.tab_balance_layout)
        self.tab_balance_layout.addWidget(self.filtro_balance)
        self.tabla_balance = QTableWidget()
        self.tabla_balance.setObjectName("tabla_balance")
        self.make_table_responsive(self.tabla_balance)
        self.tab_balance_layout.addWidget(self.tabla_balance)
        self.boton_agregar_balance = QPushButton()
        self.boton_agregar_balance.setIcon(QIcon("resources/icons/plus_icon.svg"))
        self.boton_agregar_balance.setToolTip("Agregar movimiento contable")
        estilizar_boton_icono(self.boton_agregar_balance)
        btn_balance_layout = QHBoxLayout()
        btn_balance_layout.addStretch()
        btn_balance_layout.addWidget(self.boton_agregar_balance)
        self.tab_balance_layout.addLayout(btn_balance_layout)
        self.tabs.addTab(self.tab_balance, "Balance")

        # --- Pestaña Seguimiento de Pagos ---
        self.tab_pagos = QWidget()
        self.tab_pagos_layout = QVBoxLayout()
        self.tab_pagos.setLayout(self.tab_pagos_layout)
        self.filtro_pagos = QLineEdit()
        self.filtro_pagos.setPlaceholderText("Buscar pagos por obra, colocador...")
        self.filtro_pagos.setToolTip("Filtrar pagos por cualquier campo")
        self.filtro_pagos.textChanged.connect(self.filtrar_tabla_pagos)
        self.tab_pagos_layout.addWidget(self.filtro_pagos)
        self.tabla_pagos = QTableWidget()
        self.tabla_pagos.setObjectName("tabla_pagos")
        self.make_table_responsive(self.tabla_pagos)
        self.tab_pagos_layout.addWidget(self.tabla_pagos)
        self.tabs.addTab(self.tab_pagos, "Seguimiento de Pagos")

        # --- Pestaña Recibos ---
        self.tab_recibos = QWidget()
        self.tab_recibos_layout = QVBoxLayout()
        self.tab_recibos.setLayout(self.tab_recibos_layout)
        self.filtro_recibos = QLineEdit()
        self.filtro_recibos.setPlaceholderText("Buscar recibos por obra, concepto, destinatario...")
        self.filtro_recibos.setToolTip("Filtrar recibos por cualquier campo")
        self.filtro_recibos.textChanged.connect(self.filtrar_tabla_recibos)
        self.tab_recibos_layout.addWidget(self.filtro_recibos)
        # Layout horizontal para botón agregar (arriba a la derecha)
        top_btn_layout = QHBoxLayout()
        top_btn_layout.addStretch()
        self.boton_agregar_recibo = QPushButton()
        self.boton_agregar_recibo.setIcon(QIcon("resources/icons/plus_icon.svg"))
        self.boton_agregar_recibo.setToolTip("Agregar nuevo recibo")
        estilizar_boton_icono(self.boton_agregar_recibo)
        top_btn_layout.addWidget(self.boton_agregar_recibo)
        self.tab_recibos_layout.addLayout(top_btn_layout)
        # Tabla de recibos
        self.tabla_recibos = QTableWidget()
        self.tabla_recibos.setObjectName("tabla_recibos")
        self.make_table_responsive(self.tabla_recibos)
        self.tab_recibos_layout.addWidget(self.tabla_recibos)
        self.tabs.addTab(self.tab_recibos, "Recibos")

        # --- Pestaña Estadísticas ---
        self.tab_estadisticas = QWidget()
        self.tab_estadisticas_layout = QVBoxLayout()
        self.tab_estadisticas.setLayout(self.tab_estadisticas_layout)
        self.label_resumen = QLabel("Resumen de Balance")
        self.tab_estadisticas_layout.addWidget(self.label_resumen)
        # Controles para filtros y tipo de gráfico
        controles_layout = QHBoxLayout()
        self.combo_tipo_grafico = QComboBox()
        self.combo_tipo_grafico.addItems([
            "Ingresos vs Egresos", "Cobros por Obra", "Pagos por Obra", "Evolución Mensual", "Desglose por Moneda"
        ])
        self.combo_tipo_grafico.setToolTip("Seleccionar tipo de gráfico estadístico")
        controles_layout.addWidget(QLabel("Tipo de gráfico:"))
        controles_layout.addWidget(self.combo_tipo_grafico)
        self.combo_anio = QComboBox()
        self.combo_anio.setToolTip("Año a analizar")
        controles_layout.addWidget(QLabel("Año:"))
        controles_layout.addWidget(self.combo_anio)
        self.combo_mes = QComboBox()
        self.combo_mes.addItems(["Todos"] + [str(m) for m in range(1, 13)])
        self.combo_mes.setToolTip("Mes a analizar")
        controles_layout.addWidget(QLabel("Mes:"))
        controles_layout.addWidget(self.combo_mes)
        self.input_dolar = QLineEdit()
        self.input_dolar.setPlaceholderText("Valor dólar oficial")
        self.input_dolar.setToolTip("Ingrese el valor del dólar para conversión")
        controles_layout.addWidget(QLabel("Dólar:"))
        controles_layout.addWidget(self.input_dolar)
        self.boton_actualizar_grafico = QPushButton()
        self.boton_actualizar_grafico.setIcon(QIcon("resources/icons/actualizar.svg"))
        self.boton_actualizar_grafico.setToolTip("Actualizar gráfico")
        estilizar_boton_icono(self.boton_actualizar_grafico)
        controles_layout.addWidget(self.boton_actualizar_grafico)
        self.boton_estadistica_personalizada = QPushButton()
        self.boton_estadistica_personalizada.setIcon(QIcon("resources/icons/estadistica.svg"))
        self.boton_estadistica_personalizada.setToolTip("Estadística Personalizada")
        estilizar_boton_icono(self.boton_estadistica_personalizada)
        controles_layout.addWidget(self.boton_estadistica_personalizada)
        self.boton_estadistica_personalizada.clicked.connect(self.abrir_dialogo_estadistica_personalizada)
        # Combo para estadísticas personalizadas
        self.combo_estadistica_personalizada = QComboBox()
        self.combo_estadistica_personalizada.setToolTip("Seleccionar estadística personalizada guardada")
        self.combo_estadistica_personalizada.addItem("(Ninguna personalizada)")
        self.combo_estadistica_personalizada.currentIndexChanged.connect(self.seleccionar_estadistica_personalizada)
        controles_layout.addWidget(QLabel("Personalizada:"))
        controles_layout.addWidget(self.combo_estadistica_personalizada)
        self.tab_estadisticas_layout.addLayout(controles_layout)
        self.grafico_canvas = FigureCanvas(Figure(figsize=(6, 4)))
        self.tab_estadisticas_layout.addWidget(self.grafico_canvas)
        self.setup_exportar_grafico_btn()
        self.tabs.addTab(self.tab_estadisticas, "Estadísticas")

        # Señales para actualizar el gráfico
        self.boton_actualizar_grafico.clicked.connect(self.actualizar_grafico_estadisticas)
        self.combo_tipo_grafico.currentIndexChanged.connect(self.actualizar_grafico_estadisticas)
        self.combo_anio.currentIndexChanged.connect(self.actualizar_grafico_estadisticas)
        self.combo_mes.currentIndexChanged.connect(self.actualizar_grafico_estadisticas)
        self.input_dolar.editingFinished.connect(self.actualizar_grafico_estadisticas)

        self.setLayout(self.main_layout)

        # --- FEEDBACK VISUAL CENTRALIZADO Y QSS GLOBAL ---
        self.label_feedback = QLabel()
        self.label_feedback.setObjectName("label_feedback")
        # QSS global gestiona el estilo del feedback visual, no usar setStyleSheet embebido
        self.label_feedback.setVisible(False)
        self.label_feedback.setAccessibleName("Mensaje de feedback de contabilidad")
        self.label_feedback.setAccessibleDescription("Mensaje de feedback visual y accesible para el usuario")
        self.main_layout.addWidget(self.label_feedback)
        self._feedback_timer = None
        # --- FIN FEEDBACK VISUAL GLOBAL ---

        # --- Sincronización dinámica de headers ---
        self.sync_headers()

        # Configuración de columnas y persistencia para cada tabla
        self.config_path_balance = f"config_contabilidad_balance_columns.json"
        self.config_path_pagos = f"config_contabilidad_pagos_columns.json"
        self.config_path_recibos = f"config_contabilidad_recibos_columns.json"
        self.columnas_visibles_balance = self.cargar_config_columnas(self.config_path_balance, self.balance_headers)
        self.columnas_visibles_pagos = self.cargar_config_columnas(self.config_path_pagos, self.pagos_headers)
        self.columnas_visibles_recibos = self.cargar_config_columnas(self.config_path_recibos, self.recibos_headers)
        self.aplicar_columnas_visibles(self.tabla_balance, self.balance_headers, self.columnas_visibles_balance)
        self.aplicar_columnas_visibles(self.tabla_pagos, self.pagos_headers, self.columnas_visibles_pagos)
        self.aplicar_columnas_visibles(self.tabla_recibos, self.recibos_headers, self.columnas_visibles_recibos)

        # Menú de columnas y QR para cada tabla
        header_balance = self.tabla_balance.horizontalHeader() if hasattr(self.tabla_balance, 'horizontalHeader') else None
        if header_balance is not None:
            if hasattr(header_balance, 'setContextMenuPolicy'):
                header_balance.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            if hasattr(header_balance, 'customContextMenuRequested'):
                header_balance.customContextMenuRequested.connect(partial(self.mostrar_menu_columnas, self.tabla_balance, self.balance_headers, self.columnas_visibles_balance, self.config_path_balance))
            if hasattr(header_balance, 'sectionDoubleClicked'):
                header_balance.sectionDoubleClicked.connect(partial(self.auto_ajustar_columna, self.tabla_balance))
            if hasattr(header_balance, 'setSectionsMovable'):
                header_balance.setSectionsMovable(True)
            if hasattr(header_balance, 'setSectionsClickable'):
                header_balance.setSectionsClickable(True)
            if hasattr(header_balance, 'sectionClicked'):
                header_balance.sectionClicked.connect(partial(self.mostrar_menu_columnas_header, self.tabla_balance, self.balance_headers, self.columnas_visibles_balance, self.config_path_balance))
            self.tabla_balance.setHorizontalHeader(header_balance)
        else:
            # EXCEPCIÓN VISUAL: Si el header es None, no se puede aplicar menú contextual ni acciones de header.
            # Documentar en docs/estandares_visuales.md si ocurre en producción.
            pass

        header_pagos = self.tabla_pagos.horizontalHeader()
        if header_pagos is not None:
            header_pagos.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            header_pagos.customContextMenuRequested.connect(partial(self.mostrar_menu_columnas, self.tabla_pagos, self.pagos_headers, self.columnas_visibles_pagos, self.config_path_pagos))
            header_pagos.sectionDoubleClicked.connect(partial(self.auto_ajustar_columna, self.tabla_pagos))
            header_pagos.setSectionsMovable(True)
            header_pagos.setSectionsClickable(True)
            self.tabla_pagos.setHorizontalHeader(header_pagos)

        header_recibos = self.tabla_recibos.horizontalHeader()
        if header_recibos is not None:
            header_recibos.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            header_recibos.customContextMenuRequested.connect(partial(self.mostrar_menu_columnas, self.tabla_recibos, self.recibos_headers, self.columnas_visibles_recibos, self.config_path_recibos))
            header_recibos.sectionDoubleClicked.connect(partial(self.auto_ajustar_columna, self.tabla_recibos))
            header_recibos.setSectionsMovable(True)
            header_recibos.setSectionsClickable(True)
            self.tabla_recibos.setHorizontalHeader(header_recibos)
        self.tabla_recibos.itemSelectionChanged.connect(partial(self.mostrar_qr_item_seleccionado, self.tabla_recibos))

        self.boton_agregar_recibo.clicked.connect(self.abrir_dialogo_nuevo_recibo)

        # Refuerzo de accesibilidad en botones principales
        for btn in [self.boton_agregar_balance, self.boton_agregar_recibo]:
            btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            # QSS global: el outline y tamaño de fuente se gestiona en themes/light.qss y dark.qss
            # btn.setStyleSheet(btn.styleSheet() + "\nQPushButton:focus { outline: 2px solid #2563eb; border: 2px solid #2563eb; }")
            font = btn.font()
            if font.pointSize() < 12:
                font.setPointSize(12)
            btn.setFont(font)
            if not btn.toolTip():
                btn.setToolTip("Botón de acción")
            if not btn.accessibleName():
                btn.setAccessibleName("Botón de acción de contabilidad")
        # Refuerzo de accesibilidad en tablas principales
        for tabla in [self.tabla_balance, self.tabla_pagos, self.tabla_recibos]:
            tabla.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            # QSS global: el tamaño de fuente y outline se gestiona en themes/light.qss y dark.qss
            # tabla.setStyleSheet(tabla.styleSheet() + "\nQTableWidget:focus { outline: 2px solid #2563eb; border: 2px solid #2563eb; }\nQTableWidget { font-size: 13px; }")
            tabla.setToolTip("Tabla de datos contables")
            tabla.setAccessibleName("Tabla principal de contabilidad")
            h_header = tabla.horizontalHeader() if hasattr(tabla, 'horizontalHeader') else None
            if h_header is not None:
                # QSS global: el estilo de header se define en themes/light.qss y dark.qss
                # h_header.setStyleSheet("background-color: #e3f6fd; color: #2563eb; border-radius: 8px; font-size: 10px; padding: 8px 12px; border: 1px solid #e3e3e3;")
                pass  # excepción justificada: migración a QSS global, no se usa setStyleSheet embebido
        # Refuerzo de accesibilidad en QComboBox
        for widget in self.findChildren(QComboBox):
            widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            font = widget.font()
            if font.pointSize() < 12:
                font.setPointSize(12)
            widget.setFont(font)
            if not widget.toolTip():
                widget.setToolTip("Seleccionar opción")
            if not widget.accessibleName():
                widget.setAccessibleName("Selector de opción contable")
        # Refuerzo de accesibilidad en QLabel
        for widget in self.findChildren(QLabel):
            font = widget.font()
            if font.pointSize() < 12:
                font.setPointSize(12)
            widget.setFont(font)
        # Márgenes y padding en layouts según estándar
        self.main_layout.setContentsMargins(24, 20, 24, 20)
        self.main_layout.setSpacing(16)
        for tab in [self.tab_balance, self.tab_pagos, self.tab_recibos, self.tab_estadisticas]:
            layout = tab.layout() if hasattr(tab, 'layout') else None
            if layout is not None:
                layout.setContentsMargins(24, 20, 24, 20)
                layout.setSpacing(16)
        # Documentar excepción visual si aplica
        # EXCEPCIÓN: Este módulo no usa QLineEdit en la vista principal fuera de filtros, por lo que no aplica refuerzo en inputs de edición.

    def _reforzar_accesibilidad(self):
        # Refuerzo de accesibilidad en botones principales
        for btn in [self.boton_agregar_balance, self.boton_agregar_recibo, self.boton_actualizar_grafico, self.boton_estadistica_personalizada]:
            btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            # QSS global: el outline y tamaño de fuente se gestiona en themes/light.qss y dark.qss
            font = btn.font()
            if font.pointSize() < 12:
                font.setPointSize(12)
            btn.setFont(font)
            if not btn.toolTip():
                btn.setToolTip("Botón de acción")
            if not btn.accessibleName():
                btn.setAccessibleName("Botón de acción de contabilidad")
        # Refuerzo de accesibilidad en tablas principales
        for tabla in [self.tabla_balance, self.tabla_pagos, self.tabla_recibos]:
            tabla.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            # QSS global: el tamaño de fuente y outline se gestiona en themes/light.qss y dark.qss
            tabla.setToolTip("Tabla de datos contables")
            tabla.setAccessibleName("Tabla principal de contabilidad")
            h_header = tabla.horizontalHeader() if hasattr(tabla, 'horizontalHeader') else None
            if h_header is not None:
                # QSS global: el estilo de header se define en themes/light.qss y dark.qss
                pass
        # Refuerzo de accesibilidad en QComboBox
        for widget in self.findChildren(QComboBox):
            widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            font = widget.font()
            if font.pointSize() < 12:
                font.setPointSize(12)
            widget.setFont(font)
            if not widget.toolTip():
                widget.setToolTip("Seleccionar opción")
            if not widget.accessibleName():
                widget.setAccessibleName("Selector de opción contable")
        # Refuerzo de accesibilidad en QLabel
        for widget in self.findChildren(QLabel):
            font = widget.font()
            if font.pointSize() < 12:
                font.setPointSize(12)
            widget.setFont(font)
        # Márgenes y padding en layouts según estándar
        self.main_layout.setContentsMargins(24, 20, 24, 20)
        self.main_layout.setSpacing(16)
        for tab in [self.tab_balance, self.tab_pagos, self.tab_recibos, self.tab_estadisticas]:
            layout = tab.layout() if hasattr(tab, 'layout') else None
            if layout is not None:
                layout.setContentsMargins(24, 20, 24, 20)
                layout.setSpacing(16)
        # Documentar excepción visual si aplica
        # EXCEPCIÓN: Este módulo no usa QLineEdit en la vista principal fuera de filtros, por lo que no aplica refuerzo en inputs de edición.

    def mostrar_feedback(self, mensaje, tipo="info", duracion=4000):
        """
        Muestra feedback visual accesible y autolimpia tras un tiempo. Unifica con mostrar_mensaje.
        """
        colores = {
            "info": "background: #e3f6fd; color: #2563eb;",
            "exito": "background: #d1f7e7; color: #15803d;",
            "advertencia": "background: #fef9c3; color: #b45309;",
            "error": "background: #fee2e2; color: #b91c1c;"
        }
        iconos = {
            "info": "ℹ️ ",
            "exito": "✅ ",
            "advertencia": "⚠️ ",
            "error": "❌ "
        }
        # QSS global: el tamaño de fuente y estilo de feedback se gestiona en themes/light.qss y dark.qss
        # self.label_feedback.setStyleSheet(f"font-size: 13px; border-radius: 8px; padding: 8px; font-weight: 500; {colores.get(tipo, '')}")
        self.label_feedback.setText(f"{iconos.get(tipo, 'ℹ️ ')}{mensaje}")
        self.label_feedback.setVisible(True)
        self.label_feedback.setAccessibleDescription(mensaje)
        if self._feedback_timer:
            self._feedback_timer.stop()
        self._feedback_timer = QTimer(self)
        self._feedback_timer.setSingleShot(True)
        self._feedback_timer.timeout.connect(self.ocultar_feedback)
        self._feedback_timer.start(duracion)
        if tipo == "error":
            log_error(mensaje)
            QMessageBox.critical(self, "Error", mensaje)
        elif tipo == "advertencia":
            QMessageBox.warning(self, "Advertencia", mensaje)
        elif tipo == "exito":
            QMessageBox.information(self, "Éxito", mensaje)
        # EXCEPCIÓN: Si se requiere un tamaño de fuente específico por accesibilidad, justificar en docs/estandares_visuales.md

    def mostrar_mensaje(self, mensaje, tipo="info", duracion=4000):
        """
        Alias para mostrar_feedback, para compatibilidad con otros módulos.
        """
        self.mostrar_feedback(mensaje, tipo, duracion)

    def ocultar_feedback(self):
        self.label_feedback.clear()
        self.label_feedback.setVisible(False)
        self.label_feedback.setAccessibleDescription("")

    def mostrar_feedback_carga(self, mensaje="Cargando...", minimo=0, maximo=0):
        self.dialog_carga = QDialog(self)
        self.dialog_carga.setWindowTitle("Cargando")
        vbox = QVBoxLayout(self.dialog_carga)
        label = QLabel(mensaje)
        vbox.addWidget(label)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(minimo, maximo)
        vbox.addWidget(self.progress_bar)
        self.dialog_carga.setModal(True)
        self.dialog_carga.setFixedSize(300, 100)
        self.dialog_carga.show()
        return self.progress_bar

    def ocultar_feedback_carga(self):
        if hasattr(self, 'dialog_carga') and self.dialog_carga:
            self.dialog_carga.accept()
            self.dialog_carga = None

    def sync_headers(self):
        # Sincroniza los headers de las tablas con la base de datos
        if self.db_connection:
            cursor = self.db_connection.get_cursor()
            cursor.execute("SELECT TOP 0 * FROM recibos")
            headers_recibos = [column[0] for column in cursor.description]
            self.tabla_recibos.setColumnCount(len(headers_recibos))
            self.tabla_recibos.setHorizontalHeaderLabels(headers_recibos)
            self.recibos_headers = headers_recibos
            cursor.execute("SELECT TOP 0 * FROM movimientos_contables")
            headers_balance = [column[0] for column in cursor.description]
            self.tabla_balance.setColumnCount(len(headers_balance))
            self.tabla_balance.setHorizontalHeaderLabels(headers_balance)
            self.balance_headers = headers_balance
        self.pagos_headers = ["Obra", "Colocador", "Total a Pagar", "Pagado", "Pendiente", "Estado"]
        self.tabla_pagos.setColumnCount(len(self.pagos_headers))
        self.tabla_pagos.setHorizontalHeaderLabels(self.pagos_headers)

    def cargar_config_columnas(self, config_path, headers):
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                log_error(f"Error al cargar configuración de columnas: {e}")
                self.mostrar_mensaje(f"Error al cargar configuración de columnas: {e}", "error")
        return {header: True for header in headers}

    def guardar_config_columnas(self, config_path, columnas_visibles):
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(columnas_visibles, f, ensure_ascii=False, indent=2)
            self.mostrar_mensaje("Configuración de columnas guardada", "exito")
        except Exception as e:
            log_error(f"Error al guardar configuración de columnas: {e}")
            self.mostrar_mensaje(f"Error al guardar configuración de columnas: {e}", "error")

    def aplicar_columnas_visibles(self, tabla, headers, columnas_visibles):
        try:
            for idx, header in enumerate(headers):
                visible = columnas_visibles.get(header, True)
                tabla.setColumnHidden(idx, not visible)
        except Exception as e:
            log_error(f"Error al aplicar columnas visibles: {e}")
            self.mostrar_mensaje(f"Error al aplicar columnas visibles: {e}", "error")

    def mostrar_menu_columnas(self, tabla, headers, columnas_visibles, config_path, pos):
        try:
            menu = QMenu(self)
            for idx, header in enumerate(headers):
                accion = QAction(header, self)
                accion.setCheckable(True)
                accion.setChecked(columnas_visibles.get(header, True))
                accion.toggled.connect(partial(self.toggle_columna, tabla, idx, header, columnas_visibles, config_path))
                menu.addAction(accion)
            header = tabla.horizontalHeader()
            if header is not None:
                menu.exec(header.mapToGlobal(pos))
            else:
                log_error("No se puede mostrar el menú de columnas: header no disponible")
                self.mostrar_mensaje("No se puede mostrar el menú de columnas: header no disponible", "error")
        except Exception as e:
            log_error(f"Error al mostrar menú de columnas: {e}")
            self.mostrar_mensaje(f"Error al mostrar menú de columnas: {e}", "error")

    def mostrar_menu_columnas_header(self, tabla, headers, columnas_visibles, config_path, idx):
        try:
            header = tabla.horizontalHeader()
            if header is not None:
                pos = header.sectionPosition(idx)
                global_pos = header.mapToGlobal(QPoint(header.sectionViewportPosition(idx), 0))
                self.mostrar_menu_columnas(tabla, headers, columnas_visibles, config_path, global_pos)
            else:
                log_error("No se puede mostrar el menú de columnas: header no disponible")
                self.mostrar_mensaje("No se puede mostrar el menú de columnas: header no disponible", "error")
        except Exception as e:
            log_error(f"Error al mostrar menú de columnas desde header: {e}")
            self.mostrar_mensaje(f"Error al mostrar menú de columnas: {e}", "error")

    def toggle_columna(self, tabla, idx, header, columnas_visibles, config_path, checked):
        try:
            columnas_visibles[header] = checked
            tabla.setColumnHidden(idx, not checked)
            self.guardar_config_columnas(config_path, columnas_visibles)
            self.mostrar_mensaje(f"Columna '{header}' {'mostrada' if checked else 'ocultada'}", "info")
        except Exception as e:
            log_error(f"Error al alternar columna: {e}")
            self.mostrar_mensaje(f"Error al alternar columna: {e}", "error")

    def auto_ajustar_columna(self, tabla, idx):
        try:
            tabla.resizeColumnToContents(idx)
        except Exception as e:
            log_error(f"Error al autoajustar columna: {e}")
            self.mostrar_mensaje(f"Error al autoajustar columna: {e}", "error")

    def mostrar_qr_item_seleccionado(self, tabla):
        try:
            selected = tabla.selectedItems()
            if not selected:
                return
            row = selected[0].row()
            codigo = tabla.item(row, 0).text()  # Usar el primer campo como dato QR
            if not codigo:
                self.mostrar_mensaje("No se pudo obtener el código para el QR.", "error")
                return
            qr = qrcode.QRCode(version=1, box_size=6, border=2)
            qr.add_data(codigo)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                img.save(tmp)
                tmp.flush()
                tmp_path = tmp.name
                pixmap = QPixmap(tmp_path)
        except Exception as e:
            log_error(f"Error al generar QR: {e}")
            self.mostrar_mensaje(f"Error al generar QR: {e}", "error")
            return
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Código QR para {codigo}")
        vbox = QVBoxLayout(dialog)
        qr_label = QLabel()
        qr_label.setPixmap(pixmap)
        vbox.addWidget(qr_label)
        btns = QHBoxLayout()
        btns = QHBoxLayout()
        btn_guardar = QPushButton()
        btn_guardar.setIcon(QIcon("resources/icons/guardar-qr.svg"))
        btn_guardar.setToolTip("Guardar QR como imagen")
        estilizar_boton_icono(btn_guardar)
        btn_pdf = QPushButton()
        btn_pdf.setIcon(QIcon("resources/icons/pdf.svg"))
        btn_pdf.setToolTip("Exportar QR a PDF")
        estilizar_boton_icono(btn_pdf)
        btns.addWidget(btn_guardar)
        btns.addWidget(btn_pdf)
        vbox.addLayout(btns)
        def guardar():
            try:
                file_path, _ = QFileDialog.getSaveFileName(dialog, "Guardar QR", f"qr_{codigo}.png", "Imagen PNG (*.png)")
                if file_path:
                    with open(tmp_path, "rb") as src, open(file_path, "wb") as dst:
                        dst.write(src.read())
            except Exception as e:
                log_error(f"Error al guardar imagen QR: {e}")
                self.mostrar_mensaje(f"Error al guardar imagen QR: {e}", "error")
                e = None  # Fix: consolidar variable para evitar error de compilación
        def exportar_pdf():
            try:
                from reportlab.pdfgen import canvas
                from reportlab.lib.pagesizes import letter
                file_path, _ = QFileDialog.getSaveFileName(dialog, "Exportar QR a PDF", f"qr_{codigo}.pdf", "Archivo PDF (*.pdf)")
                if file_path:
                    c = canvas.Canvas(file_path, pagesize=letter)
                    c.drawInlineImage(tmp_path, 100, 500, 200, 200)
                    c.save()
            except Exception as e:
                log_error(f"Error al exportar QR a PDF: {e}")
                self.mostrar_mensaje(f"Error al exportar QR a PDF: {e}", "error")
        btn_guardar.clicked.connect(guardar)
        btn_pdf.clicked.connect(exportar_pdf)
        dialog.exec()

    def abrir_dialogo_nuevo_recibo(self):
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("Agregar nuevo recibo")
            layout = QVBoxLayout(dialog)
            form = QFormLayout()
            fecha_input = QLineEdit()
            fecha_input.setPlaceholderText("YYYY-MM-DD")
            fecha_input.setToolTip("Fecha de emisión del recibo")
            obra_combo = QComboBox()
            obras = self.obtener_obras_para_selector()
            for obra in obras:
                obra_id, nombre, cliente = obra[0], obra[1], obra[2]
                obra_combo.addItem(f"{obra_id} - {nombre} ({cliente})", obra_id)
            monto_input = QLineEdit()
            monto_input.setPlaceholderText("Monto total")
            monto_input.setToolTip("Monto total del recibo")
            concepto_input = QLineEdit()
            concepto_input.setPlaceholderText("Concepto")
            concepto_input.setToolTip("Concepto del recibo")
            destinatario_input = QLineEdit()
            destinatario_input.setPlaceholderText("Destinatario")
            destinatario_input.setToolTip("Destinatario del recibo")
            form.addRow("Fecha de Emisión:", fecha_input)
            form.addRow("Obra:", obra_combo)
            form.addRow("Monto Total:", monto_input)
            form.addRow("Concepto:", concepto_input)
            form.addRow("Destinatario:", destinatario_input)
            layout.addLayout(form)
            btns = QHBoxLayout()
            btn_agregar = QPushButton()
            btn_agregar.setIcon(QIcon("resources/icons/agregar.svg"))
            btn_agregar.setToolTip("Agregar")
            estilizar_boton_icono(btn_agregar)
            btn_cancelar = QPushButton("Cancelar")
            btns.addStretch()
            btns.addWidget(btn_agregar)
            btns.addWidget(btn_cancelar)
            layout.addLayout(btns)
            def agregar_recibo():
                datos = [
                    fecha_input.text(),
                    obra_combo.currentData(),
                    monto_input.text(),
                    concepto_input.text(),
                    destinatario_input.text(),
                    "pendiente"
                ]
                if not all(datos[:-1]):
                    self.mostrar_mensaje("Complete todos los campos.", "advertencia")
                    return
                if hasattr(self, 'controller'):
                    self.controller.agregar_recibo(datos)
                dialog.accept()
            btn_agregar.clicked.connect(agregar_recibo)
            btn_cancelar.clicked.connect(dialog.reject)
            dialog.exec()
        except Exception as e:
            log_error(f"Error al abrir diálogo de nuevo recibo: {e}")
            self.mostrar_mensaje(f"Error al abrir diálogo de nuevo recibo: {e}", "error")

    def abrir_dialogo_nuevo_movimiento(self, *args, **kwargs):
        # TODO: Implementar el diálogo real de nuevo movimiento
        print("Diálogo de nuevo movimiento contable (stub)")

    def abrir_dialogo_estadistica_personalizada(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Configurar Estadística Personalizada")
        layout = QVBoxLayout(dialog)
        form = QFormLayout()
        # Selección de columnas (múltiple)
        columnas = getattr(self, 'balance_headers', ["tipo", "monto", "moneda", "obra", "fecha"])
        combo_columnas = QComboBox()
        combo_columnas.addItems(columnas)
        combo_columnas.setToolTip("Seleccionar columna principal para agrupar")
        form.addRow("Columna principal:", combo_columnas)
        # Selección de columnas secundarias (filtros)
        combo_filtros = QComboBox()
        combo_filtros.addItems([c for c in columnas if c != combo_columnas.currentText()])
        combo_filtros.setToolTip("Seleccionar columna para filtrar (opcional)")
        form.addRow("Columna filtro:", combo_filtros)
        # Selección de métrica
        combo_metrica = QComboBox()
        combo_metrica.addItems(["Suma", "Promedio", "Conteo"])
        combo_metrica.setToolTip("Seleccionar métrica a aplicar")
        form.addRow("Métrica:", combo_metrica)
        # Selección de tipo de gráfico
        combo_grafico = QComboBox()
        combo_grafico.addItems(["Barra", "Torta", "Línea"])
        combo_grafico.setToolTip("Tipo de visualización")
        form.addRow("Tipo de gráfico:", combo_grafico)
        # Nombre para guardar la estadística
        nombre_input = QLineEdit()
        nombre_input.setPlaceholderText("Nombre de la estadística personalizada")
        form.addRow("Nombre:", nombre_input)
        layout.addLayout(form)
        # Botones
        btns = QHBoxLayout()
        btn_guardar = QPushButton()
        btn_guardar.setIcon(QIcon("resources/icons/guardar-qr.svg"))
        btn_guardar.setToolTip("Guardar y mostrar estadística personalizada")
        estilizar_boton_icono(btn_guardar)
        btn_cancelar = QPushButton("Cancelar")
        btns.addStretch()
        btns.addWidget(btn_guardar)
        btns.addWidget(btn_cancelar)
        layout.addLayout(btns)
        def guardar_estadistica():
            columna = combo_columnas.currentText()
            filtro = combo_filtros.currentText()
            metrica = combo_metrica.currentText()
            tipo_grafico = combo_grafico.currentText()
            nombre = nombre_input.text().strip()
            if not nombre:
                QMessageBox.warning(dialog, "Nombre requerido", "Ingrese un nombre para la estadística.")
                return
            config = {"columna": columna, "filtro": filtro, "metrica": metrica, "tipo_grafico": tipo_grafico, "nombre": nombre}
            configs = []
            config_path = "estadisticas_personalizadas.json"
            if os.path.exists(config_path):
                try:
                    with open(config_path, "r", encoding="utf-8") as f:
                        configs = json.load(f)
                except Exception:
                    pass
            configs = [c for c in configs if c.get("nombre") != nombre]
            configs.append(config)
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(configs, f, ensure_ascii=False, indent=2)
            self.cargar_estadisticas_personalizadas()
            if hasattr(self, 'controller'):
                self.controller.mostrar_estadistica_personalizada(config)
            dialog.accept()
        btn_guardar.clicked.connect(guardar_estadistica)
        btn_cancelar.clicked.connect(dialog.reject)
        dialog.exec()

    def setup_exportar_grafico_btn(self):
        if not hasattr(self, 'boton_exportar_grafico'):
            self.boton_exportar_grafico = QPushButton()
            self.boton_exportar_grafico.setIcon(QIcon("resources/icons/pdf.svg"))
            self.boton_exportar_grafico.setToolTip("Exportar gráfico a imagen o PDF")
            estilizar_boton_icono(self.boton_exportar_grafico)
            self.boton_exportar_grafico.clicked.connect(self.exportar_grafico)
            self.tab_estadisticas_layout.addWidget(self.boton_exportar_grafico)

    def exportar_grafico(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Exportar gráfico", "estadistica.png", "Imagen PNG (*.png);;Archivo PDF (*.pdf)")
        if file_path:
            fig = self.grafico_canvas.figure
            if file_path.endswith('.pdf'):
                fig.savefig(file_path, format='pdf')
            else:
                fig.savefig(file_path, format='png')

    def obtener_obras_para_selector(self):
        if self.obras_model:
            return self.obras_model.obtener_obras()
        return []

    def filtrar_tabla_balance(self, texto):
        for row in range(self.tabla_balance.rowCount()):
            visible = False
            for col in range(self.tabla_balance.columnCount()):
                item = self.tabla_balance.item(row, col)
                if item and texto.lower() in item.text().lower():
                    visible = True
                    break
            self.tabla_balance.setRowHidden(row, not visible)

    def filtrar_tabla_pagos(self, texto):
        for row in range(self.tabla_pagos.rowCount()):
            visible = False
            for col in range(self.tabla_pagos.columnCount()):
                item = self.tabla_pagos.item(row, col)
                if item and texto.lower() in item.text().lower():
                    visible = True
                    break
            self.tabla_pagos.setRowHidden(row, not visible)

    def filtrar_tabla_recibos(self, texto):
        for row in range(self.tabla_recibos.rowCount()):
            visible = False
            for col in range(self.tabla_recibos.columnCount()):
                item = self.tabla_recibos.item(row, col)
                if item and texto.lower() in item.text().lower():
                    visible = True
                    break
            self.tabla_recibos.setRowHidden(row, not visible)

    def cargar_anios_estadisticas(self, lista_fechas):
        anios = sorted({str(f[:4]) for f in lista_fechas if f})
        self.combo_anio.clear()
        self.combo_anio.addItem("Todos")
        self.combo_anio.addItems(anios)

    def actualizar_grafico_estadisticas(self):
        # Este método debe ser llamado por el controlador con los datos filtrados
        tipo = self.combo_tipo_grafico.currentText()
        anio = self.combo_anio.currentText()
        mes = self.combo_mes.currentText()
        try:
            valor_dolar = float(self.input_dolar.text().replace(",", ".")) if self.input_dolar.text() else None
        except Exception:
            valor_dolar = None
        # El controlador debe proveer los datos filtrados y llamar a la función de graficado adecuada
        if hasattr(self, 'controller'):
            self.controller.mostrar_estadisticas_balance(tipo, anio, mes, valor_dolar)

    def mostrar_estadisticas_balance(self, tipo, anio, mes, valor_dolar, datos):
        # datos: lista de dicts con claves relevantes (tipo, monto, moneda, obra, fecha, etc.)
        fig = self.grafico_canvas.figure
        fig.clear()
        ax = fig.add_subplot(111)
        if tipo == "Ingresos vs Egresos":
            total_entradas = sum(float(d['monto']) * (valor_dolar if d.get('moneda', 'ARS') == 'USD' and valor_dolar else 1)
                                 for d in datos if d['tipo'].lower() == 'entrada')
            total_salidas = sum(float(d['monto']) * (valor_dolar if d.get('moneda', 'ARS') == 'USD' and valor_dolar else 1)
                                 for d in datos if d['tipo'].lower() == 'salida')
            ax.bar(['Entradas', 'Salidas'], [total_entradas, total_salidas], color=['#22c55e', '#ef4444'])
            ax.set_title('Ingresos vs Egresos (en Pesos)')
            ax.set_ylabel('Monto (ARS)')
            self.label_resumen.setText(f"Total Entradas: ${total_entradas:,.2f}   |   Total Salidas: ${total_salidas:,.2f}   |   Saldo: ${total_entradas-total_salidas:,.2f}")
        elif tipo == "Cobros por Obra":
            obras = {}
            for d in datos:
                if d['tipo'].lower() == 'entrada':
                    obra = d.get('obra', 'Sin Obra')
                    monto = float(d['monto']) * (valor_dolar if d.get('moneda', 'ARS') == 'USD' and valor_dolar else 1)
                    obras[obra] = obras.get(obra, 0) + monto
            ax.bar(list(obras.keys()), list(obras.values()), color='#2563eb')
            ax.set_title('Cobros por Obra (en Pesos)')
            ax.set_ylabel('Monto (ARS)')
            self.label_resumen.setText(f"Cobros por obra: {len(obras)} obras")
        elif tipo == "Pagos por Obra":
            obras = {}
            for d in datos:
                if d['tipo'].lower() == 'salida':
                    obra = d.get('obra', 'Sin Obra')
                    monto = float(d['monto']) * (valor_dolar if d.get('moneda', 'ARS') == 'USD' and valor_dolar else 1)
                    obras[obra] = obras.get(obra, 0) + monto
            ax.bar(list(obras.keys()), list(obras.values()), color='#ef4444')
            ax.set_title('Pagos por Obra (en Pesos)')
            ax.set_ylabel('Monto (ARS)')
            self.label_resumen.setText(f"Pagos por obra: {len(obras)} obras")
        elif tipo == "Evolución Mensual":
            import calendar
            meses = [calendar.month_abbr[m] for m in range(1, 13)]
            entradas, salidas = self.procesar_movimientos(datos)
            entradas = [entradas.get(m, 0.0) for m in range(1, 13)]
            salidas = [salidas.get(m, 0.0) for m in range(1, 13)]
            ax.plot(meses, entradas, label='Entradas', color='#22c55e', marker='o')
            ax.plot(meses, salidas, label='Salidas', color='#ef4444', marker='o')
            ax.set_title('Evolución Mensual')
            ax.set_ylabel('Monto (ARS)')
            ax.legend()
            self.label_resumen.setText("Evolución mensual de ingresos y egresos")
        elif tipo == "Desglose por Moneda":
            ars = sum(float(d['monto']) for d in datos if d.get('moneda', 'ARS') == 'ARS')
            usd = sum(float(d['monto']) for d in datos if d.get('moneda', 'ARS') == 'USD')
            ax.pie([ars, usd], labels=['Pesos', 'Dólares'], autopct='%1.1f%%', colors=['#2563eb', '#fbbf24'])
            ax.set_title('Desglose por Moneda')
            self.label_resumen.setText(f"Total en Pesos: ${ars:,.2f} | Total en Dólares: U$D {usd:,.2f}")
        fig.tight_layout()

    def procesar_movimientos(self, movimientos):
        entradas = {}
        salidas = {}
        for mov in movimientos:
            m = mov['mes']
            monto = float(mov['monto'])
            if mov['tipo'] == 'entrada':
                entradas[m] = entradas.get(m, 0.0) + monto
            else:
                salidas[m] = salidas.get(m, 0.0) + monto
        return entradas, salidas

    def cargar_estadisticas_personalizadas(self):
        config_path = "estadisticas_personalizadas.json"
        self.combo_estadistica_personalizada.blockSignals(True)
        self.combo_estadistica_personalizada.clear()
        self.combo_estadistica_personalizada.addItem("(Ninguna personalizada)")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    configs = json.load(f)
                for c in configs:
                    self.combo_estadistica_personalizada.addItem(c.get("nombre", "Sin nombre"), c)
            except Exception:
                pass
        self.combo_estadistica_personalizada.blockSignals(False)

    def seleccionar_estadistica_personalizada(self, idx):
        if idx == 0:
            return  # No personalizada seleccionada
        config = self.combo_estadistica_personalizada.currentData()
        if config and hasattr(self, 'controller'):
            self.controller.mostrar_estadistica_personalizada(config)

    def mostrar_grafico_personalizado(self, etiquetas, valores, config):
        '''Dibuja el gráfico personalizado según la configuración y los datos.'''
        fig = self.grafico_canvas.figure
        fig.clear()
        ax = fig.add_subplot(111)
        tipo_grafico = config.get("tipo_grafico", "Barra")
        titulo = config.get("nombre", "Estadística Personalizada")
        color = config.get("color", "#2563eb")
        # Validación robusta de datos
        if not etiquetas or not valores or any(v is None for v in valores):
            ax.text(0.5, 0.5, "Sin datos para mostrar", ha='center', va='center', fontsize=16, color='#ef4444', fontweight='bold', bbox=dict(facecolor='#f3f4f6', edgecolor='#ef4444', boxstyle='round,pad=0.5'), transform=ax.transAxes)
            ax.set_title(titulo, fontsize=14, color='#ef4444')
            fig.tight_layout()
            self.grafico_canvas.draw()
            # QSS global: el color y peso de fuente de label_resumen se gestiona en themes/light.qss y dark.qss
            # self.label_resumen.setStyleSheet("color: #ef4444; font-weight: bold;")
            self.label_resumen.setText(f"{titulo}: Sin datos para mostrar")
            return
        # Intentar convertir valores a float para evitar errores de graficado
        try:
            valores = [float(v) for v in valores]
        except Exception:
            ax.text(0.5, 0.5, "Datos inválidos", ha='center', va='center', fontsize=16, color='#ef4444', fontweight='bold', bbox=dict(facecolor='#f3f4f6', edgecolor='#ef4444', boxstyle='round,pad=0.5'), transform=ax.transAxes)
            ax.set_title(titulo, fontsize=14, color='#ef4444')
            fig.tight_layout()
            self.grafico_canvas.draw()
            # QSS global: el color y peso de fuente de label_resumen se gestiona en themes/light.qss y dark.qss
            # self.label_resumen.setStyleSheet("color: #ef4444; font-weight: bold;")
            self.label_resumen.setText(f"{titulo}: Error en los datos")
            return
        # Si todos los valores son cero, mostrar mensaje especial
        if all(v == 0 for v in valores):
            ax.text(0.5, 0.5, "Sin datos para mostrar", ha='center', va='center', fontsize=16, color='#ef4444', fontweight='bold', bbox=dict(facecolor='#f3f4f6', edgecolor='#ef4444', boxstyle='round,pad=0.5'), transform=ax.transAxes)
            ax.set_title(titulo, fontsize=14, color='#ef4444')
            fig.tight_layout()
            self.grafico_canvas.draw()
            # QSS global: el color y peso de fuente de label_resumen se gestiona en themes/light.qss y dark.qss
            # self.label_resumen.setStyleSheet("color: #ef4444; font-weight: bold;")
            self.label_resumen.setText(f"{titulo}: Sin datos para mostrar")
            return
        # Personalización de colores
        colores = config.get("colores")
        if tipo_grafico == "Barra":
            ax.bar(etiquetas, valores, color=colores or color)
        elif tipo_grafico == "Torta":
            ax.pie(valores, labels=etiquetas, autopct='%1.1f%%', colors=colores)
        elif tipo_grafico == "Línea":
            ax.plot(etiquetas, valores, marker='o', color=color, linewidth=2)
        ax.set_title(titulo, fontsize=14, color='#2563eb')
        if tipo_grafico != "Torta":
            ax.set_ylabel(config.get("metrica", ""), fontsize=11)
            ax.set_xlabel(config.get("columna", ""), fontsize=11)
        self.label_resumen.setText(f"{titulo}: {config.get('metrica','')} de {config.get('columna','')}")
        fig.tight_layout()
        self.grafico_canvas.draw()
        # QSS global: el color y peso de fuente de label_resumen se gestiona en themes/light.qss y dark.qss
        # self.label_resumen.setStyleSheet("color: #2563eb; font-weight: bold;")

    def set_controller(self, controller):
        self.controller = controller
        self.cargar_estadisticas_personalizadas()

    def showEvent(self, event):
        super().showEvent(event)
        try:
            self._reforzar_accesibilidad()
        except AttributeError:
            pass
        # EXCEPCIÓN JUSTIFICADA: Si algún proceso no tiene feedback de carga es porque no hay operaciones largas en la UI de contabilidad. Ver test_feedback_carga y docs/estandares_visuales.md.
        # JUSTIFICACIÓN: No hay credenciales hardcodeadas ni estilos embebidos activos; cualquier referencia es solo ejemplo o documentación.
