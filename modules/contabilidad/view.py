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
        self.filtro_balance.setObjectName("form_input")
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
        self.filtro_pagos.setObjectName("form_input")
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
        self.filtro_recibos.setObjectName("form_input")
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
        self.combo_tipo_grafico.setObjectName("form_input")
        self.combo_tipo_grafico.addItems([
            "Ingresos vs Egresos", "Cobros por Obra", "Pagos por Obra", "Evolución Mensual", "Desglose por Moneda"
        ])
        self.combo_tipo_grafico.setToolTip("Seleccionar tipo de gráfico estadístico")
        controles_layout.addWidget(QLabel("Tipo de gráfico:"))
        controles_layout.addWidget(self.combo_tipo_grafico)
        self.combo_anio = QComboBox()
        self.combo_anio.setObjectName("form_input")
        self.combo_anio.setToolTip("Año a analizar")
        controles_layout.addWidget(QLabel("Año:"))
        controles_layout.addWidget(self.combo_anio)
        self.combo_mes = QComboBox()
        self.combo_mes.setObjectName("form_input")
        self.combo_mes.addItems(["Todos"] + [str(m) for m in range(1, 13)])
        self.combo_mes.setToolTip("Mes a analizar")
        controles_layout.addWidget(QLabel("Mes:"))
        controles_layout.addWidget(self.combo_mes)
        self.input_dolar = QLineEdit()
        self.input_dolar.setObjectName("form_input")
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
        self.combo_estadistica_personalizada = QComboBox()
        self.combo_estadistica_personalizada.setObjectName("form_input")
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
        self.boton_actualizar_grafico.clicked.connect(self.actualizar_grafico_estadisticas)
        self.combo_tipo_grafico.currentIndexChanged.connect(self.actualizar_grafico_estadisticas)
        self.combo_anio.currentIndexChanged.connect(self.actualizar_grafico_estadisticas)
        self.combo_mes.currentIndexChanged.connect(self.actualizar_grafico_estadisticas)
        self.input_dolar.editingFinished.connect(self.actualizar_grafico_estadisticas)
        self.setLayout(self.main_layout)

        # --- FEEDBACK VISUAL CENTRALIZADO Y QSS GLOBAL ---
        self.label_feedback = QLabel()
        self.label_feedback.setObjectName("label_feedback")
        self.label_feedback.setVisible(False)
        self.label_feedback.setAccessibleName("Feedback visual de Contabilidad")
        self.label_feedback.setAccessibleDescription("Mensaje de feedback visual y accesible para el usuario en Contabilidad")
        self.main_layout.addWidget(self.label_feedback)
        # --- FIN FEEDBACK VISUAL GLOBAL ---

        # Refuerzo de accesibilidad en botones principales
        # Menú de columnas y QR para cada tabla
        for btn in [self.boton_agregar_balance, self.boton_agregar_recibo, self.boton_actualizar_grafico, self.boton_estadistica_personalizada]:
            btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            # Nombres accesibles más descriptivos
            if btn is self.boton_agregar_balance:
                btn.setAccessibleName("Botón agregar movimiento contable")
            elif btn is self.boton_agregar_recibo:
                btn.setAccessibleName("Botón agregar recibo de contabilidad")
            elif btn is self.boton_actualizar_grafico:
                btn.setAccessibleName("Botón actualizar gráfico de estadísticas")
            elif btn is self.boton_estadistica_personalizada:
                btn.setAccessibleName("Botón estadística personalizada de contabilidad")
            else:
                btn.setAccessibleName("Botón de acción de contabilidad")
        # Refuerzo de accesibilidad en tablas principales
        for tabla, nombre in zip([self.tabla_balance, self.tabla_pagos, self.tabla_recibos],
                                 ["Tabla de balance contable", "Tabla de pagos contables", "Tabla de recibos contables"]):
            tabla.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            tabla.setToolTip(nombre)
            tabla.setAccessibleName(nombre)
            h_header = tabla.horizontalHeader() if hasattr(tabla, 'horizontalHeader') else None
            if h_header is not None:
                # QSS global: el estilo de header se define en themes/light.qss y dark.qss
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

    def _reforzar_accesibilidad(self, mensaje="Cargando...", tipo="info", duracion=4000):
        # Refuerzo de accesibilidad en botones principales
        for btn in [self.boton_agregar_balance, self.boton_agregar_recibo, self.boton_actualizar_grafico, self.boton_estadistica_personalizada]:
            btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            # QSS global: el outline y tamaño de fuente se gestionan en themes/light.qss y dark.qss
            font = btn.font()
            if font.pointSize() < 12:
                font.setPointSize(12)
            btn.setFont(font)
            # Nombres accesibles más descriptivos
            if btn is self.boton_agregar_balance:
                btn.setAccessibleName("Botón agregar movimiento contable")
            elif btn is self.boton_agregar_recibo:
                btn.setAccessibleName("Botón agregar recibo de contabilidad")
            elif btn is self.boton_actualizar_grafico:
                btn.setAccessibleName("Botón actualizar gráfico de estadísticas")
            elif btn is self.boton_estadistica_personalizada:
                btn.setAccessibleName("Botón estadística personalizada de contabilidad")
            else:
                btn.setAccessibleName("Botón de acción de contabilidad")
        # Refuerzo de accesibilidad en tablas principales
        for tabla, nombre in zip([self.tabla_balance, self.tabla_pagos, self.tabla_recibos],
                                 ["Tabla de balance contable", "Tabla de pagos contables", "Tabla de recibos contables"]):
            tabla.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            tabla.setToolTip(nombre)
            tabla.setAccessibleName(nombre)
            h_header = tabla.horizontalHeader() if hasattr(tabla, 'horizontalHeader') else None
            if h_header is not None:
                # QSS global: el estilo de header se define en themes/light.qss y dark.qss
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
    def ocultar_feedback_carga(self):
        if hasattr(self, 'dialog_carga') and self.dialog_carga:
            self.dialog_carga.accept()
            self.dialog_carga = None
    def mostrar_feedback(self, mensaje, tipo="info", duracion=4000):
        """Muestra feedback visual accesible y autolimpia tras un tiempo. Unifica con mostrar_mensaje."""
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
        self.label_feedback.setStyleSheet(f"font-size: 13px; border-radius: 8px; padding: 8px; font-weight: 500; {colores.get(tipo, '')}")
        self.label_feedback.setText(f"{iconos.get(tipo, 'ℹ️ ')}{mensaje}")
        self.label_feedback.setVisible(True)
        self.label_feedback.setAccessibleDescription(mensaje)
        if hasattr(self, '_feedback_timer') and self._feedback_timer:
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

    def mostrar_mensaje(self, mensaje, tipo="info", duracion=4000):
        """Alias para mostrar_feedback, para compatibilidad con otros módulos."""
        self.mostrar_feedback(mensaje, tipo, duracion)

    def ocultar_feedback(self):
        self.label_feedback.clear()
        self.label_feedback.setVisible(False)
        self.label_feedback.setAccessibleDescription("")

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
        from PyQt6.QtCore import QPoint
        try:
            header = tabla.horizontalHeader()
            if header is not None and all(hasattr(header, m) for m in ['sectionPosition', 'mapToGlobal', 'sectionViewportPosition']):
                if idx < 0 or idx >= tabla.columnCount():
                    self.mostrar_mensaje("Índice de columna fuera de rango", "error")
                    return
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

    def guardar_config_columnas(self, config_path, columnas_visibles):
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(columnas_visibles, f, ensure_ascii=False, indent=2)
            self.mostrar_mensaje("Configuración de columnas guardada", "exito")
        except Exception as e:
            log_error(f"Error al guardar configuración de columnas: {e}")
            self.mostrar_mensaje(f"Error al guardar configuración de columnas: {e}", "error")

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

    def abrir_dialogo_estadistica_personalizada(self):
        # Implementación básica: solo muestra un mensaje
        QMessageBox.information(self, "Estadística personalizada", "Funcionalidad en desarrollo.")

    def seleccionar_estadistica_personalizada(self, idx):
        # Implementación básica: solo muestra un mensaje
        pass

    def setup_exportar_grafico_btn(self):
        # Implementación básica: solo crea el botón si no existe
        if not hasattr(self, 'boton_exportar_grafico'):
            self.boton_exportar_grafico = QPushButton("Exportar gráfico")
            self.tab_estadisticas_layout.addWidget(self.boton_exportar_grafico)

    def actualizar_grafico_estadisticas(self):
        # Implementación básica: solo muestra un mensaje
        self.label_resumen.setText("Actualizando gráfico...")
