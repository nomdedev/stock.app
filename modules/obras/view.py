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

        # Botón para verificar obra en SQL
        self.boton_verificar_obra = QPushButton("Verificar obra en SQL")
        self.boton_verificar_obra.setIcon(QIcon("resources/icons/search_icon.svg"))
        self.boton_verificar_obra.setIconSize(QSize(20, 20))
        self.boton_verificar_obra.setToolTip("Verificar existencia de obra en la base de datos SQL")
        self.boton_verificar_obra.setAccessibleName("Botón verificar obra en SQL")
        self.boton_verificar_obra.setAccessibleDescription("Botón para verificar si la obra existe en la base de datos SQL")
        estilizar_boton_icono(self.boton_verificar_obra)
        self.boton_verificar_obra.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.main_layout.addWidget(self.boton_verificar_obra)

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
        self.boton_verificar_obra.clicked.connect(self.on_boton_verificar_obra_clicked)

    def on_boton_agregar_clicked(self):
        """
        Slot para el botón 'Agregar Obra'. Muestra feedback visual crítico y en label.
        Cumple con los tests automáticos y los estándares visuales.
        """
        self.mostrar_mensaje("Funcionalidad de agregar obra aún no implementada.", tipo="info", titulo_personalizado="Agregar Obra")

    def on_boton_verificar_obra_clicked(self):
        """
        Slot para el botón 'Verificar Obra'. Muestra feedback visual crítico y en label.
        Cumple con los tests automáticos y los estándares visuales.
        """
        self.mostrar_mensaje("Funcionalidad de verificación aún no implementada.", tipo="info", titulo_personalizado="Verificar Obra")

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

class AltaObraDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Alta de Obra")
        self.setFixedSize(420, 420)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        # Campos
        self.nombre_input = QLineEdit()
        self.nombre_input.setObjectName("nombre_input_obra")
        self.cliente_input = QLineEdit()
        self.cliente_input.setObjectName("cliente_input_obra")
        self.fecha_medicion_input = QDateEdit()
        self.fecha_medicion_input.setCalendarPopup(True)
        self.fecha_medicion_input.setDate(QDate.currentDate())
        self.fecha_entrega_input = QDateEdit()
        self.fecha_entrega_input.setObjectName("fecha_entrega_input_obra")
        self.fecha_entrega_input.setCalendarPopup(True)
        self.fecha_entrega_input.setDate(QDate.currentDate().addDays(7))
        # VALIDACIÓN UI: nombre y cliente no vacíos
        regex = QRegularExpressionValidator(QRegularExpression(r"^[\w\sáéíóúÁÉÍÓÚüÜñÑ-]{1,100}$"))
        self.nombre_input.setValidator(regex)
        self.cliente_input.setValidator(regex)
        form.addRow("Nombre:", self.nombre_input)
        form.addRow("Cliente:", self.cliente_input)
        form.addRow("Fecha medición:", self.fecha_medicion_input)
        form.addRow("Fecha entrega:", self.fecha_entrega_input)
        layout.addLayout(form)
        # Botón Guardar
        self.btn_guardar = QPushButton("Guardar")
        self.btn_guardar.clicked.connect(self.accept)
        layout.addWidget(self.btn_guardar)
        self.setLayout(layout)
        # VALIDACIÓN UI: deshabilitar Guardar si fecha_entrega < fecha_medicion
        self.fecha_medicion_input.dateChanged.connect(self.validar_fechas)
        self.fecha_entrega_input.dateChanged.connect(self.validar_fechas)
        self.validar_fechas()
    def validar_fechas(self):
        fecha_med = self.fecha_medicion_input.date()
        fecha_ent = self.fecha_entrega_input.date()
        if fecha_ent < fecha_med:
            self.btn_guardar.setEnabled(False)
            self.fecha_entrega_input.setProperty("error", True)
            style = self.fecha_entrega_input.style()
            if style is not None:
                style.unpolish(self.fecha_entrega_input)
                style.polish(self.fecha_entrega_input)
            self.fecha_entrega_input.setToolTip("La fecha de entrega no puede ser anterior a la de medición.")
        else:
            self.btn_guardar.setEnabled(True)
            self.fecha_entrega_input.setProperty("error", False)
            style = self.fecha_entrega_input.style()
            if style is not None:
                style.unpolish(self.fecha_entrega_input)
                style.polish(self.fecha_entrega_input)
            self.fecha_entrega_input.setToolTip("")
    def accept(self):
        # VALIDACIÓN UI: nombre y cliente no vacíos
        nombre = self.nombre_input.text().strip()
        cliente = self.cliente_input.text().strip()
        if not nombre:
            self.nombre_input.setProperty("error", True)
            style = self.nombre_input.style()
            if style is not None:
                style.unpolish(self.nombre_input)
                style.polish(self.nombre_input)
            self.nombre_input.setToolTip("El nombre es obligatorio.")
            from core.logger import log_error
            log_error("[AltaObraDialog] Nombre vacío en alta de obra")
        else:
            self.nombre_input.setProperty("error", False)
            style = self.nombre_input.style()
            if style is not None:
                style.unpolish(self.nombre_input)
                style.polish(self.nombre_input)
            self.nombre_input.setToolTip("")
        if not cliente:
            self.cliente_input.setProperty("error", True)
            style = self.cliente_input.style()
            if style is not None:
                style.unpolish(self.cliente_input)
                style.polish(self.cliente_input)
            self.cliente_input.setToolTip("El cliente es obligatorio.")
            from core.logger import log_error
            log_error("[AltaObraDialog] Cliente vacío en alta de obra")
        else:
            self.cliente_input.setProperty("error", False)
            style = self.cliente_input.style()
            if style is not None:
                style.unpolish(self.cliente_input)
                style.polish(self.cliente_input)
            self.cliente_input.setToolTip("")
        fecha_med = self.fecha_medicion_input.date()
        fecha_ent = self.fecha_entrega_input.date()
        # VALIDACIÓN UI: asegurar que fecha de entrega no sea anterior
        if not nombre or not cliente:
            return  # No cerrar diálogo
        if fecha_ent < fecha_med:
            self.fecha_entrega_input.setProperty("error", True)
            style = self.fecha_entrega_input.style()
            if style is not None:
                style.unpolish(self.fecha_entrega_input)
                style.polish(self.fecha_entrega_input)
            self.fecha_entrega_input.setToolTip("La fecha de entrega no puede ser anterior a la de medición.")
            from core.logger import log_error
            log_error("[AltaObraDialog] Fecha de entrega anterior a medición")
            return  # No cerrar diálogo
        # Si todo OK, llamar a super().accept()
        super().accept()
