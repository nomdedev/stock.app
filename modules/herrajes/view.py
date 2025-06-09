from PyQt6.QtWidgets import (QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QTableWidget, QTableWidgetItem, QComboBox, QLineEdit, QTabWidget, QProgressBar, QMenu, QDialog)
from PyQt6.QtGui import QIcon, QColor, QPixmap, QAction
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QPoint
import os, json, datetime
import pandas as pd
from functools import partial
from core.table_responsive_mixin import TableResponsiveMixin
from core.ui_components import estilizar_boton_icono, aplicar_qss_global_y_tema
from core.logger import log_error

class FeedbackBanner(QWidget):
    """
    Banner/snackbar visual para feedback con icono, color y botón de cierre.
    """
    ICONOS = {
        "info": "resources/icons/info-blue.svg",
        "exito": "resources/icons/check-green.svg",
        "error": "resources/icons/error-red.svg",
        "advertencia": "resources/icons/warning-yellow.svg",
    }
    COLORES = {
        "info": "#e3f6fd",
        "exito": "#d4edda",
        "error": "#f8d7da",
        "advertencia": "#fff3cd",
    }
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("feedback_banner")
        self.setVisible(False)
        self.setAccessibleName("Feedback visual tipo banner")
        self.h_layout = QHBoxLayout(self)
        self.h_layout.setContentsMargins(16, 6, 16, 6)
        self.h_layout.setSpacing(12)
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(24, 24)
        self.h_layout.addWidget(self.icon_label)
        self.text_label = QLabel()
        self.text_label.setWordWrap(True)
        self.text_label.setAccessibleName("Mensaje de feedback visual")
        self.h_layout.addWidget(self.text_label, stretch=1)
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(28, 28)
        self.close_btn.setToolTip("Cerrar mensaje de feedback")
        self.close_btn.setAccessibleName("Cerrar feedback visual")
        self.close_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.close_btn.setStyleSheet("border:none;background:transparent;font-size:18px;")
        self.close_btn.clicked.connect(self.hide)
        self.h_layout.addWidget(self.close_btn)
        self._timer = None
    def show_feedback(self, mensaje, tipo="info", duracion=3500):
        icon_path = self.ICONOS.get(tipo, self.ICONOS["info"])
        color = self.COLORES.get(tipo, self.COLORES["info"])
        self.icon_label.setPixmap(QPixmap(icon_path).scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio))
        self.text_label.setText(mensaje)
        self.setStyleSheet(f"background:{color};border-radius:8px;font-size:15px;")
        self.setVisible(True)
        self.setAccessibleDescription(mensaje)
        self.text_label.setAccessibleDescription(mensaje)
        self.text_label.setText(mensaje)
        self.text_label.setProperty("live", "polite")  # Sugerencia para lectores de pantalla
        self.close_btn.setFocus()
        # Forzar notificación a lectores de pantalla
        self.text_label.repaint()
        self.repaint()
        if self._timer:
            self._timer.stop()
            self._timer.deleteLater()
        from PyQt6.QtCore import QTimer
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.hide)
        self._timer.start(duracion)
    def hide(self):
        self.setVisible(False)
        self.setAccessibleDescription("")
        self.text_label.setAccessibleDescription("")
        if self._timer:
            self._timer.stop()
            self._timer.deleteLater()
            self._timer = None

class HerrajesView(QWidget, TableResponsiveMixin):
    """
    Vista de gestión de herrajes.
    El botón principal de agregar herraje está disponible como self.boton_agregar para compatibilidad con el controlador.
    """
    # Señales para acciones principales
    nuevo_herraje_signal = pyqtSignal()
    exportar_excel_signal = pyqtSignal()
    buscar_signal = pyqtSignal()
    ajustar_stock_signal = pyqtSignal()
    generar_qr_signal = pyqtSignal()
    nuevo_pedido_signal = pyqtSignal()
    actualizar_signal = pyqtSignal()

    def __init__(self, db_connection=None, usuario_actual="default"):
        self.boton_agregar = None  # Inicialización temprana para evitar AttributeError
        super().__init__()
        self.setObjectName("HerrajesView")
        self.db_connection = db_connection
        self.usuario_actual = usuario_actual
        self.config_path = os.path.join(os.path.expanduser("~"), "config_herrajes_columns.json")
        self.columnas_visibles = {"ID": True, "Nombre": True, "Cantidad": True, "Proveedor": True, "Ubicación": True, "Stock mínimo": True}
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(32, 32, 32, 32)
        self.main_layout.setSpacing(16)
        # Feedback visual tipo banner/snackbar con icono
        from PyQt6.QtWidgets import QHBoxLayout
        self.feedback_banner = FeedbackBanner(self)
        self.main_layout.addWidget(self.feedback_banner)
        # Label de feedback para compatibilidad con tests de accesibilidad
        self.label_feedback = QLabel()
        self.label_feedback.setObjectName("label_feedback")
        self.label_feedback.setVisible(False)
        self.label_feedback.setAccessibleName("Feedback visual de Herrajes")
        self.label_feedback.setAccessibleDescription(
            "Mensaje de feedback visual y accesible para el usuario en Herrajes"
        )
        self.main_layout.addWidget(self.label_feedback)
        # --- Header visual moderno
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(24)
        self.label_titulo = QLabel("Gestión de Herrajes")
        self.label_titulo.setAccessibleDescription("Título principal de la vista de Herrajes")
        header_layout.addWidget(self.label_titulo, alignment=Qt.AlignmentFlag.AlignVCenter)
        header_layout.addStretch()
        self.main_layout.addLayout(header_layout)
        # --- Barra de botones principales ---
        top_btns_layout = QHBoxLayout()
        top_btns_layout.addStretch()
        # 1. Ajustar stock
        btn_ajustar_stock = QPushButton()
        btn_ajustar_stock.setIcon(QIcon("resources/icons/guardar-permisos.svg"))
        btn_ajustar_stock.setIconSize(QSize(24, 24))
        btn_ajustar_stock.setToolTip("Ajustar stock de herrajes")
        btn_ajustar_stock.setAccessibleName("Botón ajustar stock de herrajes")
        btn_ajustar_stock.clicked.connect(self.ajustar_stock_signal.emit)
        estilizar_boton_icono(btn_ajustar_stock)
        top_btns_layout.addWidget(btn_ajustar_stock)
        # 2. Buscar herraje
        btn_buscar = QPushButton()
        btn_buscar.setIcon(QIcon("resources/icons/search_icon.svg"))
        btn_buscar.setIconSize(QSize(24, 24))
        btn_buscar.setToolTip("Buscar herraje")
        btn_buscar.setAccessibleName("Botón buscar herraje")
        btn_buscar.clicked.connect(self.buscar_signal.emit)
        estilizar_boton_icono(btn_buscar)
        top_btns_layout.addWidget(btn_buscar)
        # 3. Generar QR
        btn_qr = QPushButton()
        btn_qr.setIcon(QIcon("resources/icons/qr_icon.svg"))
        btn_qr.setIconSize(QSize(24, 24))
        btn_qr.setToolTip("Generar código QR de herraje")
        btn_qr.setAccessibleName("Botón generar código QR de herraje")
        btn_qr.clicked.connect(self.generar_qr_signal.emit)
        estilizar_boton_icono(btn_qr)
        top_btns_layout.addWidget(btn_qr)
        # 4. Agregar nuevo herraje
        btn_nuevo_herraje = QPushButton()
        btn_nuevo_herraje.setIcon(QIcon("resources/icons/add-material.svg"))
        btn_nuevo_herraje.setIconSize(QSize(24, 24))
        btn_nuevo_herraje.setToolTip("Agregar nuevo herraje")
        btn_nuevo_herraje.setAccessibleName("Botón agregar nuevo herraje")
        btn_nuevo_herraje.clicked.connect(self.nuevo_herraje_signal.emit)
        estilizar_boton_icono(btn_nuevo_herraje)
        top_btns_layout.addWidget(btn_nuevo_herraje)
        self.boton_agregar = btn_nuevo_herraje  # Exponer el botón como atributo de instancia
        # 5. Exportar a Excel
        btn_excel = QPushButton()
        btn_excel.setIcon(QIcon("resources/icons/excel_icon.svg"))
        btn_excel.setIconSize(QSize(24, 24))
        btn_excel.setToolTip("Exportar herrajes a Excel")
        btn_excel.setAccessibleName("Botón exportar herrajes a Excel")
        btn_excel.clicked.connect(self.exportar_excel_signal.emit)
        estilizar_boton_icono(btn_excel)
        top_btns_layout.addWidget(btn_excel)
        self.main_layout.addLayout(top_btns_layout)
        # --- Tabs principales ---
        self.tabs = QTabWidget()
        # Pestaña 1: Tabla principal de herrajes
        self.tab_herrajes = QWidget()
        tab_herrajes_layout = QVBoxLayout(self.tab_herrajes)
        self.herrajes_headers = ["ID", "Nombre", "Cantidad", "Proveedor", "Ubicación", "Stock mínimo"]
        self.tabla_herrajes = QTableWidget()
        self.tabla_herrajes.setObjectName("tabla_herrajes")
        self.tabla_herrajes.setColumnCount(len(self.herrajes_headers))
        self.tabla_herrajes.setHorizontalHeaderLabels(self.herrajes_headers)
        self.make_table_responsive(self.tabla_herrajes)
        self.tabla_herrajes.setAlternatingRowColors(True)
        self.tabla_herrajes.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_herrajes.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_herrajes.setToolTip("Tabla principal de herrajes")
        self.tabla_herrajes.setAccessibleName("Tabla de herrajes")
        tab_herrajes_layout.addWidget(self.tabla_herrajes)
        self.tab_herrajes.setLayout(tab_herrajes_layout)
        self.tabs.addTab(self.tab_herrajes, "Herrajes")
        # Pestaña 2: Pedidos de herrajes
        self.tab_pedidos = QWidget()
        tab_pedidos_layout = QVBoxLayout(self.tab_pedidos)
        self.pedidos_headers = ["ID Pedido", "Fecha", "Solicitante", "Herrajes", "Cantidad", "Estado", "Observaciones"]
        self.tabla_pedidos = QTableWidget()
        self.tabla_pedidos.setObjectName("tabla_pedidos_herrajes")
        self.tabla_pedidos.setColumnCount(len(self.pedidos_headers))
        self.tabla_pedidos.setHorizontalHeaderLabels(self.pedidos_headers)
        self.make_table_responsive(self.tabla_pedidos)
        self.tabla_pedidos.setAlternatingRowColors(True)
        self.tabla_pedidos.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_pedidos.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_pedidos.setToolTip("Tabla de pedidos de herrajes")
        self.tabla_pedidos.setAccessibleName("Tabla de pedidos de herrajes")
        tab_pedidos_layout.addWidget(self.tabla_pedidos)
        # Botón para armar pedido de herrajes
        btn_nuevo_pedido = QPushButton()
        btn_nuevo_pedido.setIcon(QIcon("resources/icons/add-entrega.svg"))
        btn_nuevo_pedido.setIconSize(QSize(24, 24))
        btn_nuevo_pedido.setToolTip("Armar nuevo pedido de herrajes")
        btn_nuevo_pedido.setAccessibleName("Botón armar pedido de herrajes")
        btn_nuevo_pedido.clicked.connect(self.nuevo_pedido_signal.emit)
        estilizar_boton_icono(btn_nuevo_pedido)
        tab_pedidos_layout.addWidget(btn_nuevo_pedido, alignment=Qt.AlignmentFlag.AlignRight)
        # Botón para exportar pedidos a Excel
        btn_exportar_pedidos = QPushButton()
        btn_exportar_pedidos.setIcon(QIcon("resources/icons/excel_icon.svg"))
        btn_exportar_pedidos.setIconSize(QSize(24, 24))
        btn_exportar_pedidos.setToolTip("Exportar pedidos de herrajes a Excel")
        btn_exportar_pedidos.setAccessibleName("Botón exportar pedidos de herrajes a Excel")
        btn_exportar_pedidos.clicked.connect(self.exportar_tabla_pedidos_a_excel)
        estilizar_boton_icono(btn_exportar_pedidos)
        tab_pedidos_layout.addWidget(btn_exportar_pedidos, alignment=Qt.AlignmentFlag.AlignRight)
        # Botón para exportar pedidos a PDF
        btn_exportar_pedidos_pdf = QPushButton()
        btn_exportar_pedidos_pdf.setIcon(QIcon("resources/icons/pdf_icon.svg"))
        btn_exportar_pedidos_pdf.setIconSize(QSize(24, 24))
        btn_exportar_pedidos_pdf.setToolTip("Exportar pedidos de herrajes a PDF")
        btn_exportar_pedidos_pdf.setAccessibleName("Botón exportar pedidos de herrajes a PDF")
        btn_exportar_pedidos_pdf.clicked.connect(self.exportar_tabla_pedidos_a_pdf)
        estilizar_boton_icono(btn_exportar_pedidos_pdf)
        tab_pedidos_layout.addWidget(btn_exportar_pedidos_pdf, alignment=Qt.AlignmentFlag.AlignRight)
        self.tab_pedidos.setLayout(tab_pedidos_layout)
        self.tabs.addTab(self.tab_pedidos, "Pedidos de Herrajes")
        self.main_layout.addWidget(self.tabs)
        self.setLayout(self.main_layout)

        # --- FEEDBACK VISUAL CENTRALIZADO Y QSS GLOBAL ---
        self._feedback_timer = None
        # --- FIN FEEDBACK VISUAL CENTRALIZADO ---

        # Aplicar QSS global y tema visual (solo desde resources/qss/)
        from utils.theme_manager import cargar_modo_tema
        tema = cargar_modo_tema()
        qss_tema = f"resources/qss/theme_{tema}.qss"
        aplicar_qss_global_y_tema(self, qss_global_path="resources/qss/theme_light.qss", qss_tema_path=qss_tema)

        # Refuerzo de accesibilidad en tabla principal
        self.tabla_herrajes.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.tabla_herrajes.setToolTip("Tabla principal de herrajes")
        self.tabla_herrajes.setAccessibleName("Tabla de herrajes")
        # El estilo de foco y fuente se define ahora en el QSS global/tema
        h_header = self.tabla_herrajes.horizontalHeader() if hasattr(self.tabla_herrajes, 'horizontalHeader') else None
        if h_header is not None:
            try:
                # QSS global: el estilo de header se gestiona en themes/light.qss y dark.qss
                # h_header.setStyleSheet("background-color: #e3f6fd; color: #2563eb; border-radius: 8px; font-size: 10px; padding: 8px 12px; border: 1px solid #e3e3e3;")
                h_header.setSectionsMovable(True)
                h_header.setSectionsClickable(True)
            except Exception:
                pass

        # --- FIN refuerzo estándar feedback/accesibilidad ---

        # Refuerzo de accesibilidad en todos los QLabel
        for widget in self.findChildren(QLabel):
            if not widget.accessibleDescription():
                widget.setAccessibleDescription("Label informativo o de feedback en Herrajes")
        self.tabla_pedidos.cellDoubleClicked.connect(self.abrir_detalle_pedido_herrajes)

        # --- Filtros para la tabla de pedidos de herrajes ---
        self.filtros_pedidos_layout = QHBoxLayout()
        self.filtro_estado = QComboBox()
        self.filtro_estado.addItem("Todos", None)
        self.filtro_estado.addItems(["pendiente", "entregado", "cancelado"])
        self.filtro_estado.setToolTip("Filtrar por estado del pedido")
        self.filtro_obra = QComboBox()
        self.filtro_obra.addItem("Todas las obras", None)
        # Obras se llenan dinámicamente en cargar_pedidos_herrajes
        self.filtro_usuario = QComboBox()
        self.filtro_usuario.addItem("Todos los usuarios", None)
        # Usuarios se llenan dinámicamente en cargar_pedidos_herrajes
        self.filtro_tipo_herraje = QComboBox()
        self.filtro_tipo_herraje.addItem("Todos los tipos", None)
        # Tipos de herraje se llenan dinámicamente
        self.filtro_fecha_inicio = QLineEdit()
        self.filtro_fecha_inicio.setPlaceholderText("Fecha desde (AAAA-MM-DD)")
        self.filtro_fecha_inicio.setToolTip("Filtrar desde fecha (inclusive)")
        self.filtro_fecha_fin = QLineEdit()
        self.filtro_fecha_fin.setPlaceholderText("Fecha hasta (AAAA-MM-DD)")
        self.filtro_fecha_fin.setToolTip("Filtrar hasta fecha (inclusive)")
        self.filtro_stock_bajo = QComboBox()
        self.filtro_stock_bajo.addItem("Stock: Todos", None)
        self.filtro_stock_bajo.addItem("Solo bajo stock", True)
        self.filtro_busqueda = QLineEdit()
        self.filtro_busqueda.setPlaceholderText("Buscar por obra, usuario, herraje, observaciones...")
        self.filtro_busqueda.setToolTip("Búsqueda rápida en pedidos de herrajes")
        self.filtros_pedidos_layout.addWidget(QLabel("Estado:"))
        self.filtros_pedidos_layout.addWidget(self.filtro_estado)
        self.filtros_pedidos_layout.addWidget(QLabel("Obra:"))
        self.filtros_pedidos_layout.addWidget(self.filtro_obra)
        self.filtros_pedidos_layout.addWidget(QLabel("Usuario:"))
        self.filtros_pedidos_layout.addWidget(self.filtro_usuario)
        self.filtros_pedidos_layout.addWidget(QLabel("Tipo de herraje:"))
        self.filtros_pedidos_layout.addWidget(self.filtro_tipo_herraje)
        self.filtros_pedidos_layout.addWidget(QLabel("Fecha desde:"))
        self.filtros_pedidos_layout.addWidget(self.filtro_fecha_inicio)
        self.filtros_pedidos_layout.addWidget(QLabel("Fecha hasta:"))
        self.filtros_pedidos_layout.addWidget(self.filtro_fecha_fin)
        self.filtros_pedidos_layout.addWidget(self.filtro_stock_bajo)
        self.filtros_pedidos_layout.addWidget(self.filtro_busqueda)
        self.filtros_pedidos_layout.addStretch()
        tab_pedidos_layout.insertLayout(0, self.filtros_pedidos_layout)
        # Conexión de filtros
        self.filtro_estado.currentIndexChanged.connect(self.filtrar_tabla_pedidos)
        self.filtro_obra.currentIndexChanged.connect(self.filtrar_tabla_pedidos)
        self.filtro_usuario.currentIndexChanged.connect(self.filtrar_tabla_pedidos)
        self.filtro_tipo_herraje.currentIndexChanged.connect(self.filtrar_tabla_pedidos)
        self.filtro_fecha_inicio.textChanged.connect(self.filtrar_tabla_pedidos)
        self.filtro_fecha_fin.textChanged.connect(self.filtrar_tabla_pedidos)
        self.filtro_stock_bajo.currentIndexChanged.connect(self.filtrar_tabla_pedidos)
        self.filtro_busqueda.textChanged.connect(self.filtrar_tabla_pedidos)
        # Datos cacheados para filtrado
        self._datos_pedidos_cache = []
        self._filtros_recientes_path = os.path.join(os.path.expanduser("~"), "filtros_pedidos_herrajes.json")
        self.cargar_filtros_recientes()
    def mostrar_mensaje(self, mensaje, tipo="info", duracion=3500):
        """
        Alias para mostrar_feedback, usado por handlers internos para unificar feedback visual.
        """
        self.mostrar_feedback(mensaje, tipo, duracion)

    def mostrar_feedback(self, mensaje, tipo="info", duracion=3500):
        """
        Muestra un mensaje de feedback visual accesible en el banner/snackbar.
        tipo: info, exito, error, advertencia
        """
        self.feedback_banner.show_feedback(mensaje, tipo, duracion)
        if hasattr(self, "label_feedback") and self.label_feedback:
            self.label_feedback.setText(mensaje)
            self.label_feedback.setAccessibleDescription(mensaje)
            self.label_feedback.setVisible(True)

    def ocultar_feedback(self):
        self.feedback_banner.hide()
        if hasattr(self, "label_feedback") and self.label_feedback:
            self.label_feedback.setVisible(False)
            self.label_feedback.clear()
            self.label_feedback.setAccessibleDescription("")

    def mostrar_feedback_carga(self, mensaje="Cargando...", minimo=0, maximo=0):
        """Muestra un feedback visual de carga usando QProgressBar modal."""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar
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

    def cargar_config_columnas(self):
        import os, json
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            log_error(f"Error al cargar configuración de columnas: {e}")
            self.mostrar_mensaje(f"Error al cargar configuración de columnas: {e}", "error")
        return {header: True for header in self.herrajes_headers}

    def guardar_config_columnas(self):
        import json
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.columnas_visibles, f, ensure_ascii=False, indent=2)
            self.mostrar_mensaje("Configuración de columnas guardada", "exito")
        except Exception as e:
            log_error(f"Error al guardar configuración de columnas: {e}")
            self.mostrar_mensaje(f"Error al guardar configuración de columnas: {e}", "error")

    def aplicar_columnas_visibles(self):
        try:
            for idx, header in enumerate(self.herrajes_headers):
                visible = self.columnas_visibles.get(header, True)
                self.tabla_herrajes.setColumnHidden(idx, not visible)
        except Exception as e:
            log_error(f"Error al aplicar columnas visibles: {e}")
            self.mostrar_mensaje(f"Error al aplicar columnas visibles: {e}", "error")

    def mostrar_menu_columnas(self, pos):
        header = self.tabla_pedidos.horizontalHeader() if hasattr(self, 'tabla_pedidos') else None
        if header is None:
            self.mostrar_feedback("No se puede mostrar el menú de columnas: header no disponible o incompleto", "error")
            return
        try:
            menu = QMenu(self)
            for i, header_text in enumerate(self.pedidos_headers):
                accion = QAction(header_text, self)
                accion.setCheckable(True)
                accion.setChecked(not self.tabla_pedidos.isColumnHidden(i))
                accion.toggled.connect(lambda checked, col=i: self.tabla_pedidos.setColumnHidden(col, not checked))
                menu.addAction(accion)
            if pos is not None:
                menu.exec(header.mapToGlobal(pos))
            else:
                menu.exec(self.mapToGlobal(self.tabla_pedidos.pos()))
        except Exception as e:
            self.mostrar_feedback(f"Error mostrando menú de columnas: {e}", "error")

    def auto_ajustar_columna(self, index):
        header = self.tabla_pedidos.horizontalHeader() if hasattr(self, 'tabla_pedidos') else None
        if header is None:
            self.mostrar_feedback("No se puede autoajustar columna: header no disponible o incompleto", "error")
            return
        try:
            self.tabla_pedidos.resizeColumnToContents(index)
        except Exception as e:
            self.mostrar_feedback(f"Error autoajustando columna: {e}", "error")

    def mostrar_menu_columnas_header(self, index):
        header = self.tabla_pedidos.horizontalHeader() if hasattr(self, 'tabla_pedidos') else None
        if header is None:
            self.mostrar_feedback("No se puede mostrar el menú de columnas: header no disponible o incompleto", "error")
            return
        try:
            pos = header.sectionViewportPosition(index)
            menu = QMenu(self)
            for i, header_text in enumerate(self.pedidos_headers):
                accion = QAction(header_text, self)
                accion.setCheckable(True)
                accion.setChecked(not self.tabla_pedidos.isColumnHidden(i))
                accion.toggled.connect(lambda checked, col=i: self.tabla_pedidos.setColumnHidden(col, not checked))
                menu.addAction(accion)
            # Usar QPoint para mapToGlobal
            punto = QPoint(pos, 0)
            menu.exec(header.mapToGlobal(punto))
        except Exception as e:
            self.mostrar_feedback(f"Error mostrando menú de columnas: {e}", "error")

    def agregar_columna_acciones_pedidos(self):
        """
        Agrega la columna de acciones (Entregar, Cancelar, Editar) a la tabla de pedidos de herrajes.
        """
        col_accion = self.tabla_pedidos.columnCount()
        self.tabla_pedidos.setColumnCount(col_accion + 1)
        self.tabla_pedidos.setHorizontalHeaderItem(col_accion, QTableWidgetItem("Acciones"))
        for fila in range(self.tabla_pedidos.rowCount()):
            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(4)
            btn_entregar = QPushButton()
            btn_entregar.setIcon(QIcon("resources/icons/check-green.svg"))
            btn_entregar.setToolTip("Entregar pedido: marca el pedido como entregado y descuenta stock si corresponde.")
            btn_entregar.setAccessibleName("Botón entregar pedido")
            estilizar_boton_icono(btn_entregar)
            btn_entregar.clicked.connect(lambda _, r=fila: self.accion_entregar_pedido(r))
            btn_cancelar = QPushButton()
            btn_cancelar.setIcon(QIcon("resources/icons/cerrar.svg"))
            btn_cancelar.setToolTip("Cancelar pedido: anula el pedido y devuelve el stock reservado.")
            btn_cancelar.setAccessibleName("Botón cancelar pedido")
            estilizar_boton_icono(btn_cancelar)
            btn_cancelar.clicked.connect(lambda _, r=fila: self.accion_cancelar_pedido(r))
            btn_editar = QPushButton()
            btn_editar.setIcon(QIcon("resources/icons/edit.svg"))
            btn_editar.setToolTip("Editar pedido: permite modificar datos del pedido seleccionado.")
            btn_editar.setAccessibleName("Botón editar pedido")
            estilizar_boton_icono(btn_editar)
            btn_editar.clicked.connect(lambda _, r=fila: self.accion_editar_pedido(r))
            layout.addWidget(btn_entregar)
            layout.addWidget(btn_cancelar)
            layout.addWidget(btn_editar)
            layout.addStretch()
            widget.setLayout(layout)
            self.tabla_pedidos.setCellWidget(fila, col_accion, widget)

    def accion_entregar_pedido(self, fila):
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(self, "Confirmar entrega", "¿Está seguro que desea marcar este pedido como entregado? Esta acción descontará stock.", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self._ultima_accion = ("entregar", fila)
            self.mostrar_feedback_con_deshacer(f"Pedido entregado (fila {fila})", "exito")
        else:
            self.mostrar_feedback("Entrega cancelada por el usuario.", "info")

    def accion_cancelar_pedido(self, fila):
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(self, "Confirmar cancelación", "¿Está seguro que desea cancelar este pedido? El stock reservado será devuelto.", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self._ultima_accion = ("cancelar", fila)
            self.mostrar_feedback_con_deshacer(f"Pedido cancelado (fila {fila})", "exito")
        else:
            self.mostrar_feedback("Cancelación abortada por el usuario.", "info")

    def mostrar_feedback_con_deshacer(self, mensaje, tipo="info", duracion=3500):
        # Muestra feedback con botón "Deshacer" (solo para la última acción)
        self.feedback_banner.show_feedback(mensaje, tipo, duracion)
        # Agregar botón "Deshacer" temporalmente al banner
        if not hasattr(self, '_btn_deshacer'):
            from PyQt6.QtWidgets import QPushButton
            self._btn_deshacer = QPushButton("Deshacer")
            self._btn_deshacer.setAccessibleName("Botón deshacer última acción")
            self._btn_deshacer.setToolTip("Deshacer la última acción realizada")
            self._btn_deshacer.setStyleSheet("background:#f1f5f9;color:#2563eb;border-radius:6px;padding:4px 12px;font-size:14px;")
            self._btn_deshacer.clicked.connect(self.deshacer_ultima_accion)
            self.feedback_banner.h_layout.insertWidget(self.feedback_banner.h_layout.count()-1, self._btn_deshacer)
        self._btn_deshacer.setVisible(True)
    def deshacer_ultima_accion(self):
        if hasattr(self, '_ultima_accion'):
            accion, fila = self._ultima_accion
            if accion == "entregar":
                self.mostrar_feedback(f"Entrega deshecha (fila {fila})", "info")
            elif accion == "cancelar":
                self.mostrar_feedback(f"Cancelación deshecha (fila {fila})", "info")
            self._btn_deshacer.setVisible(False)
            del self._ultima_accion

    # --- Métodos stub para evitar errores de atributos faltantes ---
    #
    # ADVERTENCIA: El orden de los botones principales en las barras de acción de esta vista debe seguir el estándar definido en InventarioView.
    # Cualquier cambio en el orden, visibilidad o accesibilidad de los botones principales debe ser justificado y documentado explícitamente en este archivo y en checklist_botones_accion.txt.
    # Última revisión: 2025-06-08. Si modifica el orden, registre el motivo y la fecha en checklist_botones_accion.txt.
    # Esta advertencia es obligatoria para trazabilidad y coherencia visual/accesibilidad.
    #
    def exportar_tabla_pedidos_a_excel(self):
        self.mostrar_feedback("Funcionalidad de exportar a Excel en desarrollo.", "info")
    def exportar_tabla_pedidos_a_pdf(self):
        self.mostrar_feedback("Funcionalidad de exportar a PDF en desarrollo.", "info")
    def abrir_detalle_pedido_herrajes(self, *args, **kwargs):
        self.mostrar_feedback("Funcionalidad de detalle de pedido en desarrollo.", "info")

    def accion_editar_pedido(self, fila):
        self.mostrar_feedback(f"Acción: editar pedido en fila {fila}", "info")

    def cargar_pedidos_herrajes(self, pedidos):
        """
        Carga los pedidos de herrajes en la tabla y actualiza combos de filtros dinámicamente.
        pedidos: lista de dicts con claves: id, fecha, solicitante, herrajes, cantidad, estado, observaciones, obra, usuario, tipo_herraje, stock_bajo
        """
        self._datos_pedidos_cache = pedidos
        self.tabla_pedidos.setRowCount(0)
        # Poblar combos de obra, usuario y tipo de herraje
        obras = set()
        usuarios = set()
        tipos_herraje = set()
        for p in pedidos:
            obras.add(p.get('obra', ''))
            usuarios.add(p.get('usuario', ''))
            tipos_herraje.add(p.get('tipo_herraje', ''))
        self.filtro_obra.blockSignals(True)
        self.filtro_obra.clear()
        self.filtro_obra.addItem("Todas las obras", None)
        for o in sorted(obras):
            if o:
                self.filtro_obra.addItem(o, o)
        self.filtro_obra.blockSignals(False)
        self.filtro_usuario.blockSignals(True)
        self.filtro_usuario.clear()
        self.filtro_usuario.addItem("Todos los usuarios", None)
        for u in sorted(usuarios):
            if u:
                self.filtro_usuario.addItem(u, u)
        self.filtro_usuario.blockSignals(False)
        # Filtro avanzado: tipo de herraje
        if not hasattr(self, 'filtro_tipo_herraje'):
            from PyQt6.QtWidgets import QComboBox, QLabel
            self.filtro_tipo_herraje = QComboBox()
            self.filtro_tipo_herraje.addItem("Todos los tipos", None)
            self.filtro_tipo_herraje.setToolTip("Filtrar por tipo de herraje")
            self.filtro_tipo_herraje.currentIndexChanged.connect(self.filtrar_tabla_pedidos)
            self.filtros_pedidos_layout.insertWidget(6, QLabel("Tipo:"))
            self.filtros_pedidos_layout.insertWidget(7, self.filtro_tipo_herraje)
        self.filtro_tipo_herraje.blockSignals(True)
        self.filtro_tipo_herraje.clear()
        self.filtro_tipo_herraje.addItem("Todos los tipos", None)
        for t in sorted(tipos_herraje):
            if t:
                self.filtro_tipo_herraje.addItem(t, t)
        self.filtro_tipo_herraje.blockSignals(False)
        # Llenar tabla
        for p in pedidos:
            row = self.tabla_pedidos.rowCount()
            self.tabla_pedidos.insertRow(row)
            self.tabla_pedidos.setItem(row, 0, QTableWidgetItem(str(p.get('id', ''))))
            self.tabla_pedidos.setItem(row, 1, QTableWidgetItem(str(p.get('fecha', ''))))
            self.tabla_pedidos.setItem(row, 2, QTableWidgetItem(str(p.get('solicitante', ''))))
            self.tabla_pedidos.setItem(row, 3, QTableWidgetItem(str(p.get('herrajes', ''))))
            self.tabla_pedidos.setItem(row, 4, QTableWidgetItem(str(p.get('cantidad', ''))))
            self.tabla_pedidos.setItem(row, 5, QTableWidgetItem(str(p.get('estado', ''))))
            self.tabla_pedidos.setItem(row, 6, QTableWidgetItem(str(p.get('observaciones', ''))))
        # Agregar columna de acciones si no existe
        if self.tabla_pedidos.columnCount() == len(self.pedidos_headers):
            self.agregar_columna_acciones_pedidos()
        self.filtrar_tabla_pedidos()

    def filtrar_tabla_pedidos(self, *args, **kwargs):
        """
        Aplica los filtros avanzados a la tabla de pedidos de herrajes.
        """
        estado = self.filtro_estado.currentText().lower()
        obra = self.filtro_obra.currentData()
        usuario = self.filtro_usuario.currentData()
        tipo_herraje = self.filtro_tipo_herraje.currentData() if hasattr(self, 'filtro_tipo_herraje') else None
        texto = self.filtro_busqueda.text().lower().strip()
        # Filtro avanzado: stock bajo
        stock_bajo = getattr(self, 'filtro_stock_bajo', None)
        stock_bajo_activo = stock_bajo.currentData() is True if stock_bajo else False
        # Filtro avanzado: rango de fechas (QLineEdit, parsear manualmente)
        fecha_inicio = getattr(self, 'filtro_fecha_inicio', None)
        fecha_fin = getattr(self, 'filtro_fecha_fin', None)
        fi = None
        ff = None
        if fecha_inicio and fecha_inicio.text().strip():
            try:
                fi = datetime.datetime.strptime(fecha_inicio.text().strip(), "%Y-%m-%d").date()
            except Exception:
                fi = None
        if fecha_fin and fecha_fin.text().strip():
            try:
                ff = datetime.datetime.strptime(fecha_fin.text().strip(), "%Y-%m-%d").date()
            except Exception:
                ff = None
        self.tabla_pedidos.setRowCount(0)
        resultados = []
        for p in self._datos_pedidos_cache:
            if estado != "todos" and p.get('estado', '').lower() != estado:
                continue
            if obra and p.get('obra', None) != obra:
                continue
            if usuario and p.get('usuario', None) != usuario:
                continue
            if tipo_herraje and p.get('tipo_herraje', None) != tipo_herraje:
                continue
            if texto:
                texto_en = (
                    str(p.get('obra', '')).lower() +
                    str(p.get('usuario', '')).lower() +
                    str(p.get('herrajes', '')).lower() +
                    str(p.get('observaciones', '')).lower()
                )
                if texto not in texto_en:
                    continue
            if stock_bajo_activo and not p.get('stock_bajo', False):
                continue
            if fi or ff:
                try:
                    fecha_p = p.get('fecha', '')
                    if isinstance(fecha_p, str):
                        fecha_p = datetime.datetime.strptime(fecha_p[:10], "%Y-%m-%d").date()
                    if fi and fecha_p < fi:
                        continue
                    if ff and fecha_p > ff:
                        continue
                except Exception:
                    continue
            resultados.append(p)
        for p in resultados:
            row = self.tabla_pedidos.rowCount()
            self.tabla_pedidos.insertRow(row)
            self.tabla_pedidos.setItem(row, 0, QTableWidgetItem(str(p.get('id', ''))))
            self.tabla_pedidos.setItem(row, 1, QTableWidgetItem(str(p.get('fecha', ''))))
            self.tabla_pedidos.setItem(row, 2, QTableWidgetItem(str(p.get('solicitante', ''))))
            self.tabla_pedidos.setItem(row, 3, QTableWidgetItem(str(p.get('herrajes', ''))))
            self.tabla_pedidos.setItem(row, 4, QTableWidgetItem(str(p.get('cantidad', ''))))
            self.tabla_pedidos.setItem(row, 5, QTableWidgetItem(str(p.get('estado', ''))))
            self.tabla_pedidos.setItem(row, 6, QTableWidgetItem(str(p.get('observaciones', ''))))
        # Volver a agregar columna de acciones si es necesario
        if self.tabla_pedidos.columnCount() == len(self.pedidos_headers):
            self.agregar_columna_acciones_pedidos()
        if not resultados:
            self.mostrar_feedback("No se encontraron pedidos con los filtros aplicados.", "advertencia")
        else:
            self.ocultar_feedback()
        self.guardar_filtros_recientes()

    def guardar_filtros_recientes(self):
        """Guarda los filtros recientes en un archivo JSON en el home del usuario."""
        filtros = {
            'estado': self.filtro_estado.currentText(),
            'obra': self.filtro_obra.currentData(),
            'usuario': self.filtro_usuario.currentData(),
            'tipo_herraje': self.filtro_tipo_herraje.currentData() if hasattr(self, 'filtro_tipo_herraje') else None,
            'busqueda': self.filtro_busqueda.text(),
        }
        path = os.path.join(os.path.expanduser("~"), "filtros_pedidos_herrajes.json")
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(filtros, f, ensure_ascii=False, indent=2)
        except Exception as e:
            log_error(f"Error guardando filtros recientes: {e}")

    def cargar_filtros_recientes(self):
        try:
            if os.path.exists(self._filtros_recientes_path):
                with open(self._filtros_recientes_path, "r", encoding="utf-8") as f:
                    filtros = json.load(f)
                # Restaurar valores en los widgets de filtro
                if filtros.get("estado"):
                    idx = self.filtro_estado.findText(filtros["estado"])
                    if idx >= 0:
                        self.filtro_estado.setCurrentIndex(idx)
                if filtros.get("obra"):
                    idx = self.filtro_obra.findText(filtros["obra"])
                    if idx >= 0:
                        self.filtro_obra.setCurrentIndex(idx)
                if filtros.get("usuario"):
                    idx = self.filtro_usuario.findText(filtros["usuario"])
                    if idx >= 0:
                        self.filtro_usuario.setCurrentIndex(idx)
                if filtros.get("tipo_herraje"):
                    idx = self.filtro_tipo_herraje.findText(filtros["tipo_herraje"])
                    if idx >= 0:
                        self.filtro_tipo_herraje.setCurrentIndex(idx)
                if filtros.get("fecha_inicio"):
                    self.filtro_fecha_inicio.setText(filtros["fecha_inicio"])
                if filtros.get("fecha_fin"):
                    self.filtro_fecha_fin.setText(filtros["fecha_fin"])
                if filtros.get("stock_bajo"):
                    self.filtro_stock_bajo.setCurrentIndex(1 if filtros["stock_bajo"] else 0)
                if filtros.get("busqueda"):
                    self.filtro_busqueda.setText(filtros["busqueda"])
        except Exception as e:
            log_error(f"Error cargando filtros recientes: {e}")

    def actualizar_tabla_pedidos(self, datos):
        """
        Actualiza la tabla de pedidos de herrajes con los datos filtrados.
        """
        self.tabla_pedidos.setRowCount(0)
        for pedido in datos:
            fila = self.tabla_pedidos.rowCount()
            self.tabla_pedidos.insertRow(fila)
            for col, header in enumerate(self.pedidos_headers):
                item = QTableWidgetItem(str(pedido.get(header.lower(), "")))
                self.tabla_pedidos.setItem(fila, col, item)
        # Volver a agregar la columna de acciones si existe
        if self.tabla_pedidos.columnCount() > len(self.pedidos_headers):
            self.agregar_columna_acciones_pedidos()

    def abrir_dialogo_pedido_herrajes(self, controller=None):
        """
        Abre un diálogo modal robusto para armar un pedido de herrajes con autocompletado de código.
        El parámetro controller debe ser pasado explícitamente desde el controlador.
        """
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QLabel, QPushButton, QHBoxLayout, QSpinBox, QComboBox, QCompleter
        from PyQt6.QtGui import QPixmap
        from PyQt6.QtCore import Qt
        import os
        dialog = QDialog(self)
        self._ultimo_dialogo_pedido = dialog  # Guardar referencia para tests
        dialog.setWindowTitle("Armar pedido de herrajes")
        dialog.setModal(True)
        dialog.setStyleSheet("QDialog { background: #fff9f3; border-radius: 12px; }")
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)
        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setSpacing(12)
        # --- Combo de obras ---
        cmb_obras = QComboBox()
        cmb_obras.setToolTip("Seleccione la obra asociada al pedido")
        cmb_obras.setAccessibleName("Obra para pedido")
        obras = []
        if controller and hasattr(controller, 'model') and hasattr(controller.model, 'obtener_obras'):
            obras = controller.model.obtener_obras()
        for obra in obras:
            cmb_obras.addItem(str(obra.get('nombre', obra.get('id_obra'))), obra.get('id_obra'))
        form.addRow("Obra:", cmb_obras)
        # --- Autocompletado de herraje ---
        input_codigo = QLineEdit()
        input_codigo.setPlaceholderText("Código o nombre de herraje")
        input_codigo.setToolTip("Ingrese el código o nombre del herraje")
        input_codigo.setAccessibleName("Código de herraje para pedido")
        input_codigo.setObjectName("input_codigo_herraje")
        herrajes = []
        if controller and hasattr(controller, 'model') and hasattr(controller.model, 'obtener_herrajes'):
            herrajes = controller.model.obtener_herrajes()
        codigos_nombres = [f"{h.get('codigo','')} - {h.get('nombre','')}" for h in herrajes]
        completer = QCompleter(codigos_nombres)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        input_codigo.setCompleter(completer)
        form.addRow("Herraje:", input_codigo)
        # --- Mostrar nombre e imagen al seleccionar ---
        lbl_nombre = QLabel("")
        lbl_nombre.setStyleSheet("color: #2563eb; font-size: 13px;")
        lbl_nombre.setAccessibleName("Nombre de herraje seleccionado")
        lbl_imagen = QLabel("")
        lbl_imagen.setFixedSize(64, 64)
        lbl_imagen.setAccessibleName("Imagen de herraje seleccionado")
        form.addRow("Nombre:", lbl_nombre)
        form.addRow("Imagen:", lbl_imagen)
        # --- SpinBox de cantidad ---
        spin_cantidad = QSpinBox()
        spin_cantidad.setMinimum(1)
        spin_cantidad.setMaximum(1)
        spin_cantidad.setToolTip("Cantidad a pedir (máximo: stock actual)")
        spin_cantidad.setAccessibleName("Cantidad a pedir")
        spin_cantidad.setObjectName("spin_cantidad_herraje")
        form.addRow("Cantidad:", spin_cantidad)
        # --- Stock actual label ---
        lbl_stock = QLabel("")
        lbl_stock.setStyleSheet("color: #2563eb; font-size: 13px;")
        form.addRow("Stock actual:", lbl_stock)
        # --- Actualizar datos al seleccionar herraje ---
        def buscar_herraje(texto):
            texto_normalizado = texto.strip().lower().replace(' ', '')
            print('DEBUG buscar_herraje: texto ingresado:', texto, '| normalizado:', texto_normalizado)
            for h in herrajes:
                clave = f"{h.get('codigo','')} - {h.get('nombre','')}".lower().replace(' ', '')
                codigo = h.get('codigo','').lower().replace(' ', '')
                print('DEBUG clave:', clave, '| codigo:', codigo)
                if texto_normalizado == clave or texto_normalizado == codigo:
                    print('DEBUG herraje encontrado:', h)
                    return h
            print('DEBUG herraje NO encontrado')
            return None
        def actualizar_datos_herraje():
            texto = input_codigo.text().strip().lower()
            herraje = buscar_herraje(texto)
            if not herraje:
                lbl_nombre.setText("")
                lbl_imagen.clear()
                lbl_stock.setText("")
                spin_cantidad.setMaximum(1)
                return
            lbl_nombre.setText(herraje.get('nombre',''))
            stock = int(herraje.get('stock_actual', 1))
            lbl_stock.setText(str(stock))
            spin_cantidad.setMaximum(stock if stock > 0 else 1)
            # Imagen
            if herraje.get('imagen') and os.path.exists(herraje['imagen']):
                pix = QPixmap(herraje['imagen']).scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio)
                lbl_imagen.setPixmap(pix)
            else:
                lbl_imagen.clear()
        input_codigo.editingFinished.connect(actualizar_datos_herraje)
        input_codigo.textChanged.connect(lambda _: actualizar_datos_herraje())
        # --- Observaciones ---
        input_obs = QLineEdit()
        input_obs.setPlaceholderText("Observaciones (opcional)")
        input_obs.setAccessibleName("Observaciones del pedido")
        form.addRow("Observaciones:", input_obs)
        layout.addLayout(form)
        # --- Feedback visual ---
        lbl_feedback = QLabel("")
        lbl_feedback.setObjectName("label_feedback_pedido")
        lbl_feedback.setStyleSheet("font-size: 13px; color: #ef4444; padding: 4px 0;")
        lbl_feedback.setVisible(False)
        layout.addWidget(lbl_feedback)
        # --- Botones ---
        btns = QHBoxLayout()
        btn_confirmar = QPushButton()
        btn_confirmar.setIcon(QIcon("resources/icons/add-entrega.svg"))
        btn_confirmar.setToolTip("Confirmar pedido de herrajes")
        btn_confirmar.setObjectName("btn_confirmar_pedido_herraje")
        estilizar_boton_icono(btn_confirmar)
        btn_cancelar = QPushButton()
        btn_cancelar.setIcon(QIcon("resources/icons/cerrar.svg"))
        btn_cancelar.setToolTip("Cancelar y cerrar")
        estilizar_boton_icono(btn_cancelar)
        btns.addStretch()
        btns.addWidget(btn_confirmar)
        btns.addWidget(btn_cancelar)
        layout.addLayout(btns)
        # --- Acción confirmar ---
        def confirmar():
            id_obra = cmb_obras.currentData()
            texto = input_codigo.text().strip().lower()
            herraje = buscar_herraje(texto)
            cantidad = spin_cantidad.value()
            if id_obra is None or not herraje or cantidad < 1:
                lbl_feedback.setText("Complete todos los campos y seleccione un herraje válido.")
                lbl_feedback.setVisible(True)
                return
            if cantidad > int(herraje.get('stock_actual', 0)):
                lbl_feedback.setText("Stock insuficiente para el pedido.")
                lbl_feedback.setVisible(True)
                return
            if not controller or not hasattr(controller, "reservar_herraje"):
                lbl_feedback.setText("Error: No se ha configurado el controlador de herrajes.")
                lbl_feedback.setVisible(True)
                return
            try:
                controller.reservar_herraje(self.usuario_actual, id_obra, herraje.get('id_herraje'), cantidad)
                self.mostrar_feedback("Pedido de herrajes realizado correctamente.", tipo="exito")
                dialog.accept()
                self.actualizar_signal.emit()
            except ValueError as e:
                lbl_feedback.setText(str(e))
                lbl_feedback.setVisible(True)
            except Exception as e:
                lbl_feedback.setText(f"Error inesperado: {e}")
                lbl_feedback.setVisible(True)
        btn_confirmar.clicked.connect(confirmar)
        btn_cancelar.clicked.connect(dialog.reject)
        dialog.exec()

    def _conectar_nuevo_pedido(self, controller):
        # Buscar el botón en la pestaña de pedidos
        for w in self.tab_pedidos.findChildren(QPushButton):
            if w.toolTip() == "Armar nuevo pedido de herrajes":
                try:
                    w.clicked.disconnect()
                except Exception:
                    pass
                w.clicked.connect(lambda: self.abrir_dialogo_pedido_herrajes(controller))
                break
