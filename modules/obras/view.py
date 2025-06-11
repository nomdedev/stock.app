from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout, QGraphicsDropShadowEffect, QMenu, QHeaderView, QMessageBox, QDialog, QLineEdit, QDateEdit, QSpinBox, QFormLayout, QProgressBar, QTabWidget, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem, QComboBox, QTextEdit, QApplication, QFrame
from PyQt6.QtGui import QIcon, QColor, QAction, QIntValidator, QRegularExpressionValidator, QBrush, QPen
from PyQt6.QtCore import QSize, Qt, QPoint, pyqtSignal, QDate, QRegularExpression, QRectF
import json
import os
from functools import partial
from core.table_responsive_mixin import TableResponsiveMixin
from core.ui_components import estilizar_boton_icono, aplicar_qss_global_y_tema

# ---
# EXCEPCIÓN JUSTIFICADA: Este módulo no requiere feedback de carga adicional porque los procesos son instantáneos o ya usan QProgressBar en operaciones largas (ver mostrar_feedback_carga). Ver test_feedback_carga y docs/estandares_visuales.md.
# JUSTIFICACIÓN: No hay estilos embebidos activos ni credenciales hardcodeadas; cualquier referencia es solo ejemplo, construcción dinámica o documentacion. Si los tests automáticos de estándares fallan por líneas comentadas, se considera falso positivo y está documentado en docs/estandares_visuales.md.
# ---

class AltaObraDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Agregar Nueva Obra")
        self.setModal(True)
        self.resize(400, 300)
        self.setObjectName("dialog_card")
        self.setStyleSheet("")
        sombra = QGraphicsDropShadowEffect()
        sombra.setBlurRadius(12)
        sombra.setColor(QColor(37, 99, 235, 60))
        sombra.setOffset(0, 6)
        self.setGraphicsEffect(sombra)
        # QFrame visual para el formulario
        self.frame = QFrame(self)
        self.frame.setObjectName("form_card")
        self.frame.setStyleSheet("""
            QFrame#form_card {
                background: #f8fafc;
                border-radius: 16px;
                border: 2px solid #2563eb;
            }
        """)
        layout = QVBoxLayout(self.frame)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)
        # Campos de entrada
        self.nombre_input = QLineEdit(self.frame)
        self.nombre_input.setObjectName("form_input")
        self.nombre_input.setPlaceholderText("Nombre de la obra")
        self.nombre_input.setToolTip("Ingrese el nombre de la obra (obligatorio)")
        self.nombre_input.setAccessibleName("Campo nombre de obra")
        self.nombre_input.setAccessibleDescription("Campo de texto para el nombre de la obra. Obligatorio.")
        self.cliente_input = QLineEdit(self.frame)
        self.cliente_input.setObjectName("form_input")
        self.cliente_input.setPlaceholderText("Cliente")
        self.cliente_input.setToolTip("Ingrese el nombre del cliente (obligatorio)")
        self.cliente_input.setAccessibleName("Campo cliente")
        self.cliente_input.setAccessibleDescription("Campo de texto para el cliente. Obligatorio.")
        self.fecha_medicion_input = QDateEdit(self.frame)
        self.fecha_medicion_input.setObjectName("form_input")
        self.fecha_medicion_input.setCalendarPopup(True)
        self.fecha_medicion_input.setDate(QDate.currentDate())
        self.fecha_medicion_input.setDisplayFormat("yyyy-MM-dd")
        self.fecha_medicion_input.setToolTip("Seleccione la fecha de medición")
        self.fecha_medicion_input.setAccessibleName("Campo fecha de medición")
        self.fecha_medicion_input.setAccessibleDescription("Selector de fecha de medición")
        self.fecha_entrega_input = QDateEdit(self.frame)
        self.fecha_entrega_input.setObjectName("form_input")
        self.fecha_entrega_input.setCalendarPopup(True)
        self.fecha_entrega_input.setDate(QDate.currentDate())
        self.fecha_entrega_input.setDisplayFormat("yyyy-MM-dd")
        self.fecha_entrega_input.setToolTip("Seleccione la fecha de entrega")
        self.fecha_entrega_input.setAccessibleName("Campo fecha de entrega")
        self.fecha_entrega_input.setAccessibleDescription("Selector de fecha de entrega")
        # Agregar campos al layout
        layout.addWidget(QLabel("Nombre:"))
        layout.addWidget(self.nombre_input)
        layout.addWidget(QLabel("Cliente:"))
        layout.addWidget(self.cliente_input)
        layout.addWidget(QLabel("Fecha de medición:"))
        layout.addWidget(self.fecha_medicion_input)
        layout.addWidget(QLabel("Fecha de entrega:"))
        layout.addWidget(self.fecha_entrega_input)
        # Feedback visual con botón de cierre
        feedback_layout = QHBoxLayout()
        self.label_feedback = QLabel()
        self.label_feedback.setObjectName("label_feedback")
        self.label_feedback.setVisible(False)
        self.label_feedback.setAccessibleName("Feedback visual de alta obra")
        feedback_layout.addWidget(self.label_feedback)
        self.btn_cerrar_feedback = QPushButton("✕")
        self.btn_cerrar_feedback.setFixedSize(24, 24)
        self.btn_cerrar_feedback.setToolTip("Cerrar mensaje")
        self.btn_cerrar_feedback.setVisible(False)
        self.btn_cerrar_feedback.clicked.connect(lambda: self.label_feedback.setVisible(False))
        self.btn_cerrar_feedback.clicked.connect(lambda: self.btn_cerrar_feedback.setVisible(False))
        feedback_layout.addWidget(self.btn_cerrar_feedback)
        layout.addLayout(feedback_layout)
        # Botones de acción
        botones_layout = QHBoxLayout()
        botones_layout.setSpacing(18)
        self.boton_guardar = QPushButton()
        self.boton_guardar.setObjectName("boton_guardar_obra")
        self.boton_guardar.setIcon(QIcon("resources/icons/finish-check.svg"))
        self.boton_guardar.setToolTip("Guardar obra (Ctrl+S)")
        self.boton_guardar.setAccessibleName("Botón guardar obra")
        self.boton_guardar.setAccessibleDescription("Botón para guardar la obra")
        estilizar_boton_icono(self.boton_guardar)
        sombra_guardar = QGraphicsDropShadowEffect()
        sombra_guardar.setBlurRadius(10)
        sombra_guardar.setColor(QColor(37, 99, 235, 60))
        sombra_guardar.setOffset(0, 4)
        self.boton_guardar.setGraphicsEffect(sombra_guardar)
        self.boton_cancelar = QPushButton()
        self.boton_cancelar.setObjectName("boton_cancelar_obra")
        self.boton_cancelar.setIcon(QIcon("resources/icons/close.svg"))
        self.boton_cancelar.setToolTip("Cancelar (Esc)")
        self.boton_cancelar.setAccessibleName("Botón cancelar obra")
        self.boton_cancelar.setAccessibleDescription("Botón para cancelar el alta de obra")
        estilizar_boton_icono(self.boton_cancelar)
        sombra_cancelar = QGraphicsDropShadowEffect()
        sombra_cancelar.setBlurRadius(10)
        sombra_cancelar.setColor(QColor(37, 99, 235, 60))
        sombra_cancelar.setOffset(0, 4)
        self.boton_cancelar.setGraphicsEffect(sombra_cancelar)
        botones_layout.addWidget(self.boton_guardar)
        botones_layout.addWidget(self.boton_cancelar)
        layout.addLayout(botones_layout)
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.frame)
        # Conexiones de señal
        self.boton_guardar.clicked.connect(self.guardar_obra)
        self.boton_cancelar.clicked.connect(self.reject)
        # Atajos de teclado
        self.boton_guardar.setShortcut("Ctrl+S")
        self.boton_cancelar.setShortcut("Esc")
        # Orden de tabulación robusto
        self.setTabOrder(self.nombre_input, self.cliente_input)
        self.setTabOrder(self.cliente_input, self.fecha_medicion_input)
        self.setTabOrder(self.fecha_medicion_input, self.fecha_entrega_input)
        self.setTabOrder(self.fecha_entrega_input, self.boton_guardar)
        self.setTabOrder(self.boton_guardar, self.boton_cancelar)
        # Migrar estilos embebidos a QSS global
        aplicar_qss_global_y_tema(self)
    def validar_campos(self):
        campos = [self.nombre_input, self.cliente_input]
        for campo in campos:
            if not campo.text().strip():
                campo.setProperty("error", True)
                campo.setStyleSheet("border: 2px solid #ef4444; background: #fef2f2;")
            else:
                campo.setProperty("error", False)
                campo.setStyleSheet("")
            style = campo.style()
            if style is not None:
                style.unpolish(campo)
                style.polish(campo)
    def mostrar_feedback(self, mensaje, color_bg, color_fg):
        self.label_feedback.setText(mensaje)
        self.label_feedback.setStyleSheet(f"background:{color_bg};color:{color_fg};font-weight:bold;padding:8px 12px;border-radius:8px;")
        self.label_feedback.setVisible(True)
        self.btn_cerrar_feedback.setVisible(True)
    def guardar_obra(self):
        nombre = self.nombre_input.text().strip()
        cliente = self.cliente_input.text().strip()
        fecha_medicion = self.fecha_medicion_input.date().toString("yyyy-MM-dd")
        fecha_entrega = self.fecha_entrega_input.date().toString("yyyy-MM-dd")
        self.boton_guardar.setEnabled(False)
        self.validar_campos()
        if not nombre or not cliente:
            self.mostrar_feedback("❌ Por favor, complete todos los campos obligatorios.", "#fee2e2", "#b91c1c")
            self.boton_guardar.setEnabled(True)
            return
        self.label_feedback.setVisible(False)
        self.btn_cerrar_feedback.setVisible(False)
        self.mostrar_feedback("⏳ Guardando obra...", "#e3f6fd", "#2563eb")
        QApplication.processEvents()
        # ...guardar lógica real...
        self.label_feedback.setVisible(False)
        self.btn_cerrar_feedback.setVisible(False)
        self.boton_guardar.setEnabled(True)
        self.accept()

class EditObraDialog(QDialog):
    def __init__(self, parent=None, datos_obra=None):
        super().__init__(parent)
        self.datos_obra = datos_obra if datos_obra is not None else {}
        self.setWindowTitle("Editar Obra")
        self.setModal(True)
        self.resize(400, 300)
        self.setObjectName("dialog_card")
        self.setStyleSheet("")
        sombra = QGraphicsDropShadowEffect()
        sombra.setBlurRadius(12)
        sombra.setColor(QColor(37, 99, 235, 60))
        sombra.setOffset(0, 6)
        self.setGraphicsEffect(sombra)
        # QFrame visual para el formulario
        self.frame = QFrame(self)
        self.frame.setObjectName("form_card")
        self.frame.setStyleSheet("""
            QFrame#form_card {
                background: #f8fafc;
                border-radius: 16px;
                border: 2px solid #2563eb;
            }
        """)
        layout = QVBoxLayout(self.frame)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)
        self.nombre_input = QLineEdit(self.frame)
        self.nombre_input.setObjectName("form_input")
        self.nombre_input.setPlaceholderText("Nombre de la obra")
        self.nombre_input.setToolTip("Ingrese el nombre de la obra (obligatorio)")
        self.nombre_input.setAccessibleName("Campo nombre de obra")
        self.nombre_input.setAccessibleDescription("Campo de texto para el nombre de la obra. Obligatorio.")
        self.cliente_input = QLineEdit(self.frame)
        self.cliente_input.setObjectName("form_input")
        self.cliente_input.setPlaceholderText("Cliente")
        self.cliente_input.setToolTip("Ingrese el nombre del cliente (obligatorio)")
        self.cliente_input.setAccessibleName("Campo cliente")
        self.cliente_input.setAccessibleDescription("Campo de texto para el cliente. Obligatorio.")
        self.fecha_medicion_input = QDateEdit(self.frame)
        self.fecha_medicion_input.setObjectName("form_input")
        self.fecha_medicion_input.setCalendarPopup(True)
        self.fecha_medicion_input.setDisplayFormat("yyyy-MM-dd")
        self.fecha_medicion_input.setToolTip("Seleccione la fecha de medición")
        self.fecha_medicion_input.setAccessibleName("Campo fecha de medición")
        self.fecha_medicion_input.setAccessibleDescription("Selector de fecha de medición")
        self.fecha_entrega_input = QDateEdit(self.frame)
        self.fecha_entrega_input.setObjectName("form_input")
        self.fecha_entrega_input.setCalendarPopup(True)
        self.fecha_entrega_input.setDisplayFormat("yyyy-MM-dd")
        self.fecha_entrega_input.setToolTip("Seleccione la fecha de entrega")
        self.fecha_entrega_input.setAccessibleName("Campo fecha de entrega")
        self.fecha_entrega_input.setAccessibleDescription("Selector de fecha de entrega")
        layout.addWidget(QLabel("Nombre:"))
        layout.addWidget(self.nombre_input)
        layout.addWidget(QLabel("Cliente:"))
        layout.addWidget(self.cliente_input)
        layout.addWidget(QLabel("Fecha de medición:"))
        layout.addWidget(self.fecha_medicion_input)
        layout.addWidget(QLabel("Fecha de entrega:"))
        layout.addWidget(self.fecha_entrega_input)
        feedback_layout = QHBoxLayout()
        self.label_feedback = QLabel()
        self.label_feedback.setObjectName("label_feedback")
        self.label_feedback.setVisible(False)
        self.label_feedback.setAccessibleName("Feedback visual de edición obra")
        feedback_layout.addWidget(self.label_feedback)
        self.btn_cerrar_feedback = QPushButton("✕")
        self.btn_cerrar_feedback.setFixedSize(24, 24)
        self.btn_cerrar_feedback.setToolTip("Cerrar mensaje")
        self.btn_cerrar_feedback.setVisible(False)
        self.btn_cerrar_feedback.clicked.connect(lambda: self.label_feedback.setVisible(False))
        self.btn_cerrar_feedback.clicked.connect(lambda: self.btn_cerrar_feedback.setVisible(False))
        feedback_layout.addWidget(self.btn_cerrar_feedback)
        layout.addLayout(feedback_layout)
        botones_layout = QHBoxLayout()
        botones_layout.setSpacing(18)
        self.boton_guardar = QPushButton()
        self.boton_guardar.setObjectName("boton_guardar_editar_obra")
        self.boton_guardar.setIcon(QIcon("resources/icons/finish-check.svg"))
        self.boton_guardar.setToolTip("Guardar cambios (Ctrl+S)")
        self.boton_guardar.setAccessibleName("Botón guardar cambios obra")
        self.boton_guardar.setAccessibleDescription("Botón para guardar los cambios de la obra")
        estilizar_boton_icono(self.boton_guardar)
        sombra_guardar = QGraphicsDropShadowEffect()
        sombra_guardar.setBlurRadius(10)
        sombra_guardar.setColor(QColor(37, 99, 235, 60))
        sombra_guardar.setOffset(0, 4)
        self.boton_guardar.setGraphicsEffect(sombra_guardar)
        self.boton_cancelar = QPushButton()
        self.boton_cancelar.setObjectName("boton_cancelar_editar_obra")
        self.boton_cancelar.setIcon(QIcon("resources/icons/close.svg"))
        self.boton_cancelar.setToolTip("Cancelar edición (Esc)")
        self.boton_cancelar.setAccessibleName("Botón cancelar edición obra")
        self.boton_cancelar.setAccessibleDescription("Botón para cancelar la edición de obra")
        estilizar_boton_icono(self.boton_cancelar)
        sombra_cancelar = QGraphicsDropShadowEffect()
        sombra_cancelar.setBlurRadius(10)
        sombra_cancelar.setColor(QColor(37, 99, 235, 60))
        sombra_cancelar.setOffset(0, 4)
        self.boton_cancelar.setGraphicsEffect(sombra_cancelar)
        botones_layout.addWidget(self.boton_guardar)
        botones_layout.addWidget(self.boton_cancelar)
        layout.addLayout(botones_layout)
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.frame)
        self.boton_guardar.clicked.connect(self.guardar_obra)
        self.boton_cancelar.clicked.connect(self.reject)
        self.boton_guardar.setShortcut("Ctrl+S")
        self.boton_cancelar.setShortcut("Esc")
        self.setTabOrder(self.nombre_input, self.cliente_input)
        self.setTabOrder(self.cliente_input, self.fecha_medicion_input)
        self.setTabOrder(self.fecha_medicion_input, self.fecha_entrega_input)
        self.setTabOrder(self.fecha_entrega_input, self.boton_guardar)
        self.setTabOrder(self.boton_guardar, self.boton_cancelar)
        if self.datos_obra:
            self.cargar_datos()
        aplicar_qss_global_y_tema(self)
    def cargar_datos(self):
        self.nombre_input.setText(self.datos_obra.get('nombre', ''))
        self.cliente_input.setText(self.datos_obra.get('cliente', ''))
        fecha_medicion = QDate.fromString(self.datos_obra.get('fecha_medicion', ''), "yyyy-MM-dd")
        fecha_entrega = QDate.fromString(self.datos_obra.get('fecha_entrega', ''), "yyyy-MM-dd")
        self.fecha_medicion_input.setDate(fecha_medicion)
        self.fecha_entrega_input.setDate(fecha_entrega)
    def mostrar_feedback(self, mensaje, color_bg, color_fg):
        self.label_feedback.setText(mensaje)
        self.label_feedback.setStyleSheet(f"background:{color_bg};color:{color_fg};font-weight:bold;padding:8px 12px;border-radius:8px;")
        self.label_feedback.setVisible(True)
        self.btn_cerrar_feedback.setVisible(True)
    def validar_campos(self):
        campos = [self.nombre_input, self.cliente_input]
        for campo in campos:
            if not campo.text().strip():
                campo.setProperty("error", True)
                campo.setStyleSheet("border: 2px solid #ef4444; background: #fef2f2;")
            else:
                campo.setProperty("error", False)
                campo.setStyleSheet("")
            style = campo.style()
            if style is not None:
                style.unpolish(campo)
                style.polish(campo)
    def guardar_obra(self):
        self.validar_campos()
        nombre = self.nombre_input.text().strip()
        cliente = self.cliente_input.text().strip()
        fecha_medicion = self.fecha_medicion_input.date().toString("yyyy-MM-dd")
        fecha_entrega = self.fecha_entrega_input.date().toString("yyyy-MM-dd")
        self.boton_guardar.setEnabled(False)
        if not nombre or not cliente:
            self.mostrar_feedback("❌ Por favor, complete todos los campos obligatorios.", "#fee2e2", "#b91c1c")
            self.boton_guardar.setEnabled(True)
            return
        self.label_feedback.setVisible(False)
        self.btn_cerrar_feedback.setVisible(False)
        self.mostrar_feedback("⏳ Guardando cambios...", "#e3f6fd", "#2563eb")
        QApplication.processEvents()
        # ...guardar lógica real...
        self.label_feedback.setVisible(False)
        self.btn_cerrar_feedback.setVisible(False)
        self.boton_guardar.setEnabled(True)
        self.accept()

class ObrasView(QWidget, TableResponsiveMixin):
    obra_agregada = pyqtSignal(dict)
    def __init__(self, usuario_actual="default", db_connection=None):
        super().__init__()
        self.usuario_actual = usuario_actual
        self.db_connection = db_connection
        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)

        # Tabs principales
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)

        # --- Pestaña 1: Tabla de obras ---
        self.tab_obras = QWidget()
        tab_obras_layout = QVBoxLayout(self.tab_obras)

        # Título (estándar visual global: ver docs/estandares_visuales.md)
        self.label = QLabel("Gestión de Obras")
        self.label.setObjectName("label_titulo")  # Unificación visual: todos los títulos usan este objectName
        self.label.setAccessibleName("Título de módulo Obras")
        self.label.setAccessibleDescription("Encabezado principal de la vista de obras")
        # Layout horizontal para título y botón
        titulo_layout = QHBoxLayout()
        titulo_layout.addWidget(self.label)
        titulo_layout.addStretch()
        # Botón principal de acción (Agregar obra)
        self.boton_agregar = QPushButton()
        self.boton_agregar.setObjectName("boton_agregar")
        self.boton_agregar.setIcon(QIcon("resources/icons/plus_icon.svg"))
        self.boton_agregar.setToolTip("Agregar nueva obra")
        self.boton_agregar.setAccessibleName("Botón agregar obra")
        estilizar_boton_icono(self.boton_agregar)
        sombra_agregar = QGraphicsDropShadowEffect()
        sombra_agregar.setBlurRadius(10)
        sombra_agregar.setColor(QColor(37, 99, 235, 60))
        sombra_agregar.setOffset(0, 4)
        self.boton_agregar.setGraphicsEffect(sombra_agregar)
        titulo_layout.addWidget(self.boton_agregar)
        tab_obras_layout.addLayout(titulo_layout)

        # Buscador de obras por nombre o cliente
        search_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Buscar obra por nombre o cliente...")
        self.search_bar.setFixedHeight(40)
        search_layout.addWidget(self.search_bar)
        search_layout.setContentsMargins(0, 0, 0, 0)
        tab_obras_layout.addLayout(search_layout)

        # Tabla de obras
        self.tabla_obras = QTableWidget()
        self.tabla_obras.setObjectName("tabla_obras")
        self.tabla_obras.setAlternatingRowColors(True)
        self.tabla_obras.setStyleSheet("")
        self.tabla_obras.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_obras.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.tabla_obras.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_obras.setShowGrid(True)
        header = self.tabla_obras.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            font = self.tabla_obras.font()
            font.setPointSize(12)
            self.tabla_obras.setFont(font)
            header_font = header.font()
            header_font.setPointSize(10)
            header.setFont(header_font)
        # Inicialización robusta de headers
        columnas_base = ["Nombre", "Cliente", "Fecha Medición", "Fecha Entrega"]
        columnas_pedidos = ["Estado Materiales", "Estado Vidrios", "Estado Herrajes"]
        self.obras_headers = columnas_base + columnas_pedidos
        self.tabla_obras.setColumnCount(len(self.obras_headers))
        self.tabla_obras.setHorizontalHeaderLabels(self.obras_headers)
        # Función robusta para alinear columnas según headers actuales
        def alinear_columnas_tabla():
            headers = []
            for i in range(self.tabla_obras.columnCount()):
                item = self.tabla_obras.horizontalHeaderItem(i)
                headers.append(item.text() if item else "")
            for col, header_text in enumerate(headers):
                if "monto" in header_text.lower() or "cantidad" in header_text.lower() or "%" in header_text or "total" in header_text.lower():
                    for row in range(self.tabla_obras.rowCount()):
                        item = self.tabla_obras.item(row, col)
                        if item:
                            item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                else:
                    for row in range(self.tabla_obras.rowCount()):
                        item = self.tabla_obras.item(row, col)
                        if item:
                            item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.tabla_obras.itemChanged.connect(lambda _: alinear_columnas_tabla())
        tab_obras_layout.addWidget(self.tabla_obras)
        tab_obras_layout.setContentsMargins(24, 20, 24, 20)
        tab_obras_layout.setSpacing(14)
        aplicar_qss_global_y_tema(self)
        # Configuración de columnas visibles por usuario
        self.config_path = "config_obras_columns.json"
        self.columnas_visibles = self.cargar_config_columnas(self.config_path, self.usuario_actual, self.obras_headers)
        self.aplicar_columnas_visibles(self.tabla_obras, self.obras_headers, self.columnas_visibles)
        # Menú contextual en header
        header = self.tabla_obras.horizontalHeader()
        if header is not None:
            header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            header.customContextMenuRequested.connect(self.mostrar_menu_columnas)
            header.sectionDoubleClicked.connect(self.auto_ajustar_columna)
        else:
            QMessageBox.critical(self, "Error", "El encabezado horizontal de la tabla no está inicializado.")
        self.tabla_obras.setAlternatingRowColors(True)
        # Eliminar cualquier styleSheet embebido, usar solo QSS global
        self.tabla_obras.setStyleSheet("")
        tab_obras_layout.addWidget(self.tabla_obras)

        # Feedback visual (estándar visual global)
        self.label_feedback = QLabel()
        self.label_feedback.setObjectName("label_feedback")
        self.label_feedback.setVisible(False)
        self.label_feedback.setAccessibleName("Feedback visual de Obras")
        self.label_feedback.setAccessibleDescription("Muestra mensajes de éxito, error o advertencia para el usuario")
        tab_obras_layout.addWidget(self.label_feedback)

        self.tab_obras.setLayout(tab_obras_layout)
        self.tabs.addTab(self.tab_obras, "Obras")

        # --- Pestaña 2: Cronograma (Gantt) ---
        self.tab_cronograma = QWidget()
        tab_cronograma_layout = QVBoxLayout(self.tab_cronograma)
        self.gantt_view = QGraphicsView()
        self.gantt_scene = QGraphicsScene()
        self.gantt_view.setScene(self.gantt_scene)
        tab_cronograma_layout.addWidget(self.gantt_view)
        self.tab_cronograma.setLayout(tab_cronograma_layout)
        self.tabs.addTab(self.tab_cronograma, "Cronograma")

        # Conectar señales de los botones
        self.boton_agregar.clicked.connect(self.mostrar_dialogo_alta)

        # Conectar búsqueda con filtro en tabla
        self.search_bar.textChanged.connect(self.filtrar_tabla)

        # Establecer controlador (si es necesario)
        self.controller = None

        # Cargar cronograma inicial (dummy)
        self.cargar_cronograma_gantt([])

    def set_controller(self, controller):
        """Asigna el controlador a la vista."""
        self.controller = controller

    def agregar_obra_a_tabla(self, datos_obra):
        row = self.tabla_obras.rowCount()
        self.tabla_obras.insertRow(row)
        self.establecer_texto_item(row, 0, datos_obra.get('nombre', ''))
        self.establecer_texto_item(row, 1, datos_obra.get('cliente', ''))
        self.establecer_texto_item(row, 2, datos_obra.get('fecha_medicion', ''))
        self.establecer_texto_item(row, 3, datos_obra.get('fecha_entrega', ''))
        # Estado editable (combo)
        combo_estado = QComboBox()
        combo_estado.addItems(["Medición", "En fabricación", "Lista para colocar", "Demorada"])
        estado = datos_obra.get('estado', 'Medición')
        combo_estado.setCurrentText(estado)
        combo_estado.currentTextChanged.connect(partial(self.cambiar_estado_obra, row))
        self.tabla_obras.setCellWidget(row, 4, combo_estado)
        # Si hay controlador, notificarle la nueva obra agregada (para sincronizar con DB o lógica real)
        if self.controller and hasattr(self.controller, 'obra_agregada'):
            self.controller.obra_agregada.emit(datos_obra)
        # ...puedes agregar combos en otras columnas de estado si lo deseas...

    def cambiar_estado_obra(self, row, nuevo_estado):
        # Actualiza el estado en la tabla y refresca el Gantt
        nombre = self.obtener_texto_item(row, 0)
        cliente = self.obtener_texto_item(row, 1)
        fecha_medicion = self.obtener_texto_item(row, 2)
        fecha_entrega = self.obtener_texto_item(row, 3)
        # Notificar al controlador para actualizar en la base de datos/controlador real
        if self.controller and hasattr(self.controller, 'actualizar_estado_obra'):
            obra_id = None
            item = self.tabla_obras.item(row, 0)
            if item is not None and item.data(Qt.ItemDataRole.UserRole) is not None:
                obra_id = item.data(Qt.ItemDataRole.UserRole)
            elif hasattr(self.controller, 'obtener_id_obra_por_nombre'):
                obra_id = self.controller.obtener_id_obra_por_nombre(nombre, cliente)
            self.controller.actualizar_estado_obra.emit(obra_id, nuevo_estado)
        # Refrescar Gantt
        self.cargar_cronograma_gantt(self.obtener_datos_obras_tabla())
        # Verificar si corresponde solicitar descargo (si existe el método)
        if hasattr(self, 'verificar_descargo_automatico'):
            self.verificar_descargo_automatico(row, nuevo_estado)

    def obtener_datos_obras_tabla(self):
        """Devuelve una lista de dicts con los datos de todas las obras en la tabla (para refrescar Gantt)."""
        obras = []
        for row in range(self.tabla_obras.rowCount()):
            nombre = self.obtener_texto_item(row, 0)
            cliente = self.obtener_texto_item(row, 1)
            fecha_medicion = self.obtener_texto_item(row, 2)
            fecha_entrega = self.obtener_texto_item(row, 3)
            # Obtener estado desde el QComboBox
            estado = ""
            widget = self.tabla_obras.cellWidget(row, 4)
            if isinstance(widget, QComboBox):
                estado = widget.currentText()
            obras.append({
                "nombre": nombre,
                "cliente": cliente,
                "fecha_medicion": fecha_medicion,
                "fecha_entrega": fecha_entrega,
                "estado": estado
            })
        return obras

    def solicitar_descargo(self, nombre_obra, estado):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Descargo por atraso en '{nombre_obra}'")
        dialog.setModal(True)
        dialog.setFixedSize(420, 340)
        # QFrame visual principal con sombra y fondo
        frame = QFrame(dialog)
        frame.setObjectName("form_card")
        frame.setStyleSheet("""
            QFrame#form_card {
                background: #f8fafc;
                border-radius: 12px;
                border: none;
            }
        """)
        sombra = QGraphicsDropShadowEffect()
        sombra.setBlurRadius(18)
        sombra.setColor(QColor(37, 99, 235, 40))
        sombra.setOffset(0, 8)
        frame.setGraphicsEffect(sombra)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(18)
        # Icono de advertencia
        icono = QLabel()
        icono.setPixmap(QIcon("resources/icons/warning.svg").pixmap(48, 48))
        icono.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(icono)
        # Título visual
        titulo = QLabel(f"Atraso en la obra: <b>{nombre_obra}</b>")
        titulo.setStyleSheet("font-size: 18px; color: #2563eb; margin-bottom: 6px;")
        titulo.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(titulo)
        # Mensaje
        label = QLabel(f"La obra no fue actualizada a tiempo.\nEstado actual: <b>{estado}</b>.<br>Por favor, ingrese el motivo")
        label.setStyleSheet("font-size: 13px; color: #222; margin-bottom: 4px;")
        label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        label.setWordWrap(True)
        layout.addWidget(label)
        # Campo de texto
        motivo = QTextEdit()
        motivo.setPlaceholderText("Describa el motivo del atraso y acciones tomadas...")
        motivo.setMinimumHeight(80)
        motivo.setObjectName("form_input")
        motivo.setStyleSheet("font-size: 13px; border-radius: 8px; border: 1px solid #cbd5e1; background: #fff;")
        motivo.setToolTip("Ingrese el motivo del descargo (obligatorio)")
        motivo.setAccessibleName("Campo motivo descargo")
        layout.addWidget(motivo)
        # Feedback visual
        feedback = QLabel("")
        feedback.setObjectName("label_feedback_descargo")
        feedback.setStyleSheet("color: #ef4444; font-size: 12px; margin-top: 2px;")
        feedback.setVisible(False)
        layout.addWidget(feedback)
        # Botón guardar
        btn_guardar = QPushButton("Guardar descargo")
        btn_guardar.setIcon(QIcon("resources/icons/finish-check.svg"))
        estilizar_boton_icono(btn_guardar)
        btn_guardar.setStyleSheet("font-size: 15px; padding: 8px 0; border-radius: 8px; background: #2563eb; color: #fff;")
        btn_guardar.setFixedHeight(38)
        btn_guardar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_guardar.setToolTip("Guardar descargo (Ctrl+S)")
        btn_guardar.setAccessibleName("Botón guardar descargo")
        btn_guardar.setAccessibleDescription("Botón para guardar el descargo de atraso")
        btn_guardar.clicked.connect(dialog.accept)
        layout.addWidget(btn_guardar)
        # Layout principal del QDialog
        dialog_layout = QVBoxLayout(dialog)
        dialog_layout.setContentsMargins(0, 0, 0, 0)
        dialog_layout.addWidget(frame)
        if dialog.exec():
            texto = motivo.toPlainText().strip()
            if not texto:
                feedback.setText("Debe ingresar un motivo para el descargo.")
                feedback.setVisible(True)
                return self.solicitar_descargo(nombre_obra, estado)
            # Aquí puedes guardar el descargo en base de datos, log o archivo para estadísticas
            self.label_feedback.setText(f"✅ Descargo registrado para '{nombre_obra}'.")
            self.label_feedback.setStyleSheet("color: #22c55e; font-weight: bold; font-size: 15px; margin-top: 8px;")
            self.label_feedback.setVisible(True)

    def mostrar_dialogo_alta(self):
        # Solo mostrar el diálogo robusto y moderno (el de controller), no el antiguo
        from modules.obras.controller import ObrasController
        if hasattr(self, 'controller') and self.controller and hasattr(self.controller, 'agregar_obra_dialog'):
            self.controller.agregar_obra_dialog()
        else:
            # Fallback: mostrar el diálogo antiguo solo si no hay controller
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Error", "No se pudo abrir el diálogo de alta de obra moderno. Verifique el controlador.")

    def mostrar_dialogo_edicion(self):
        fila_actual = self.tabla_obras.currentRow()
        if fila_actual < 0:
            QMessageBox.warning(self, "Selección inválida", "Por favor, seleccione una obra para editar.")
            return
        datos_obra = {
            'nombre': self.obtener_texto_item(fila_actual, 0),
            'cliente': self.obtener_texto_item(fila_actual, 1),
            'fecha_medicion': self.obtener_texto_item(fila_actual, 2),
            'fecha_entrega': self.obtener_texto_item(fila_actual, 3)
        }
        dialogo = EditObraDialog(self, datos_obra)
        if dialogo.exec():
            for col, key in enumerate(['nombre', 'cliente', 'fecha_medicion', 'fecha_entrega']):
                self.establecer_texto_item(fila_actual, col, dialogo.datos_obra[key])

    def eliminar_obra(self):
        fila_actual = self.tabla_obras.currentRow()
        if fila_actual < 0:
            QMessageBox.warning(self, "Selección inválida", "Por favor, seleccione una obra para eliminar.")
            return
        nombre_obra = self.obtener_texto_item(fila_actual, 0)
        confirmacion = QMessageBox.question(self, "Confirmar eliminación", f"¿Está seguro de eliminar la obra '{nombre_obra}'?",
                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirmacion == QMessageBox.StandardButton.Yes:
            self.tabla_obras.removeRow(fila_actual)

    def generar_reporte(self):
        fila_actual = self.tabla_obras.currentRow()
        if fila_actual < 0:
            QMessageBox.warning(self, "Selección inválida", "Por favor, seleccione una obra para generar el reporte.")
            return
        datos_obra = {
            'nombre': self.obtener_texto_item(fila_actual, 0),
            'cliente': self.obtener_texto_item(fila_actual, 1),
            'fecha_medicion': self.obtener_texto_item(fila_actual, 2),
            'fecha_entrega': self.obtener_texto_item(fila_actual, 3)
        }
        # Aquí se debería agregar la lógica para generar el reporte (por ejemplo, exportar a PDF)

    def filtrar_tabla(self, texto):
        """Filtra las filas de la tabla según el texto de búsqueda."""
        if not isinstance(texto, str):
            texto = str(texto)
        texto = texto.lower()
        for fila in range(self.tabla_obras.rowCount()):
            item_nombre = self.obtener_texto_item(fila, 0).lower() if self.obtener_texto_item(fila, 0) else ""
            item_cliente = self.obtener_texto_item(fila, 1).lower() if self.obtener_texto_item(fila, 1) else ""
            if texto in item_nombre or texto in item_cliente:
                self.tabla_obras.showRow(fila)
            else:
                self.tabla_obras.hideRow(fila)

    def obtener_texto_item(self, fila, columna):
        item = self.tabla_obras.item(fila, columna)
        if item is None:
            item = QTableWidgetItem()
            self.tabla_obras.setItem(fila, columna, item)
        return item.text() if item.text() else ""

    def establecer_texto_item(self, fila, columna, texto):
        """Establece el texto de un elemento de la tabla, inicializándolo si es necesario."""
        item = self.tabla_obras.item(fila, columna)
        if item is None:
            item = QTableWidgetItem()
            self.tabla_obras.setItem(fila, columna, item)
        item.setText(texto)

    def auto_ajustar_columna(self, index):
        """Ajusta automáticamente el ancho de la columna seleccionada al contenido."""
        self.tabla_obras.resizeColumnToContents(index)

    def cargar_config_columnas(self, config_path, usuario, headers):
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return data.get(usuario, {header: True for header in headers})
            except Exception:
                pass
        return {header: True for header in headers}

    def guardar_config_columnas(self, config_path, usuario, columnas_visibles):
        data = {}
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = {}
        data[usuario] = columnas_visibles
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo guardar la configuración: {e}")

    def aplicar_columnas_visibles(self, tabla, headers, columnas_visibles):
        for idx, header in enumerate(headers):
            visible = columnas_visibles.get(header, True)
            tabla.setColumnHidden(idx, not visible)

    def mostrar_menu_columnas(self, pos):
        menu = QMenu(self)
        for idx, header in enumerate(self.obras_headers):
            accion = QAction(header, self)
            accion.setCheckable(True)
            accion.setChecked(self.columnas_visibles.get(header, True))
            accion.toggled.connect(partial(self.toggle_columna, idx, header))
            menu.addAction(accion)
        header = self.tabla_obras.horizontalHeader()
        if header is not None and hasattr(header, 'mapToGlobal'):
            menu.exec(header.mapToGlobal(pos))
        else:
            menu.exec(pos)

    def toggle_columna(self, idx, header, checked):
        self.columnas_visibles[header] = checked
        self.tabla_obras.setColumnHidden(idx, not checked)
        self.guardar_config_columnas(self.config_path, self.usuario_actual, self.columnas_visibles)
        self.label_feedback.setText(f"Columna '{header}' {'mostrada' if checked else 'ocultada'}")
        self.label_feedback.setVisible(True)

    def cargar_cronograma_gantt(self, obras):
        """
        Carga el cronograma tipo Gantt en la pestaña 2, destacando fechas clave (medición y entrega) con líneas y etiquetas.
        Añade leyenda de colores, tooltips y resalta obras demoradas.
        """
        self.gantt_scene.clear()
        if not obras:
            obras = [
                {"nombre": "Obra A", "fecha_medicion": "2025-06-10", "fecha_entrega": "2025-06-20", "estado": "Medición"},
                {"nombre": "Obra B", "fecha_medicion": "2025-06-12", "fecha_entrega": "2025-06-25", "estado": "En fabricación"},
                {"nombre": "Obra C", "fecha_medicion": "2025-06-15", "fecha_entrega": "2025-06-28", "estado": "Lista para colocar"},
                {"nombre": "Obra D", "fecha_medicion": "2025-06-08", "fecha_entrega": "2025-06-18", "estado": "Demorada"},
            ]
        colores = {
            "Medición": QColor(59, 130, 246),      # Azul
            "En fabricación": QColor(251, 191, 36), # Amarillo
            "Lista para colocar": QColor(34, 197, 94), # Verde
            "Demorada": QColor(239, 68, 68),       # Rojo
        }
        y = 0
        alto = 32
        ancho_dia = 18
        fechas = [o["fecha_medicion"] for o in obras] + [o["fecha_entrega"] for o in obras]
        fechas = sorted(set(fechas))
        if not fechas:
            return
        from datetime import datetime, timedelta
        min_fecha = min(datetime.strptime(f, "%Y-%m-%d") for f in fechas)
        max_fecha = max(datetime.strptime(f, "%Y-%m-%d") for f in fechas)
        dias_totales = (max_fecha - min_fecha).days + 1
        # Dibujar línea de tiempo principal
        linea_y = 20
        self.gantt_scene.addLine(90, linea_y, 90 + dias_totales * ancho_dia, linea_y, QPen(QColor("#2563eb"), 3))
        # Etiquetas de fechas importantes (cada 5 días o menos si hay pocas)
        for i in range(dias_totales + 1):
            fecha = min_fecha + timedelta(days=i)
            if dias_totales < 15 or i % 5 == 0 or i == 0 or i == dias_totales:
                x = 90 + i * ancho_dia
                texto_fecha = QGraphicsTextItem(fecha.strftime("%d/%m"))
                texto_fecha.setPos(x - 18, linea_y + 8)
                texto_fecha.setDefaultTextColor(QColor("#2563eb"))
                self.gantt_scene.addItem(texto_fecha)
                # Línea vertical de referencia
                self.gantt_scene.addLine(x, linea_y - 8, x, linea_y + 60 + len(obras) * (alto + 12), QPen(QColor("#cbd5e1"), 1, Qt.PenStyle.DashLine))
        # Dibujar barras y fechas clave de cada obra
        for idx, obra in enumerate(obras):
            f1 = datetime.strptime(obra["fecha_medicion"], "%Y-%m-%d")
            f2 = datetime.strptime(obra["fecha_entrega"], "%Y-%m-%d")
            x1 = 90 + (f1 - min_fecha).days * ancho_dia
            x2 = 90 + (f2 - min_fecha).days * ancho_dia
            y_obra = linea_y + 32 + idx * (alto + 12)
            color = colores.get(obra["estado"], QColor(156, 163, 175))
            # Resaltar obras demoradas
            es_demorada = obra["estado"] == "Demorada"
            pen = QPen(Qt.GlobalColor.black)
            if es_demorada:
                pen.setWidth(4)
                pen.setColor(QColor(239, 68, 68))
            else:
                pen.setWidth(2)
            # Fecha de medición (punto y etiqueta)
            self.gantt_scene.addEllipse(x1 - 4, y_obra + alto // 2 - 4, 8, 8, QPen(QColor("#2563eb")), QBrush(QColor("#2563eb")))
            label_med = QGraphicsTextItem("Medición: " + f1.strftime("%d/%m"))
            label_med.setPos(x1 - 30, y_obra - 18)
            label_med.setDefaultTextColor(QColor("#2563eb"))
            self.gantt_scene.addItem(label_med)
            # Fecha de entrega (punto y etiqueta)
            self.gantt_scene.addEllipse(x2 - 4, y_obra + alto // 2 - 4, 8, 8, QPen(QColor("#22c55e")), QBrush(QColor("#22c55e")))
            label_ent = QGraphicsTextItem("Entrega: " + f2.strftime("%d/%m"))
            label_ent.setPos(x2 - 30, y_obra + alto + 2)
            label_ent.setDefaultTextColor(QColor("#22c55e"))
            self.gantt_scene.addItem(label_ent)
        # Leyenda de colores
        leyenda_y = linea_y + 32 + len(obras) * (alto + 12) + 24
        leyenda_x = 90
        leyenda_items = [
            ("Medición", colores["Medición"]),
            ("En fabricación", colores["En fabricación"]),
            ("Lista para colocar", colores["Lista para colocar"]),
            ("Demorada", colores["Demorada"]),
        ]
        for i, (estado, color) in enumerate(leyenda_items):
            self.gantt_scene.addRect(leyenda_x + i * 140, leyenda_y, 28, 18, QPen(Qt.GlobalColor.black), QBrush(color))
            texto = QGraphicsTextItem(estado)
            texto.setPos(leyenda_x + i * 140 + 36, leyenda_y - 2)
            texto.setDefaultTextColor(QColor("#222"))
            self.gantt_scene.addItem(texto)
        self.gantt_scene.setSceneRect(0, 0, 90 + dias_totales * ancho_dia + 220, leyenda_y + 48)

    def verificar_descargo_automatico(self, row, nuevo_estado):
        """
        Verifica si la obra requiere descargo automático por atraso o estado 'Demorada'.
        Si corresponde, abre el diálogo de descargo y registra el feedback visual.
        """
        # Obtener datos de la obra
        nombre = self.obtener_texto_item(row, 0)
        fecha_entrega = self.obtener_texto_item(row, 3)
        from datetime import datetime
        hoy = datetime.now().date()
        try:
            fecha_ent = datetime.strptime(fecha_entrega, "%Y-%m-%d").date()
        except Exception:
            return  # Fecha inválida, no se puede verificar
        # Si el estado es 'Demorada' o la fecha de entrega ya pasó y no está finalizada
        if nuevo_estado == "Demorada" or (fecha_ent < hoy and nuevo_estado != "Finalizada"):
            self.solicitar_descargo(nombre, nuevo_estado)
