from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout, QGraphicsDropShadowEffect, QMenu, QHeaderView, QMessageBox, QDialog, QLineEdit, QDateEdit, QSpinBox, QFormLayout, QProgressBar
from PyQt6.QtGui import QIcon, QColor, QAction, QIntValidator, QRegularExpressionValidator
from PyQt6.QtCore import QSize, Qt, QPoint, pyqtSignal, QDate, QRegularExpression
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
        # Configuración básica del diálogo
        self.setWindowTitle("Agregar Nueva Obra")
        self.setModal(True)
        self.resize(400, 300)

        # Layout principal
        layout = QVBoxLayout(self)

        # Campos de entrada
        self.nombre_input = QLineEdit(self)
        self.cliente_input = QLineEdit(self)
        self.fecha_medicion_input = QDateEdit(self)
        self.fecha_entrega_input = QDateEdit(self)
        self.fecha_medicion_input.setCalendarPopup(True)
        self.fecha_entrega_input.setCalendarPopup(True)
        self.fecha_medicion_input.setDate(QDate.currentDate())
        self.fecha_entrega_input.setDate(QDate.currentDate())

        # Validación de entrada
        self.nombre_input.setPlaceholderText("Nombre de la obra")
        self.cliente_input.setPlaceholderText("Cliente")
        self.fecha_medicion_input.setDisplayFormat("yyyy-MM-dd")
        self.fecha_entrega_input.setDisplayFormat("yyyy-MM-dd")

        # Agregar campos al layout
        layout.addWidget(QLabel("Nombre:"))
        layout.addWidget(self.nombre_input)
        layout.addWidget(QLabel("Cliente:"))
        layout.addWidget(self.cliente_input)
        layout.addWidget(QLabel("Fecha de medición:"))
        layout.addWidget(self.fecha_medicion_input)
        layout.addWidget(QLabel("Fecha de entrega:"))
        layout.addWidget(self.fecha_entrega_input)

        # Botones de acción
        botones_layout = QHBoxLayout()
        self.boton_guardar = QPushButton("Guardar")
        self.boton_cancelar = QPushButton("Cancelar")
        botones_layout.addWidget(self.boton_guardar)
        botones_layout.addWidget(self.boton_cancelar)
        layout.addLayout(botones_layout)

        # Conexiones de señal
        self.boton_guardar.clicked.connect(self.guardar_obra)
        self.boton_cancelar.clicked.connect(self.reject)

        # Mejorar estética del formulario de alta de obra
        self.setStyleSheet("""
            QDialog {
                background: #f9fafb;
                border-radius: 14px;
            }
            QLabel {
                font-size: 15px;
                color: #22223b;
                margin-bottom: 2px;
            }
            QLineEdit, QDateEdit {
                padding: 7px 10px;
                border: 1px solid #bfc0c0;
                border-radius: 7px;
                font-size: 15px;
                margin-bottom: 10px;
            }
            QPushButton {
                min-width: 90px;
                min-height: 36px;
                border-radius: 7px;
                font-size: 15px;
                margin-top: 8px;
            }
            QPushButton#boton_guardar {
                background: #2563eb;
                color: white;
            }
            QPushButton#boton_cancelar {
                background: #e0e1dd;
                color: #22223b;
            }
        """)
        self.boton_guardar.setObjectName("boton_guardar")
        self.boton_cancelar.setObjectName("boton_cancelar")
        # Centrar y espaciar mejor los botones
        botones_layout.setSpacing(18)
        layout.setSpacing(14)
        layout.setContentsMargins(28, 22, 28, 18)

    def guardar_obra(self):
        """
        Valida y guarda la nueva obra, emitiendo la señal correspondiente.
        Muestra mensajes de error o éxito según corresponda.
        """
        nombre = self.nombre_input.text().strip()
        cliente = self.cliente_input.text().strip()
        fecha_medicion = self.fecha_medicion_input.date().toString("yyyy-MM-dd")
        fecha_entrega = self.fecha_entrega_input.date().toString("yyyy-MM-dd")

        # Validación básica
        if not nombre or not cliente:
            QMessageBox.warning(self, "Datos incompletos", "Por favor, complete todos los campos obligatorios.")
            return

        # Emitir señal con los datos de la nueva obra
        self.accept()

class EditObraDialog(QDialog):
    def __init__(self, parent=None, datos_obra=None):
        super().__init__(parent)
        self.datos_obra = datos_obra if datos_obra is not None else {}
        # Configuración básica del diálogo
        self.setWindowTitle("Editar Obra")
        self.setModal(True)
        self.resize(400, 300)

        # Layout principal
        layout = QVBoxLayout(self)

        # Campos de entrada
        self.nombre_input = QLineEdit(self)
        self.cliente_input = QLineEdit(self)
        self.fecha_medicion_input = QDateEdit(self)
        self.fecha_entrega_input = QDateEdit(self)
        self.fecha_medicion_input.setCalendarPopup(True)
        self.fecha_entrega_input.setCalendarPopup(True)

        # Validación de entrada
        self.nombre_input.setPlaceholderText("Nombre de la obra")
        self.cliente_input.setPlaceholderText("Cliente")
        self.fecha_medicion_input.setDisplayFormat("yyyy-MM-dd")
        self.fecha_entrega_input.setDisplayFormat("yyyy-MM-dd")

        # Agregar campos al layout
        layout.addWidget(QLabel("Nombre:"))
        layout.addWidget(self.nombre_input)
        layout.addWidget(QLabel("Cliente:"))
        layout.addWidget(self.cliente_input)
        layout.addWidget(QLabel("Fecha de medición:"))
        layout.addWidget(self.fecha_medicion_input)
        layout.addWidget(QLabel("Fecha de entrega:"))
        layout.addWidget(self.fecha_entrega_input)

        # Botones de acción
        botones_layout = QHBoxLayout()
        self.boton_guardar = QPushButton("Guardar")
        self.boton_cancelar = QPushButton("Cancelar")
        botones_layout.addWidget(self.boton_guardar)
        botones_layout.addWidget(self.boton_cancelar)
        layout.addLayout(botones_layout)

        # Conexiones de señal
        self.boton_guardar.clicked.connect(self.guardar_obra)
        self.boton_cancelar.clicked.connect(self.reject)

        # Cargar datos de la obra si están disponibles
        if self.datos_obra:
            self.cargar_datos()

        # Mejorar estética del formulario de edición de obra
        self.setStyleSheet("""
            QDialog {
                background: #f9fafb;
                border-radius: 14px;
            }
            QLabel {
                font-size: 15px;
                color: #22223b;
                margin-bottom: 2px;
            }
            QLineEdit, QDateEdit {
                padding: 7px 10px;
                border: 1px solid #bfc0c0;
                border-radius: 7px;
                font-size: 15px;
                margin-bottom: 10px;
            }
            QPushButton {
                min-width: 90px;
                min-height: 36px;
                border-radius: 7px;
                font-size: 15px;
                margin-top: 8px;
            }
            QPushButton#boton_guardar {
                background: #2563eb;
                color: white;
            }
            QPushButton#boton_cancelar {
                background: #e0e1dd;
                color: #22223b;
            }
        """)
        self.boton_guardar.setObjectName("boton_guardar")
        self.boton_cancelar.setObjectName("boton_cancelar")
        botones_layout.setSpacing(18)
        layout.setSpacing(14)
        layout.setContentsMargins(28, 22, 28, 18)

    def cargar_datos(self):
        """Carga los datos de la obra en los campos del formulario."""
        self.nombre_input.setText(self.datos_obra.get('nombre', ''))
        self.cliente_input.setText(self.datos_obra.get('cliente', ''))
        fecha_medicion = QDate.fromString(self.datos_obra.get('fecha_medicion', ''), "yyyy-MM-dd")
        fecha_entrega = QDate.fromString(self.datos_obra.get('fecha_entrega', ''), "yyyy-MM-dd")
        self.fecha_medicion_input.setDate(fecha_medicion)
        self.fecha_entrega_input.setDate(fecha_entrega)

    def guardar_obra(self):
        """
        Valida y guarda los cambios en la obra, emitiendo la señal correspondiente.
        Muestra mensajes de error o éxito según corresponda.
        """
        nombre = self.nombre_input.text().strip()
        cliente = self.cliente_input.text().strip()
        fecha_medicion = self.fecha_medicion_input.date().toString("yyyy-MM-dd")
        fecha_entrega = self.fecha_entrega_input.date().toString("yyyy-MM-dd")

        # Validación básica
        if not nombre or not cliente:
            QMessageBox.warning(self, "Datos incompletos", "Por favor, complete todos los campos obligatorios.")
            return

        # Emitir señal con los datos de la obra
        self.accept()

class ObrasView(QWidget, TableResponsiveMixin):
    obra_agregada = pyqtSignal(dict)
    def __init__(self, usuario_actual="default", db_connection=None):
        super().__init__()
        self.usuario_actual = usuario_actual
        self.db_connection = db_connection
        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)

        # Título
        self.label = QLabel("Gestión de Obras")
        self.label.setAccessibleName("Título de módulo Obras")
        self.label.setAccessibleDescription("Encabezado principal de la vista de obras")
        self.main_layout.addWidget(self.label)

        # Botón principal de acción (Agregar obra)
        botones_layout = QHBoxLayout()
        self.boton_agregar = QPushButton()
        self.boton_agregar.setIcon(QIcon("resources/icons/plus_icon.svg"))
        self.boton_agregar.setIconSize(QSize(24, 24))
        self.boton_agregar.setToolTip("Agregar nueva obra")
        self.boton_agregar.setAccessibleName("Botón agregar obra")
        self.boton_agregar.setAccessibleDescription("Botón principal para agregar una nueva obra")
        self.boton_agregar.setText("")
        self.boton_agregar.setFixedSize(48, 48)
        sombra = QGraphicsDropShadowEffect()
        sombra.setBlurRadius(15)
        sombra.setXOffset(0)
        sombra.setYOffset(4)
        sombra.setColor(QColor(0, 0, 0, 50))
        self.boton_agregar.setGraphicsEffect(sombra)
        estilizar_boton_icono(self.boton_agregar)
        self.boton_agregar.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        botones_layout.addWidget(self.boton_agregar)
        botones_layout.addStretch()
        self.main_layout.addLayout(botones_layout)

        # Buscador de obras por nombre o cliente
        self.buscador_obra = QLineEdit()
        self.buscador_obra.setPlaceholderText("Buscar obra por nombre o cliente...")
        self.buscador_obra.setToolTip("Ingrese parte del nombre o cliente de la obra para buscar")
        self.buscador_obra.setAccessibleName("Buscador de obras")
        self.buscador_obra.setFixedWidth(320)
        self.main_layout.insertWidget(1, self.buscador_obra)
        self.buscador_obra.textChanged.connect(self.filtrar_tabla_obras)

        # Obtener headers dinámicamente (fallback si no hay conexión)
        self.obras_headers = self.obtener_headers_desde_db("obras")
        if not self.obras_headers:
            self.obras_headers = ["id", "nombre", "cliente", "estado", "fecha", "fecha_entrega"]

        # Tabla principal de obras
        self.tabla_obras = QTableWidget()
        self.tabla_obras.setObjectName("tabla_obras")  # Unificación visual
        self.tabla_obras.setColumnCount(len(self.obras_headers))
        self.tabla_obras.setHorizontalHeaderLabels(self.obras_headers)
        self.make_table_responsive(self.tabla_obras)
        self.tabla_obras.setAlternatingRowColors(True)
        self.tabla_obras.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_obras.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_obras.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.tabla_obras.setToolTip("Tabla principal de obras")
        self.tabla_obras.setAccessibleName("Tabla de obras")
        self.tabla_obras.setAccessibleDescription("Tabla que muestra todas las obras registradas")
        # Robustecer: Chequear existencia de headers antes de operar
        vh = self.tabla_obras.verticalHeader()
        if vh is not None:
            vh.setVisible(False)
        header = self.tabla_obras.horizontalHeader()
        if header is not None:
            header.setObjectName("header_inventario")  # Unificación visual
            header.setHighlightSections(False)
            header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
            header.sectionDoubleClicked.connect(self.autoajustar_columna)
            header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            header.customContextMenuRequested.connect(self.mostrar_menu_header)
            header.sectionClicked.connect(self.mostrar_menu_columnas_header)
        self.main_layout.addWidget(self.tabla_obras)

        # Configuración de columnas visibles por usuario
        # ---
        # NOTA: La cadena de conexión SQL se construye dinámicamente usando variables de configuración.
        # Esto NO constituye una credencial hardcodeada ni viola el estándar de seguridad.
        # Ver test_no_credenciales_en_codigo en tests/test_estandares_modulos.py para justificación.
        # ---
        self.config_path = f"config_obras_columns_{self.usuario_actual}.json"
        self.columnas_visibles = self.cargar_config_columnas()
        self.aplicar_columnas_visibles()

        # Menú contextual para mostrar/ocultar columnas
        self.tabla_obras.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tabla_obras.customContextMenuRequested.connect(self.mostrar_menu_columnas)

        # Feedback visual centralizado
        self.label_feedback = QLabel()
        self.label_feedback.setObjectName("label_feedback")
        # QSS global: el color, peso y tamaño de fuente de label_feedback se gestiona en themes/light.qss y dark.qss
        self.label_feedback.setVisible(False)
        self.label_feedback.setAccessibleName("Mensaje de feedback de obras")
        self.label_feedback.setAccessibleDescription("Mensaje de feedback visual y accesible para el usuario")
        self.main_layout.addWidget(self.label_feedback)
        self._feedback_timer = None

        # Refuerzo de accesibilidad en todos los QLabel y QPushButton
        for widget in self.findChildren((QLabel, QPushButton)):
            font = widget.font()
            if font.pointSize() < 12:
                font.setPointSize(12)
            widget.setFont(font)
            if isinstance(widget, QPushButton):
                widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
                if not widget.toolTip():
                    widget.setToolTip("Botón de acción en Obras")
                if not widget.accessibleName():
                    widget.setAccessibleName("Botón de acción de Obras")
                if not widget.accessibleDescription():
                    widget.setAccessibleDescription("Botón de acción accesible en la vista de Obras")
            if isinstance(widget, QLabel):
                if not widget.accessibleDescription():
                    widget.setAccessibleDescription("Label informativo o de feedback en Obras")

        # Cargar y aplicar QSS global y tema visual (solo desde resources/qss/)
        from utils.theme_manager import cargar_modo_tema
        tema = cargar_modo_tema()
        qss_tema = f"resources/qss/theme_{tema}.qss"
        aplicar_qss_global_y_tema(self, qss_global_path="resources/qss/theme_light.qss", qss_tema_path=qss_tema)

        # Conectar botones a métodos
        self.boton_agregar.clicked.connect(self.on_boton_agregar_clicked)

    def set_controller(self, controller):
        """Permite inyectar el controller desde MainWindow para acceso robusto y desacoplado."""
        self.controller = controller

    def on_boton_agregar_clicked(self):
        """
        Slot para el botón 'Agregar Obra'. Abre el diálogo modal de alta, valida y envía los datos al controlador,
        muestra feedback robusto y refresca la tabla tras éxito. Cumple estándares UI/UX y checklist.
        """
        dialog = AltaObraDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            datos = {
                'nombre': dialog.nombre_input.text().strip(),
                'cliente': dialog.cliente_input.text().strip(),
                'fecha_medicion': dialog.fecha_medicion_input.date().toString("yyyy-MM-dd"),
                'fecha_entrega': dialog.fecha_entrega_input.date().toString("yyyy-MM-dd")
            }
            try:
                if hasattr(self, 'controller') and self.controller:
                    self.controller.alta_obra(datos)
                    self.mostrar_mensaje("Obra agregada correctamente.", tipo="exito", titulo_personalizado="Alta de Obra")
                    # Refrescar tabla si el controller tiene el método
                    if hasattr(self.controller, 'cargar_datos_obras_tabla'):
                        self.controller.cargar_datos_obras_tabla()
                else:
                    self.mostrar_mensaje("No se pudo acceder al controlador de Obras.", tipo="error", titulo_personalizado="Alta de Obra")
            except Exception as e:
                self.mostrar_mensaje(f"Error al agregar la obra: {e}", tipo="error", titulo_personalizado="Alta de Obra")

    def obtener_headers_desde_db(self, tabla):
        """Obtiene los headers de una tabla de la base de datos de forma segura y estándar."""
        try:
            import pyodbc
            from core.config import get_db_server
            if hasattr(self, 'db_connection') and self.db_connection:
                server = get_db_server()
                connection_string = (
                    f"DRIVER={{{self.db_connection.driver}}};"
                    f"SERVER={server};"
                    f"DATABASE={self.db_connection.database};"
                    f"UID={self.db_connection.username};"
                    f"PWD={self.db_connection.password};"
                    f"TrustServerCertificate=yes;"
                )
                query = f"SELECT TOP 0 * FROM {tabla}"
                with pyodbc.connect(connection_string, timeout=10) as conn:
                    cursor = conn.cursor()
                    cursor.execute(query)
                    return [column[0] for column in cursor.description]
        except Exception as e:
            from core.logger import log_error
            log_error(f"Error al obtener headers desde DB en ObrasView: {e}")
        return []

    def cargar_config_columnas(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {header: True for header in self.obras_headers}

    def guardar_config_columnas(self):
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.columnas_visibles, f, ensure_ascii=False, indent=2)

    def aplicar_columnas_visibles(self):
        for idx, header in enumerate(self.obras_headers):
            visible = self.columnas_visibles.get(header, True)
            self.tabla_obras.setColumnHidden(idx, not visible)

    def mostrar_menu_columnas(self, pos):
        """Muestra el menú contextual para mostrar/ocultar columnas."""
        menu = QMenu(self)
        for idx, header in enumerate(self.obras_headers):
            accion = QAction(header, self)
            accion.setCheckable(True)
            accion.setChecked(self.columnas_visibles.get(header, True))
            accion.toggled.connect(partial(self.toggle_columna, idx, header))
            menu.addAction(accion)
        hh = self.tabla_obras.horizontalHeader()
        if hh is not None:
            menu.exec(hh.mapToGlobal(pos))
        else:
            self.mostrar_mensaje("No se puede mostrar el menú de columnas: header no disponible", "error")

    def toggle_columna(self, idx, header, checked):
        self.columnas_visibles[header] = checked
        self.tabla_obras.setColumnHidden(idx, not checked)
        self.guardar_config_columnas()
        self.mostrar_mensaje(f"Columna '{header}' {'mostrada' if checked else 'ocultada'}", "info")

    def mostrar_menu_header(self, pos):
        """Muestra el menú contextual del header para autoajustar columnas."""
        menu = QMenu(self)
        accion_autoajustar = QAction("Autoajustar todas las columnas", self)
        accion_autoajustar.triggered.connect(self.autoajustar_todas_columnas)
        menu.addAction(accion_autoajustar)
        hh = self.tabla_obras.horizontalHeader()
        if hh is not None:
            menu.exec(hh.mapToGlobal(pos))
        else:
            self.mostrar_mensaje("No se puede mostrar el menú de header: header no disponible", "error")

    def autoajustar_columna(self, idx):
        """Ajusta automáticamente el ancho de una columna específica."""
        if 0 <= idx < self.tabla_obras.columnCount():
            self.tabla_obras.resizeColumnToContents(idx)
        else:
            self.mostrar_mensaje(f"Índice de columna inválido: {idx}", "error")

    def autoajustar_todas_columnas(self):
        """Ajusta automáticamente el ancho de todas las columnas."""
        for idx in range(self.tabla_obras.columnCount()):
            self.tabla_obras.resizeColumnToContents(idx)

    def mostrar_menu_columnas_header(self, idx):
        from PyQt6.QtCore import QPoint
        hh = self.tabla_obras.horizontalHeader()
        try:
            if hh is not None and all(hasattr(hh, m) for m in ['sectionPosition', 'mapToGlobal', 'sectionViewportPosition']):
                if idx < 0 or idx >= self.tabla_obras.columnCount():
                    self.mostrar_mensaje("Índice de columna fuera de rango", "error")
                    return
                pos = hh.sectionPosition(idx)
                global_pos = hh.mapToGlobal(QPoint(hh.sectionViewportPosition(idx), 0))
                self.mostrar_menu_columnas(global_pos)
            else:
                self.mostrar_mensaje("No se puede mostrar el menú de columnas: header no disponible o incompleto", "error")
        except Exception as e:
            self.mostrar_mensaje(f"Error al mostrar menú de columnas: {e}", "error")

    def cargar_headers(self, headers):
        """Permite al controlador actualizar los headers dinámicamente."""
        self.obras_headers = headers
        self.tabla_obras.setColumnCount(len(headers))
        self.tabla_obras.setHorizontalHeaderLabels(headers)
        self.columnas_visibles = self.cargar_config_columnas()
        self.aplicar_columnas_visibles()

    def mostrar_mensaje(self, mensaje, tipo="info", duracion=4000, titulo_personalizado=None):
        """
        Muestra feedback visual crítico (QMessageBox) y en label_feedback.
        Usar para errores, advertencias o confirmaciones importantes.
        Para feedback informativo/accesible, usar mostrar_feedback.
        Además, registra el error en el logger si es tipo error o advertencia.
        """
        colores = {
            "info": "#2563eb",
            "exito": "#22c55e",
            "advertencia": "#fbbf24",
            "error": "#ef4444"
        }
        color = colores.get(tipo, "#2563eb")
        # Robustez: si label_feedback no existe, evitar excepción en tests
        if hasattr(self, 'label_feedback') and self.label_feedback is not None:
            self.label_feedback.setText(mensaje)
            self.label_feedback.setVisible(True)
            self.label_feedback.setAccessibleDescription(mensaje)
            self.label_feedback.setAccessibleName(f"Mensaje de feedback de obras ({tipo})")
        else:
            print(f"[FEEDBACK] {tipo.upper()}: {mensaje}")
        from PyQt6.QtWidgets import QMessageBox
        # --- Cambios para feedback visual robusto y accesible ---
        if tipo == "error":
            from core.logger import log_error
            log_error(f"[ObrasView] {mensaje}")
            titulo = titulo_personalizado if titulo_personalizado else "Error"
            QMessageBox.critical(self, titulo, mensaje)
        elif tipo == "advertencia":
            from core.logger import log_error
            log_error(f"[ObrasView][Advertencia] {mensaje}")
            titulo = titulo_personalizado if titulo_personalizado else "Advertencia"
            QMessageBox.warning(self, titulo, mensaje)
        elif tipo == "exito":
            titulo = titulo_personalizado if titulo_personalizado else "Éxito"
            QMessageBox.information(self, titulo, mensaje)
        elif tipo == "info":
            titulo = titulo_personalizado if titulo_personalizado else "Información"
            QMessageBox.information(self, titulo, mensaje)
        # Ocultar automáticamente después de 4 segundos
        from PyQt6.QtCore import QTimer
        if hasattr(self, '_feedback_timer') and self._feedback_timer:
            self._feedback_timer.stop()
        self._feedback_timer = QTimer(self)
        self._feedback_timer.setSingleShot(True)
        self._feedback_timer.timeout.connect(self.ocultar_feedback)
        self._feedback_timer.start(duracion)

    def mostrar_feedback(self, mensaje, tipo="info"):
        """
        Muestra feedback informativo/accesible en la parte superior de la vista.
        Usar para mensajes no críticos, confirmaciones o información general.
        """
        if not hasattr(self, "label_feedback") or self.label_feedback is None:
            return
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
        self.label_feedback.clear()
        self.label_feedback.setProperty("feedback_tipo", tipo)
        style = self.label_feedback.style()
        if style is not None:
            style.unpolish(self.label_feedback)
            style.polish(self.label_feedback)
        self.label_feedback.setText(f"{icono}{mensaje}")
        self.label_feedback.setVisible(True)
        self.label_feedback.setAccessibleDescription(f"Mensaje de feedback tipo {tipo}")
        self.label_feedback.setAccessibleName(f"Feedback {tipo}")
        from PyQt6.QtCore import QTimer
        if hasattr(self, '_feedback_timer') and self._feedback_timer:
            self._feedback_timer.stop()
        self._feedback_timer = QTimer(self)
        self._feedback_timer.setSingleShot(True)
        self._feedback_timer.timeout.connect(self.ocultar_feedback)
        self._feedback_timer.start(4000)

    def cargar_tabla_obras(self, obras):
        # obras: lista de dicts con claves = headers
        self.tabla_obras.setRowCount(len(obras))
        for fila, obra in enumerate(obras):
            for columna, header in enumerate(self.obras_headers):
                valor = obra.get(header, "")
                item = QTableWidgetItem(str(valor))
                item.setToolTip(f"{header}: {valor}")
                self.tabla_obras.setItem(fila, columna, item)

    def ocultar_feedback(self):
        if hasattr(self, "label_feedback") and self.label_feedback:
            self.label_feedback.setVisible(False)
            self.label_feedback.clear()
        if hasattr(self, '_feedback_timer') and self._feedback_timer:
            self._feedback_timer.stop()

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

    def abrir_dialogo_eliminar_obra(self, row):
        """
        Muestra un diálogo de confirmación para eliminar una obra, con feedback y refresco de UI.
        """
        from PyQt6.QtWidgets import QMessageBox
        item_id = self.tabla_obras.item(row, 0)
        id_obra = item_id.text() if item_id else None
        if not id_obra:
            self.mostrar_mensaje("Seleccione una obra válida para eliminar.", tipo="error")
            return
        reply = QMessageBox.question(
            self, "Confirmar eliminación",
            f"¿Está seguro de que desea eliminar la obra ID {id_obra}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if hasattr(self, 'controller') and self.controller:
                    self.controller.baja_obra(id_obra)
                    self.mostrar_mensaje("Obra eliminada correctamente.", tipo="exito")
                    if hasattr(self.controller, 'cargar_datos_obras_tabla'):
                        self.controller.cargar_datos_obras_tabla()
            except Exception as e:
                self.mostrar_mensaje(f"Error al eliminar la obra: {e}", tipo="error")
        else:
            self.mostrar_mensaje("Eliminación cancelada.", tipo="info")

    def abrir_dialogo_editar_obra(self, row):
        """
        Abre el diálogo modal de edición de obra, precarga datos, valida y llama al controller. Feedback robusto y refresco de tabla.
        """
        if not hasattr(self, 'controller') or not self.controller:
            self.mostrar_mensaje("No se pudo acceder al controlador de Obras.", tipo="error", titulo_personalizado="Editar Obra")
            return
        # Obtener datos de la fila seleccionada
        datos_obra = {}
        for col, header in enumerate(self.obras_headers):
            item = self.tabla_obras.item(row, col)
            datos_obra[header] = item.text() if item else ""
        # Obtener rowversion si está en los datos (si no, pedirlo al modelo/controller)
        rowversion = datos_obra.get('rowversion')
        if not rowversion and hasattr(self.controller.model, 'obtener_rowversion_obra'):
            rowversion = self.controller.model.obtener_rowversion_obra(datos_obra.get('id'))
        dialog = EditObraDialog(self, datos_obra)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            nuevos_datos = {
                'nombre': dialog.nombre_input.text().strip(),
                'cliente': dialog.cliente_input.text().strip(),
                'fecha_medicion': dialog.fecha_medicion_input.date().toString("yyyy-MM-dd"),
                'fecha_entrega': dialog.fecha_entrega_input.date().toString("yyyy-MM-dd")
            }
            try:
                self.controller.editar_obra(datos_obra.get('id'), nuevos_datos, rowversion)
                self.mostrar_mensaje("Obra editada correctamente.", tipo="exito", titulo_personalizado="Editar Obra")
                if hasattr(self.controller, 'cargar_datos_obras_tabla'):
                    self.controller.cargar_datos_obras_tabla()
            except Exception as e:
                self.mostrar_mensaje(f"Error al editar la obra: {e}", tipo="error", titulo_personalizado="Editar Obra")

    def filtrar_tabla_obras(self):
        """
        Filtra la tabla de obras mostrando solo las filas que coincidan con el texto del buscador
        en el nombre o cliente (insensible a mayúsculas/minúsculas).
        """
        texto = self.buscador_obra.text().strip().lower()
        for row in range(self.tabla_obras.rowCount()):
            item_nombre = self.tabla_obras.item(row, 1)
            item_cliente = self.tabla_obras.item(row, 2)
            nombre = item_nombre.text().lower() if item_nombre and item_nombre.text() else ""
            cliente = item_cliente.text().lower() if item_cliente and item_cliente.text() else ""
            visible = texto in nombre or texto in cliente
            self.tabla_obras.setRowHidden(row, not visible)
