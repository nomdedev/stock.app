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
        self.boton_agregar.setIcon(QIcon("img/add-material.svg"))
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
        self.boton_agregar_balance.setIcon(QIcon("img/plus_icon.svg"))
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
        self.boton_agregar_recibo.setIcon(QIcon("img/plus_icon.svg"))
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
        self.boton_actualizar_grafico.setIcon(QIcon("img/actualizar.svg"))
        self.boton_actualizar_grafico.setToolTip("Actualizar gráfico")
        estilizar_boton_icono(self.boton_actualizar_grafico)
        controles_layout.addWidget(self.boton_actualizar_grafico)
        self.boton_estadistica_personalizada = QPushButton()
        self.boton_estadistica_personalizada.setIcon(QIcon("img/estadistica.svg"))
        self.boton_estadistica_personalizada.setToolTip("Estadística Personalizada")
        estilizar_boton_icono(self.boton_estadistica_personalizada)
        controles_layout.addWidget(self.boton_estadistica_personalizada)
        self.boton_exportar_excel_recibos.setAccessibleName("Botón exportar recibos a Excel")ersonalizada)
        estilizar_boton_icono(self.boton_exportar_excel_recibos)
        btn_recibos_layout.addWidget(self.boton_exportar_excel_recibos)
        self.tab_recibos_layout.addLayout(btn_recibos_layout)ccionar estadística personalizada guardada")
        self.tabs.addTab(self.tab_recibos, "Recibos")"(Ninguna personalizada)")
        self.combo_estadistica_personalizada.currentIndexChanged.connect(self.seleccionar_estadistica_personalizada)
        # --- Pestaña Estadísticas ---bel("Personalizada:"))
        self.tab_estadisticas = QWidget()ombo_estadistica_personalizada)
        self.tab_estadisticas_layout = QVBoxLayout()oles_layout)
        self.tab_estadisticas.setLayout(self.tab_estadisticas_layout)
        self.label_resumen = QLabel("Resumen de Balance")co_canvas)
        self.tab_estadisticas_layout.addWidget(self.label_resumen)
        # Controles para filtros y tipo de gráficostadísticas")
        controles_layout = QHBoxLayout()
        self.combo_tipo_grafico = QComboBox()
        self.combo_tipo_grafico.addItems([ked.connect(self.actualizar_grafico_estadisticas)
            "Ingresos vs Egresos", "Cobros por Obra", "Pagos por Obra", "Evolución Mensual", "Desglose por Moneda"
        ])lf.combo_anio.currentIndexChanged.connect(self.actualizar_grafico_estadisticas)
        self.combo_tipo_grafico.setToolTip("Seleccionar tipo de gráfico estadístico")as)
        controles_layout.addWidget(QLabel("Tipo de gráfico:"))ar_grafico_estadisticas)
        controles_layout.addWidget(self.combo_tipo_grafico)
        self.combo_anio = QComboBox()ut)
        self.combo_anio.setToolTip("Año a analizar")
        controles_layout.addWidget(QLabel("Año:"))LOBAL ---
        controles_layout.addWidget(self.combo_anio)
        self.combo_mes = QComboBox()tName("label_feedback")
        self.combo_mes.addItems(["Todos"] + [str(m) for m in range(1, 13)])leSheet embebido
        self.combo_mes.setToolTip("Mes a analizar")
        controles_layout.addWidget(QLabel("Mes:"))saje de feedback de contabilidad")
        controles_layout.addWidget(self.combo_mes)on("Mensaje de feedback visual y accesible para el usuario")
        self.input_dolar = QLineEdit()f.label_feedback)
        self.input_dolar.setPlaceholderText("Valor dólar oficial")
        self.input_dolar.setToolTip("Ingrese el valor del dólar para conversión")
        controles_layout.addWidget(QLabel("Dólar:"))
        controles_layout.addWidget(self.input_dolar)
        self.boton_actualizar_grafico = QPushButton()
        self.boton_actualizar_grafico.setIcon(QIcon("resources/icons/actualizar.svg"))
        self.boton_actualizar_grafico.setToolTip("Actualizar gráfico")
        estilizar_boton_icono(self.boton_actualizar_grafico)ance_columns.json"
        controles_layout.addWidget(self.boton_actualizar_grafico)mns.json"
        self.boton_estadistica_personalizada = QPushButton()ibos_columns.json"
        self.boton_estadistica_personalizada.setIcon(QIcon("resources/icons/estadistica.svg")) self.balance_headers)
        self.boton_estadistica_personalizada.setToolTip("Estadística Personalizada")pagos, self.pagos_headers)
        estilizar_boton_icono(self.boton_estadistica_personalizada)s(self.config_path_recibos, self.recibos_headers)
        controles_layout.addWidget(self.boton_estadistica_personalizada)headers, self.columnas_visibles_balance)
        self.boton_estadistica_personalizada.clicked.connect(self.abrir_dialogo_estadistica_personalizada)
        # Combo para estadísticas personalizadasa_recibos, self.recibos_headers, self.columnas_visibles_recibos)
        self.combo_estadistica_personalizada = QComboBox()
        self.combo_estadistica_personalizada.setToolTip("Seleccionar estadística personalizada guardada")
        self.combo_estadistica_personalizada.addItem("(Ninguna personalizada)")tabla_balance, 'horizontalHeader') else None
        self.combo_estadistica_personalizada.currentIndexChanged.connect(self.seleccionar_estadistica_personalizada)
        controles_layout.addWidget(QLabel("Personalizada:"))'):
        controles_layout.addWidget(self.combo_estadistica_personalizada).CustomContextMenu)
        self.tab_estadisticas_layout.addLayout(controles_layout)ed'):
        self.grafico_canvas = FigureCanvas(Figure(figsize=(6, 4)))partial(self.mostrar_menu_columnas, self.tabla_balance, self.balance_headers, self.columnas_visibles_balance, self.config_path_balance))
        self.tab_estadisticas_layout.addWidget(self.grafico_canvas)
        self.setup_exportar_grafico_btn()bleClicked.connect(partial(self.auto_ajustar_columna, self.tabla_balance))
        self.tabs.addTab(self.tab_estadisticas, "Estadísticas")
                header_balance.setSectionsMovable(True)
        # Señales para actualizar el gráficoectionsClickable'):
        self.boton_actualizar_grafico.clicked.connect(self.actualizar_grafico_estadisticas)
        self.combo_tipo_grafico.currentIndexChanged.connect(self.actualizar_grafico_estadisticas)
        self.combo_anio.currentIndexChanged.connect(self.actualizar_grafico_estadisticas)header, self.tabla_balance, self.balance_headers, self.columnas_visibles_balance, self.config_path_balance))
        self.combo_mes.currentIndexChanged.connect(self.actualizar_grafico_estadisticas)
        self.input_dolar.editingFinished.connect(self.actualizar_grafico_estadisticas)
        self.setLayout(self.main_layout)ader es None, no se puede aplicar menú contextual ni acciones de header.
            # Documentar en docs/estandares_visuales.md si ocurre en producción.
        # --- FEEDBACK VISUAL CENTRALIZADO Y QSS GLOBAL ---
        self.label_feedback = QLabel()
        self.label_feedback.setObjectName("label_feedback")
        self.label_feedback.setVisible(False)
        self.label_feedback.setAccessibleName("Feedback visual de Contabilidad")Menu)
        self.label_feedback.setAccessibleDescription("Mensaje de feedback visual y accesible para el usuario en Contabilidad")eaders, self.columnas_visibles_pagos, self.config_path_pagos))
        self.main_layout.addWidget(self.label_feedback)artial(self.auto_ajustar_columna, self.tabla_pagos))
        self._feedback_timer = NonesMovable(True)
        # --- FIN FEEDBACK VISUAL GLOBAL ---e(True)
            self.tabla_pagos.setHorizontalHeader(header_pagos)
        # --- Sincronización dinámica de headers ---
        self.sync_headers()lf.tabla_recibos.horizontalHeader()
        if header_recibos is not None:
        # Configuración de columnas y persistencia para cada tablacy.CustomContextMenu)
        self.config_path_balance = f"config_contabilidad_balance_columns.json"trar_menu_columnas, self.tabla_recibos, self.recibos_headers, self.columnas_visibles_recibos, self.config_path_recibos))
        self.config_path_pagos = f"config_contabilidad_pagos_columns.json"ajustar_columna, self.tabla_recibos))
        self.config_path_recibos = f"config_contabilidad_recibos_columns.json"
        self.columnas_visibles_balance = self.cargar_config_columnas(self.config_path_balance, self.balance_headers)
        self.columnas_visibles_pagos = self.cargar_config_columnas(self.config_path_pagos, self.pagos_headers)
        self.columnas_visibles_recibos = self.cargar_config_columnas(self.config_path_recibos, self.recibos_headers)s))
        self.aplicar_columnas_visibles(self.tabla_balance, self.balance_headers, self.columnas_visibles_balance)
        self.aplicar_columnas_visibles(self.tabla_pagos, self.pagos_headers, self.columnas_visibles_pagos)
        self.aplicar_columnas_visibles(self.tabla_recibos, self.recibos_headers, self.columnas_visibles_recibos)
        # Refuerzo de accesibilidad en botones principales
        # Menú de columnas y QR para cada tabla self.boton_agregar_recibo]:
        header_balance = self.tabla_balance.horizontalHeader() if hasattr(self.tabla_balance, 'horizontalHeader') else None
        if header_balance is not None: tamaño de fuente se gestiona en themes/light.qss y dark.qss
            if hasattr(header_balance, 'setContextMenuPolicy'):on:focus { outline: 2px solid #2563eb; border: 2px solid #2563eb; }")
                header_balance.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            if hasattr(header_balance, 'customContextMenuRequested'):
                header_balance.customContextMenuRequested.connect(partial(self.mostrar_menu_columnas, self.tabla_balance, self.balance_headers, self.columnas_visibles_balance, self.config_path_balance))
            if hasattr(header_balance, 'sectionDoubleClicked'):
                header_balance.sectionDoubleClicked.connect(partial(self.auto_ajustar_columna, self.tabla_balance))
            if hasattr(header_balance, 'setSectionsMovable'):
                header_balance.setSectionsMovable(True)
            if hasattr(header_balance, 'setSectionsClickable'):bilidad")
                header_balance.setSectionsClickable(True)
            if hasattr(header_balance, 'sectionClicked'):s, self.tabla_recibos]:
                header_balance.sectionClicked.connect(partial(self.mostrar_menu_columnas_header, self.tabla_balance, self.balance_headers, self.columnas_visibles_balance, self.config_path_balance))
            self.tabla_balance.setHorizontalHeader(header_balance)a en themes/light.qss y dark.qss
        else: tabla.setStyleSheet(tabla.styleSheet() + "\nQTableWidget:focus { outline: 2px solid #2563eb; border: 2px solid #2563eb; }\nQTableWidget { font-size: 13px; }")
            # EXCEPCIÓN VISUAL: Si el header es None, no se puede aplicar menú contextual ni acciones de header.
            # Documentar en docs/estandares_visuales.md si ocurre en producción.
            passader = tabla.horizontalHeader() if hasattr(tabla, 'horizontalHeader') else None
            if h_header is not None:
        header_pagos = self.tabla_pagos.horizontalHeader()e en themes/light.qss y dark.qss
        if header_pagos is not None:heet("background-color: #e3f6fd; color: #2563eb; border-radius: 8px; font-size: 10px; padding: 8px 12px; border: 1px solid #e3e3e3;")
            header_pagos.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)tyleSheet embebido
            header_pagos.customContextMenuRequested.connect(partial(self.mostrar_menu_columnas, self.tabla_pagos, self.pagos_headers, self.columnas_visibles_pagos, self.config_path_pagos))
            header_pagos.sectionDoubleClicked.connect(partial(self.auto_ajustar_columna, self.tabla_pagos))
            header_pagos.setSectionsMovable(True)StrongFocus)
            header_pagos.setSectionsClickable(True)
            self.tabla_pagos.setHorizontalHeader(header_pagos)
                font.setPointSize(12)
        header_recibos = self.tabla_recibos.horizontalHeader()
        if header_recibos is not None:
            header_recibos.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            header_recibos.customContextMenuRequested.connect(partial(self.mostrar_menu_columnas, self.tabla_recibos, self.recibos_headers, self.columnas_visibles_recibos, self.config_path_recibos))
            header_recibos.sectionDoubleClicked.connect(partial(self.auto_ajustar_columna, self.tabla_recibos))
            header_recibos.setSectionsMovable(True)
            header_recibos.setSectionsClickable(True)
            self.tabla_recibos.setHorizontalHeader(header_recibos)
        self.tabla_recibos.itemSelectionChanged.connect(partial(self.mostrar_qr_item_seleccionado, self.tabla_recibos))
                font.setPointSize(12)
        self.boton_agregar_recibo.clicked.connect(self.abrir_dialogo_nuevo_recibo)
        # Márgenes y padding en layouts según estándar
        # Refuerzo de accesibilidad en botones principales)
        for btn in [self.boton_agregar_balance, self.boton_agregar_recibo, self.boton_actualizar_grafico, self.boton_estadistica_personalizada]:
            btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus).tab_recibos, self.tab_estadisticas]:
            font = btn.font()ut() if hasattr(tab, 'layout') else None
            if font.pointSize() < 12:
                font.setPointSize(12)gins(24, 20, 24, 20)
            btn.setFont(font)cing(16)
            if not btn.toolTip():sual si aplica
                btn.setToolTip("Botón de acción") en la vista principal fuera de filtros, por lo que no aplica refuerzo en inputs de edición.
            # Nombres accesibles más descriptivos
            if btn is self.boton_agregar_balance:
                btn.setAccessibleName("Botón agregar movimiento contable")
            elif btn is self.boton_agregar_recibo:lf.boton_agregar_recibo, self.boton_actualizar_grafico, self.boton_estadistica_personalizada]:
                btn.setAccessibleName("Botón agregar recibo de contabilidad")
            elif btn is self.boton_actualizar_grafico:e se gestiona en themes/light.qss y dark.qss
                btn.setAccessibleName("Botón actualizar gráfico de estadísticas")
            elif btn is self.boton_estadistica_personalizada:
                btn.setAccessibleName("Botón estadística personalizada de contabilidad")
            else:etFont(font)
                btn.setAccessibleName("Botón de acción de contabilidad")
        # Refuerzo de accesibilidad en tablas principales
        for tabla, nombre in zip([self.tabla_balance, self.tabla_pagos, self.tabla_recibos],
                                 ["Tabla de balance contable", "Tabla de pagos contables", "Tabla de recibos contables"]):
            tabla.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            tabla.setToolTip(nombre)ance, self.tabla_pagos, self.tabla_recibos]:
            tabla.setAccessibleName(nombre)licy.StrongFocus)
            h_header = tabla.horizontalHeader() if hasattr(tabla, 'horizontalHeader') else Noneqss
            if h_header is not None:de datos contables")
                # QSS global: el estilo de header se define en themes/light.qss y dark.qss
                # h_header.setStyleSheet("background-color: #e3f6fd; color: #2563eb; border-radius: 8px; font-size: 10px; padding: 8px 12px; border: 1px solid #e3e3e3;")
                pass  # excepción justificada: migración a QSS global, no se usa setStyleSheet embebido
        # Refuerzo de accesibilidad en QComboBoxr se define en themes/light.qss y dark.qss
        for widget in self.findChildren(QComboBox):
            widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            font = widget.font()hildren(QComboBox):
            if font.pointSize() < 12:FocusPolicy.StrongFocus)
                font.setPointSize(12)
            widget.setFont(font)< 12:
            if not widget.toolTip():)
                widget.setToolTip("Seleccionar opción")
            if not widget.accessibleName():
                widget.setAccessibleName("Selector de opción contable")
        # Refuerzo de accesibilidad en QLabel
        for widget in self.findChildren(QLabel):or de opción contable")
            font = widget.font()dad en QLabel
            if font.pointSize() < 12:en(QLabel):
                font.setPointSize(12)
            widget.setFont(font)< 12:
            if not widget.accessibleDescription():
                widget.setAccessibleDescription("Label informativo o de feedback en Contabilidad")
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

    def _reforzar_accesibilidad(self):, tipo="info", duracion=4000):
        # Refuerzo de accesibilidad en botones principales
        for btn in [self.boton_agregar_balance, self.boton_agregar_recibo, self.boton_actualizar_grafico, self.boton_estadistica_personalizada]:
            btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            # QSS global: el outline y tamaño de fuente se gestiona en themes/light.qss y dark.qss
            font = btn.font()nd: #e3f6fd; color: #2563eb;",
            if font.pointSize() < 12:f7e7; color: #15803d;",
                font.setPointSize(12)d: #fef9c3; color: #b45309;",
            btn.setFont(font)und: #fee2e2; color: #b91c1c;"
            if not btn.toolTip():
                btn.setToolTip("Botón de acción")
            # Nombres accesibles más descriptivos
            if btn is self.boton_agregar_balance:
                btn.setAccessibleName("Botón agregar movimiento contable")
            elif btn is self.boton_agregar_recibo:
                btn.setAccessibleName("Botón agregar recibo de contabilidad")
            elif btn is self.boton_actualizar_grafico:feedback se gestiona en themes/light.qss y dark.qss
                btn.setAccessibleName("Botón actualizar gráfico de estadísticas"); padding: 8px; font-weight: 500; {colores.get(tipo, '')}")
            elif btn is self.boton_estadistica_personalizada:)}{mensaje}")
                btn.setAccessibleName("Botón estadística personalizada de contabilidad")
            else:l_feedback.setAccessibleDescription(mensaje)
                btn.setAccessibleName("Botón de acción de contabilidad")
        # Refuerzo de accesibilidad en tablas principales
        for tabla, nombre in zip([self.tabla_balance, self.tabla_pagos, self.tabla_recibos],
                                 ["Tabla de balance contable", "Tabla de pagos contables", "Tabla de recibos contables"]):
            tabla.setFocusPolicy(Qt.FocusPolicy.StrongFocus)edback)
            tabla.setToolTip(nombre)uracion)
            tabla.setAccessibleName(nombre)
            h_header = tabla.horizontalHeader() if hasattr(tabla, 'horizontalHeader') else None
            if h_header is not None:f, "Error", mensaje)
                # QSS global: el estilo de header se define en themes/light.qss y dark.qss
                passBox.warning(self, "Advertencia", mensaje)
        # Refuerzo de accesibilidad en QComboBox
        for widget in self.findChildren(QComboBox):mensaje)
            widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)ífico por accesibilidad, justificar en docs/estandares_visuales.md
            font = widget.font()
            if font.pointSize() < 12:, tipo="info", duracion=4000):
                font.setPointSize(12)
            widget.setFont(font)ack, para compatibilidad con otros módulos.
            if not widget.toolTip():
                widget.setToolTip("Seleccionar opción")
            if not widget.accessibleName():
                widget.setAccessibleName("Selector de opción contable")
        # Refuerzo de accesibilidad en QLabel
        for widget in self.findChildren(QLabel):
            font = widget.font()ccessibleDescription("")
            if font.pointSize() < 12:
                font.setPointSize(12)mensaje="Cargando...", minimo=0, maximo=0):
            widget.setFont(font)log(self)
            if not widget.accessibleDescription():")
                widget.setAccessibleDescription("Label informativo o de feedback en Contabilidad")
        # Márgenes y padding en layouts según estándar
        self.main_layout.setContentsMargins(24, 20, 24, 20)
        self.main_layout.setSpacing(16)r()
        for tab in [self.tab_balance, self.tab_pagos, self.tab_recibos, self.tab_estadisticas]:
            layout = tab.layout() if hasattr(tab, 'layout') else None
            if layout is not None:(True)
                layout.setContentsMargins(24, 20, 24, 20)
                layout.setSpacing(16)
        # Documentar excepción visual si aplica
        # EXCEPCIÓN: Este módulo no usa QLineEdit en la vista principal fuera de filtros, por lo que no aplica refuerzo en inputs de edición.
    def ocultar_feedback_carga(self):
    def mostrar_feedback(self, mensaje, tipo="info", duracion=4000):
        """ self.dialog_carga.accept()
        Muestra feedback visual accesible y autolimpia tras un tiempo. Unifica con mostrar_mensaje.
        """
        colores = {s(self):
            "info": "background: #e3f6fd; color: #2563eb;",de datos
            "exito": "background: #d1f7e7; color: #15803d;",
            "advertencia": "background: #fef9c3; color: #b45309;",
            "error": "background: #fee2e2; color: #b91c1c;"
        }   headers_recibos = [column[0] for column in cursor.description]
        iconos = {abla_recibos.setColumnCount(len(headers_recibos))
            "info": "ℹ️ ",ibos.setHorizontalHeaderLabels(headers_recibos)
            "exito": "✅ ",eaders = headers_recibos
            "advertencia": "⚠️ ",T TOP 0 * FROM movimientos_contables")
            "error": "❌ "ce = [column[0] for column in cursor.description]
        }   self.tabla_balance.setColumnCount(len(headers_balance))
        # QSS global: el tamaño de fuente y estilo de feedback se gestiona en themes/light.qss y dark.qss
        # self.label_feedback.setStyleSheet(f"font-size: 13px; border-radius: 8px; padding: 8px; font-weight: 500; {colores.get(tipo, '')}")
        self.label_feedback.setText(f"{iconos.get(tipo, 'ℹ️ ')}{mensaje}")o", "Pendiente", "Estado"]
        self.label_feedback.setVisible(True)self.pagos_headers))
        self.label_feedback.setAccessibleDescription(mensaje)_headers)
        if self._feedback_timer:
            self._feedback_timer.stop()nfig_path, headers):
        self._feedback_timer = QTimer(self)
        self._feedback_timer.setSingleShot(True)
        self._feedback_timer.timeout.connect(self.ocultar_feedback)
        self._feedback_timer.start(duracion)
        if tipo == "error":n as e:
            log_error(mensaje)ror al cargar configuración de columnas: {e}")
            QMessageBox.critical(self, "Error", mensaje)onfiguración de columnas: {e}", "error")
        elif tipo == "advertencia":ader in headers}
            QMessageBox.warning(self, "Advertencia", mensaje)
        elif tipo == "exito":as(self, config_path, columnas_visibles):
            QMessageBox.information(self, "Éxito", mensaje)
        # EXCEPCIÓN: Si se requiere un tamaño de fuente específico por accesibilidad, justificar en docs/estandares_visuales.md
                json.dump(columnas_visibles, f, ensure_ascii=False, indent=2)
    def mostrar_mensaje(self, mensaje, tipo="info", duracion=4000):a", "exito")
        """ept Exception as e:
        Alias para mostrar_feedback, para compatibilidad con otros módulos.
        """ self.mostrar_mensaje(f"Error al guardar configuración de columnas: {e}", "error")
        self.mostrar_feedback(mensaje, tipo, duracion)
    def aplicar_columnas_visibles(self, tabla, headers, columnas_visibles):
    def ocultar_feedback(self):
        self.label_feedback.clear()erate(headers):
        self.label_feedback.setVisible(False)et(header, True)
        self.label_feedback.setAccessibleDescription("")
        except Exception as e:
    def mostrar_feedback_carga(self, mensaje="Cargando...", minimo=0, maximo=0):
        self.dialog_carga = QDialog(self)al aplicar columnas visibles: {e}", "error")
        self.dialog_carga.setWindowTitle("Cargando")
        vbox = QVBoxLayout(self.dialog_carga)aders, columnas_visibles, config_path, pos):
        label = QLabel(mensaje)
        vbox.addWidget(label))
        self.progress_bar = QProgressBar()eaders):
        self.progress_bar.setRange(minimo, maximo)
        vbox.addWidget(self.progress_bar)
        self.dialog_carga.setModal(True)as_visibles.get(header, True))
        self.dialog_carga.setFixedSize(300, 100)elf.toggle_columna, tabla, idx, header, columnas_visibles, config_path))
        self.dialog_carga.show()ccion)
        return self.progress_barontalHeader()
            if header is not None:
    def ocultar_feedback_carga(self):oGlobal(pos))
        if hasattr(self, 'dialog_carga') and self.dialog_carga:
            self.dialog_carga.accept() mostrar el menú de columnas: header no disponible")
            self.dialog_carga = None("No se puede mostrar el menú de columnas: header no disponible", "error")
        except Exception as e:
    def sync_headers(self):or al mostrar menú de columnas: {e}")
        # Sincroniza los headers de las tablas con la base de datoss: {e}", "error")
        if self.db_connection:
            cursor = self.db_connection.get_cursor()aders, columnas_visibles, config_path, idx):
            cursor.execute("SELECT TOP 0 * FROM recibos")
            headers_recibos = [column[0] for column in cursor.description]
            self.tabla_recibos.setColumnCount(len(headers_recibos))
            self.tabla_recibos.setHorizontalHeaderLabels(headers_recibos)
            self.recibos_headers = headers_recibosoint(header.sectionViewportPosition(idx), 0))
            cursor.execute("SELECT TOP 0 * FROM movimientos_contables")ibles, config_path, global_pos)
            headers_balance = [column[0] for column in cursor.description]
            self.tabla_balance.setColumnCount(len(headers_balance)) header no disponible")
            self.tabla_balance.setHorizontalHeaderLabels(headers_balance)mnas: header no disponible", "error")
            self.balance_headers = headers_balance
        self.pagos_headers = ["Obra", "Colocador", "Total a Pagar", "Pagado", "Pendiente", "Estado"]
        self.tabla_pagos.setColumnCount(len(self.pagos_headers))mnas: {e}", "error")
        self.tabla_pagos.setHorizontalHeaderLabels(self.pagos_headers)
    def toggle_columna(self, tabla, idx, header, columnas_visibles, config_path, checked):
    def cargar_config_columnas(self, config_path, headers):
        if os.path.exists(config_path): checked
            try:a.setColumnHidden(idx, not checked)
                with open(config_path, "r", encoding="utf-8") as f:bles)
                    return json.load(f)mna '{header}' {'mostrada' if checked else 'ocultada'}", "info")
            except Exception as e:
                log_error(f"Error al cargar configuración de columnas: {e}")
                self.mostrar_mensaje(f"Error al cargar configuración de columnas: {e}", "error")
        return {header: True for header in headers}
    def auto_ajustar_columna(self, tabla, idx):
    def guardar_config_columnas(self, config_path, columnas_visibles):
        try:tabla.resizeColumnToContents(idx)
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(columnas_visibles, f, ensure_ascii=False, indent=2)
            self.mostrar_mensaje("Configuración de columnas guardada", "exito")
        except Exception as e:
            log_error(f"Error al guardar configuración de columnas: {e}")
            self.mostrar_mensaje(f"Error al guardar configuración de columnas: {e}", "error")
            selected = tabla.selectedItems()
    def aplicar_columnas_visibles(self, tabla, headers, columnas_visibles):
        try:    return
            for idx, header in enumerate(headers):
                visible = columnas_visibles.get(header, True)mer campo como dato QR
                tabla.setColumnHidden(idx, not visible)
        except Exception as e:ensaje("No se pudo obtener el código para el QR.", "error")
            log_error(f"Error al aplicar columnas visibles: {e}")
            self.mostrar_mensaje(f"Error al aplicar columnas visibles: {e}", "error")
            qr.add_data(codigo)
    def mostrar_menu_columnas(self, tabla, headers, columnas_visibles, config_path, pos):
        try:img = qr.make_image(fill_color="black", back_color="white")
            menu = QMenu(self)dTemporaryFile(suffix=".png", delete=False) as tmp:
            for idx, header in enumerate(headers):
                accion = QAction(header, self)
                accion.setCheckable(True)
                accion.setChecked(columnas_visibles.get(header, True))
                accion.toggled.connect(partial(self.toggle_columna, tabla, idx, header, columnas_visibles, config_path))
                menu.addAction(accion)ar QR: {e}")
            header = tabla.horizontalHeader()enerar QR: {e}", "error")
            if header is not None:
                menu.exec(header.mapToGlobal(pos))
            else:tWindowTitle(f"Código QR para {codigo}")
                log_error("No se puede mostrar el menú de columnas: header no disponible")
                self.mostrar_mensaje("No se puede mostrar el menú de columnas: header no disponible", "error")
        except Exception as e:map)
            log_error(f"Error al mostrar menú de columnas: {e}")
            self.mostrar_mensaje(f"Error al mostrar menú de columnas: {e}", "error")
        btns = QHBoxLayout()
    def mostrar_menu_columnas_header(self, tabla, headers, columnas_visibles, config_path, idx):
        from PyQt6.QtCore import QPointguardar-qr.svg"))
        try:guardar.setToolTip("Guardar QR como imagen")
            header = tabla.horizontalHeader()
            if header is not None and all(hasattr(header, m) for m in ['sectionPosition', 'mapToGlobal', 'sectionViewportPosition']):
                if idx < 0 or idx >= tabla.columnCount():
                    self.mostrar_mensaje("Índice de columna fuera de rango", "error")
                    returnono(btn_pdf)
                pos = header.sectionPosition(idx)
                global_pos = header.mapToGlobal(QPoint(header.sectionViewportPosition(idx), 0))
                self.mostrar_menu_columnas(tabla, headers, columnas_visibles, config_path, global_pos)
            else:ar():
                log_error("No se puede mostrar el menú de columnas: header no disponible o incompleto")
                self.mostrar_mensaje("No se puede mostrar el menú de columnas: header no disponible o incompleto", "error")
        except Exception as e:
            log_error(f"Error al mostrar menú de columnas desde header: {e}")s dst:
            self.mostrar_mensaje(f"Error al mostrar menú de columnas: {e}", "error")
            except Exception as e:
    def toggle_columna(self, tabla, idx, header, columnas_visibles, config_path, checked):
        try:    self.mostrar_mensaje(f"Error al guardar imagen QR: {e}", "error")
            columnas_visibles[header] = checkediable para evitar error de compilación
            tabla.setColumnHidden(idx, not checked)
            self.guardar_config_columnas(config_path, columnas_visibles)
            self.mostrar_mensaje(f"Columna '{header}' {'mostrada' if checked else 'ocultada'}", "info")
        except Exception as e:.lib.pagesizes import letter
            log_error(f"Error al alternar columna: {e}")me(dialog, "Exportar QR a PDF", f"qr_{codigo}.pdf", "Archivo PDF (*.pdf)")
            self.mostrar_mensaje(f"Error al alternar columna: {e}", "error")
                    c = canvas.Canvas(file_path, pagesize=letter)
    def auto_ajustar_columna(self, tabla, idx): 100, 500, 200, 200)
        try:        c.save()
            tabla.resizeColumnToContents(idx)
        except Exception as e:ror al exportar QR a PDF: {e}")
            log_error(f"Error al autoajustar columna: {e}") a PDF: {e}", "error")
            self.mostrar_mensaje(f"Error al autoajustar columna: {e}", "error")
        btn_pdf.clicked.connect(exportar_pdf)
    def mostrar_qr_item_seleccionado(self, tabla):
        try:
            selected = tabla.selectedItems()
            if not selected:
                returnDialog(self)
            row = selected[0].row()Agregar nuevo recibo")
            codigo = tabla.item(row, 0).text()  # Usar el primer campo como dato QR
            if not codigo:yout()
                self.mostrar_mensaje("No se pudo obtener el código para el QR.", "error")
                returnt.setPlaceholderText("YYYY-MM-DD")
            qr = qrcode.QRCode(version=1, box_size=6, border=2)")
            qr.add_data(codigo)Box()
            qr.make(fit=True)ner_obras_para_selector()
            img = qr.make_image(fill_color="black", back_color="white")
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                img.save(tmp)dItem(f"{obra_id} - {nombre} ({cliente})", obra_id)
                tmp.flush()LineEdit()
                tmp_path = tmp.namederText("Monto total")
                pixmap = QPixmap(tmp_path)total del recibo")
        except Exception as e:LineEdit()
            log_error(f"Error al generar QR: {e}")cepto")
            self.mostrar_mensaje(f"Error al generar QR: {e}", "error")
            returnatario_input = QLineEdit()
        dialog = QDialog(self).setPlaceholderText("Destinatario")
        dialog.setWindowTitle(f"Código QR para {codigo}")el recibo")
        vbox = QVBoxLayout(dialog)Emisión:", fecha_input)
        qr_label = QLabel()ra:", obra_combo)
        qr_label.setPixmap(pixmap)al:", monto_input)
        vbox.addWidget(qr_label)o:", concepto_input)
        btns = QHBoxLayout()tinatario:", destinatario_input)
        btns = QHBoxLayout()(form)
        btn_guardar = QPushButton()
        btn_guardar.setIcon(QIcon("resources/icons/guardar-qr.svg"))
        btn_guardar.setToolTip("Guardar QR como imagen"))
        estilizar_boton_icono(btn_guardar)r")
        btn_pdf = QPushButton()no(btn_agregar)
        btn_pdf.setIcon(QIcon("resources/icons/pdf.svg"))
        btn_pdf.setToolTip("Exportar QR a PDF")
        estilizar_boton_icono(btn_pdf))
        btns.addWidget(btn_guardar)elar)
        btns.addWidget(btn_pdf)ns)
        vbox.addLayout(btns)bo():
        def guardar():= [
            try:    fecha_input.text(),
                file_path, _ = QFileDialog.getSaveFileName(dialog, "Guardar QR", f"qr_{codigo}.png", "Imagen PNG (*.png)")
                if file_path:ut.text(),
                    with open(tmp_path, "rb") as src, open(file_path, "wb") as dst:
                        dst.write(src.read()),
            except Exception as e:
                log_error(f"Error al guardar imagen QR: {e}")
                self.mostrar_mensaje(f"Error al guardar imagen QR: {e}", "error")
                e = None  # Fix: consolidar variable para evitar error de compilación
        def exportar_pdf():
            try:if hasattr(self, 'controller'):
                from reportlab.pdfgen import canvasdatos)
                from reportlab.lib.pagesizes import letter
                file_path, _ = QFileDialog.getSaveFileName(dialog, "Exportar QR a PDF", f"qr_{codigo}.pdf", "Archivo PDF (*.pdf)")
                if file_path:ked.connect(dialog.reject)
                    c = canvas.Canvas(file_path, pagesize=letter)
                    c.drawInlineImage(tmp_path, 100, 500, 200, 200)
                    c.save()r al abrir diálogo de nuevo recibo: {e}")
            except Exception as e:"Error al abrir diálogo de nuevo recibo: {e}", "error")
                log_error(f"Error al exportar QR a PDF: {e}")
                self.mostrar_mensaje(f"Error al exportar QR a PDF: {e}", "error")
        btn_guardar.clicked.connect(guardar)de nuevo movimiento
        btn_pdf.clicked.connect(exportar_pdf)ntable (stub)")
        dialog.exec()
    def abrir_dialogo_estadistica_personalizada(self):
    def abrir_dialogo_nuevo_recibo(self):
        try:og.setWindowTitle("Configurar Estadística Personalizada")
            dialog = QDialog(self)g)
            dialog.setWindowTitle("Agregar nuevo recibo")
            layout = QVBoxLayout()últiple)
            form = QFormLayout() 'balance_headers', ["tipo", "monto", "moneda", "obra", "fecha"])
            fecha_input = QLineEdit()
            fecha_input.setPlaceholderText("YYYY-MM-DD")
            fecha_input.setToolTip("Fecha de emisión del recibo")para agrupar")
            obra_combo = QComboBox()al:", combo_columnas)
            obras = self.obtener_obras_para_selector()
            for obra in obras:Box()
                obra_id, nombre, cliente = obra[0], obra[1], obra[2]lumnas.currentText()])
                obra_combo.addItem(f"{obra_id} - {nombre} ({cliente})", obra_id)
            monto_input = QLineEdit(), combo_filtros)
            monto_input.setPlaceholderText("Monto total")
            monto_input.setToolTip("Monto total del recibo")
            concepto_input = QLineEdit()"Promedio", "Conteo"])
            concepto_input.setPlaceholderText("Concepto")plicar")
            concepto_input.setToolTip("Concepto del recibo")
            destinatario_input = QLineEdit()
            destinatario_input.setPlaceholderText("Destinatario")
            destinatario_input.setToolTip("Destinatario del recibo")
            form.addRow("Fecha de Emisión:", fecha_input)
            form.addRow("Obra:", obra_combo)o_grafico)
            form.addRow("Monto Total:", monto_input)
            form.addRow("Concepto:", concepto_input)
            form.addRow("Destinatario:", destinatario_input)stica personalizada")
            layout.addLayout(form)bre_input)
            btns = QHBoxLayout()
            btn_agregar = QPushButton()
            btn_agregar.setIcon(QIcon("resources/icons/agregar.svg"))
            btn_agregar.setToolTip("Agregar")
            estilizar_boton_icono(btn_agregar)-qr.svg"))
            btn_cancelar = QPushButton("Cancelar")estadística personalizada")
            btn_cancelar.setObjectName("btn_cancelar")(btn_guardar)
            btns.addStretch()celar")
            btns.addWidget(btn_agregar)
            btns.addWidget(btn_cancelar))
            layout.addLayout(btns)ar)
            def agregar_recibo():btns)
                datos = [
                    fecha_input.text(),ext()
                    obra_combo.currentData(),entText()
                    monto_input.text(),tText()
                    concepto_input.text(),ntText()
                    destinatario_input.text(),ut.text().strip()
                    "pendiente"t nombre:
                ]log, "Nombre requerido", "Ingrese un nombre para la estadística.")
                if not all(datos[:-1]):
                    self.mostrar_mensaje("Complete todos los campos.", "advertencia")umna": columna, "filtro": filtro, "metrica": metrica, "tipo_grafico": tipo_grafico, "nombre": nombre}
                    return
                if hasattr(self, 'controller'):on"
                    self.controller.agregar_recibo(datos)onfig_path):
                dialog.accept()
            btn_agregar.clicked.connect(agregar_recibo)g="utf-8") as f:
            btn_cancelar.clicked.connect(dialog.reject)
            self.setTabOrder(fecha_input, obra_combo)
            self.setTabOrder(obra_combo, monto_input)
            self.setTabOrder(monto_input, concepto_input)nombre]
            self.setTabOrder(concepto_input, destinatario_input)
            self.setTabOrder(destinatario_input, btn_agregar)w", encoding="utf-8") as f:
            dialog.setLayout(layout)(configs, f, ensure_ascii=False, indent=2)
            dialog.exec()sticas_personalizadas()
        except Exception as e:
            log_error(f"Error al abrir diálogo de nuevo recibo: {e}")
            self.mostrar_mensaje(f"Error al abrir diálogo de nuevo recibo: {e}", "error")            dialog.accept()

    def abrir_dialogo_nuevo_movimiento(self, *args, **kwargs):
        # TODO: Implementar el diálogo real de nuevo movimiento
        print("Diálogo de nuevo movimiento contable (stub)")

    def abrir_dialogo_estadistica_personalizada(self):boton_exportar_grafico'):
        dialog = QDialog(self)
        dialog.setWindowTitle("Configurar Estadística Personalizada")ico.setIcon(QIcon("img/pdf.svg"))
        layout = QVBoxLayout(dialog)tar_grafico.setToolTip("Exportar gráfico a imagen o PDF")
        form = QFormLayout()on_exportar_grafico)
        # Selección de columnas (múltiple)
        columnas = getattr(self, 'balance_headers', ["tipo", "monto", "moneda", "obra", "fecha"])yout.addWidget(self.boton_exportar_grafico)
        combo_columnas = QComboBox()
        combo_columnas.addItems(columnas)
        combo_columnas.setToolTip("Seleccionar columna principal para agrupar")"Exportar gráfico", "estadistica.png", "Imagen PNG (*.png);;Archivo PDF (*.pdf)")
        form.addRow("Columna principal:", combo_columnas)
        # Selección de columnas secundarias (filtros)as.figure
        combo_filtros = QComboBox()
        combo_filtros.addItems([c for c in columnas if c != combo_columnas.currentText()])
        combo_filtros.setToolTip("Seleccionar columna para filtrar (opcional)")
        form.addRow("Columna filtro:", combo_filtros)le_path, format='png')
        # Selección de métrica
        combo_metrica = QComboBox()
        combo_metrica.addItems(["Suma", "Promedio", "Conteo"])
        combo_metrica.setToolTip("Seleccionar métrica a aplicar")ras()
        form.addRow("Métrica:", combo_metrica)
        # Selección de tipo de gráfico
        combo_grafico = QComboBox()
        combo_grafico.addItems(["Barra", "Torta", "Línea"])
        combo_grafico.setToolTip("Tipo de visualización")
        form.addRow("Tipo de gráfico:", combo_grafico)nce.columnCount()):
        # Nombre para guardar la estadísticabalance.item(row, col)
        nombre_input = QLineEdit()
        nombre_input.setPlaceholderText("Nombre de la estadística personalizada")
        form.addRow("Nombre:", nombre_input)
        layout.addLayout(form)tabla_balance.setRowHidden(row, not visible)
        # Botones
        btns = QHBoxLayout()exto):
        btn_guardar = QPushButton()
        btn_guardar.setIcon(QIcon("resources/icons/guardar-qr.svg"))
        btn_guardar.setToolTip("Guardar y mostrar estadística personalizada")gos.columnCount()):
        estilizar_boton_icono(btn_guardar)ow, col)
        btn_cancelar = QPushButton("Cancelar")nd texto.lower() in item.text().lower():
        btn_cancelar.setObjectName("btn_cancelar")
        btns.addStretch()
        btns.addWidget(btn_guardar)etRowHidden(row, not visible)
        btns.addWidget(btn_cancelar)
        layout.addLayout(btns)
        def guardar_estadistica():ount()):
            columna = combo_columnas.currentText()
            filtro = combo_filtros.currentText()Count()):
            metrica = combo_metrica.currentText()ow, col)
            tipo_grafico = combo_grafico.currentText()d texto.lower() in item.text().lower():
            nombre = nombre_input.text().strip()
            if not nombre:eak
                QMessageBox.warning(dialog, "Nombre requerido", "Ingrese un nombre para la estadística.")
                return
            config = {"columna": columna, "filtro": filtro, "metrica": metrica, "tipo_grafico": tipo_grafico, "nombre": nombre}
            configs = [] lista_fechas if f})
            config_path = "estadisticas_personalizadas.json"nio.clear()
            if os.path.exists(config_path):
                try:
                    with open(config_path, "r", encoding="utf-8") as f:
                        configs = json.load(f)co_estadisticas(self):
                except Exception: filtrados
                    passfico.currentText()
            configs = [c for c in configs if c.get("nombre") != nombre]
            configs.append(config)
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(configs, f, ensure_ascii=False, indent=2)dolar.text().replace(",", ".")) if self.input_dolar.text() else None
            self.cargar_estadisticas_personalizadas()
            if hasattr(self, 'controller'):one
                self.controller.mostrar_estadistica_personalizada(config)s y llamar a la función de graficado adecuada
            dialog.accept()
        btn_guardar.clicked.connect(guardar_estadistica)roller.mostrar_estadisticas_balance(tipo, anio, mes, valor_dolar)
        btn_cancelar.clicked.connect(dialog.reject)
        dialog.exec(), tipo, anio, mes, valor_dolar, datos):
tipo, monto, moneda, obra, fecha, etc.)
    def setup_exportar_grafico_btn(self):
        if not hasattr(self, 'boton_exportar_grafico'):
            self.boton_exportar_grafico = QPushButton()
            self.boton_exportar_grafico.setIcon(QIcon("resources/icons/pdf.svg"))
            self.boton_exportar_grafico.setToolTip("Exportar gráfico a imagen o PDF")neda', 'ARS') == 'USD' and valor_dolar else 1)
            estilizar_boton_icono(self.boton_exportar_grafico)a')
            self.boton_exportar_grafico.clicked.connect(self.exportar_grafico)            total_salidas = sum(float(d['monto']) * (valor_dolar if d.get('moneda', 'ARS') == 'USD' and valor_dolar else 1)
            self.tab_estadisticas_layout.addWidget(self.boton_exportar_grafico)  for d in datos if d['tipo'].lower() == 'salida')

    def exportar_grafico(self):tle('Ingresos vs Egresos (en Pesos)')
        file_path, _ = QFileDialog.getSaveFileName(self, "Exportar gráfico", "estadistica.png", "Imagen PNG (*.png);;Archivo PDF (*.pdf)")
        if file_path:otal Entradas: ${total_entradas:,.2f}   |   Total Salidas: ${total_salidas:,.2f}   |   Saldo: ${total_entradas-total_salidas:,.2f}")
            fig = self.grafico_canvas.figure
            if file_path.endswith('.pdf'): = {}
                fig.savefig(file_path, format='pdf')
            else:                if d['tipo'].lower() == 'entrada':
                fig.savefig(file_path, format='png')Sin Obra')
float(d['monto']) * (valor_dolar if d.get('moneda', 'ARS') == 'USD' and valor_dolar else 1)
    def obtener_obras_para_selector(self):) + monto
        if self.obras_model:r(list(obras.keys()), list(obras.values()), color='#2563eb')
            return self.obras_model.obtener_obras()            ax.set_title('Cobros por Obra (en Pesos)')
        return []
: {len(obras)} obras")
    def filtrar_tabla_balance(self, texto): por Obra":
        for row in range(self.tabla_balance.rowCount()):
            visible = False
            for col in range(self.tabla_balance.columnCount()):
                item = self.tabla_balance.item(row, col)obra', 'Sin Obra')
                if item and texto.lower() in item.text().lower(): = float(d['monto']) * (valor_dolar if d.get('moneda', 'ARS') == 'USD' and valor_dolar else 1)
                    visible = True
                    break            ax.bar(list(obras.keys()), list(obras.values()), color='#ef4444')
            self.tabla_balance.setRowHidden(row, not visible)(en Pesos)')

    def filtrar_tabla_pagos(self, texto):men.setText(f"Pagos por obra: {len(obras)} obras")
        for row in range(self.tabla_pagos.rowCount()):
            visible = False
            for col in range(self.tabla_pagos.columnCount()):]
                item = self.tabla_pagos.item(row, col)lf.procesar_movimientos(datos)
                if item and texto.lower() in item.text().lower():ntradas.get(m, 0.0) for m in range(1, 13)]
                    visible = True, 13)]
                    break            ax.plot(meses, entradas, label='Entradas', color='#22c55e', marker='o')
            self.tabla_pagos.setRowHidden(row, not visible)Salidas', color='#ef4444', marker='o')

    def filtrar_tabla_recibos(self, texto):Monto (ARS)')
        for row in range(self.tabla_recibos.rowCount()):
            visible = Falsel de ingresos y egresos")
            for col in range(self.tabla_recibos.columnCount()):
                item = self.tabla_recibos.item(row, col)to']) for d in datos if d.get('moneda', 'ARS') == 'ARS')
                if item and texto.lower() in item.text().lower():at(d['monto']) for d in datos if d.get('moneda', 'ARS') == 'USD')
                    visible = Trueutopct='%1.1f%%', colors=['#2563eb', '#fbbf24'])
                    break            ax.set_title('Desglose por Moneda')
            self.tabla_recibos.setRowHidden(row, not visible)s: ${ars:,.2f} | Total en Dólares: U$D {usd:,.2f}")

    def cargar_anios_estadisticas(self, lista_fechas):
        anios = sorted({str(f[:4]) for f in lista_fechas if f})ientos):
        self.combo_anio.clear()
        self.combo_anio.addItem("Todos")        salidas = {}
        self.combo_anio.addItems(anios)

    def actualizar_grafico_estadisticas(self):
        # Este método debe ser llamado por el controlador con los datos filtrados
        tipo = self.combo_tipo_grafico.currentText()(m, 0.0) + monto
        anio = self.combo_anio.currentText()else:
        mes = self.combo_mes.currentText()
        try:salidas
            valor_dolar = float(self.input_dolar.text().replace(",", ".")) if self.input_dolar.text() else None
        except Exception:
            valor_dolar = Nonesonalizadas.json"
        # El controlador debe proveer los datos filtrados y llamar a la función de graficado adecuada
        if hasattr(self, 'controller'):        self.combo_estadistica_personalizada.clear()
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
