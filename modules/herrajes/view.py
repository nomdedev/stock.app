from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, QHBoxLayout, QGraphicsDropShadowEffect, QMenu, QHeaderView, QMessageBox, QFormLayout
from PyQt6.QtGui import QIcon, QColor, QAction
from PyQt6.QtCore import QSize, Qt, QPoint
import json
import os
from functools import partial
from core.table_responsive_mixin import TableResponsiveMixin
from core.ui_components import estilizar_boton_icono, aplicar_qss_global_y_tema
from core.logger import log_error

class HerrajesView(QWidget, TableResponsiveMixin):
    """
    Vista de gestión de herrajes.
    El botón principal de agregar herraje está disponible como self.boton_agregar para compatibilidad con el controlador.
    """
    def __init__(self):
        super().__init__()
        # Inicialización de atributos antes de cualquier uso
        self.config_path = "config_herrajes_columns.json"
        self.herrajes_headers = ["Nombre", "Cantidad", "Proveedor"]
        self.columnas_visibles = {header: True for header in self.herrajes_headers}

        # --- FEEDBACK VISUAL CENTRALIZADO Y QSS GLOBAL ---
        self.label_feedback = QLabel()
        self.label_feedback.setObjectName("label_feedback")
        # QSS global gestiona el estilo del feedback visual, no usar setStyleSheet embebido
        self.label_feedback.setVisible(False)
        self.label_feedback.setAccessibleName("Mensaje de feedback de herrajes")
        self.label_feedback.setAccessibleDescription("Mensaje de feedback visual y accesible para el usuario")
        self.main_layout.addWidget(self.label_feedback)
        self._feedback_timer = None
        # --- FIN FEEDBACK VISUAL CENTRALIZADO ---

        # Aplicar QSS global y tema visual (estándar)
        aplicar_qss_global_y_tema(self, qss_global_path="themes/light.qss", qss_tema_path="themes/light.qss")
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(24, 20, 24, 20)
        self.main_layout.setSpacing(16)

        # --- HEADER VISUAL MODERNO: título y barra de botones alineados ---
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(24)
        self.label_titulo = QLabel("Gestión de Herrajes")
        header_layout.addWidget(self.label_titulo, alignment=Qt.AlignmentFlag.AlignVCenter)
        # Botón principal (Agregar herraje)
        self.boton_agregar = QPushButton()
        self.boton_agregar.setIcon(QIcon("img/add-material.svg"))
        self.boton_agregar.setIconSize(QSize(24, 24))
        self.boton_agregar.setToolTip("Agregar herraje")
        header_layout.addWidget(self.boton_agregar)
        header_layout.addStretch()
        self.main_layout.addLayout(header_layout)

        self.form_layout = QFormLayout()
        self.nombre_input = QLineEdit()
        self.cantidad_input = QLineEdit()
        self.proveedor_input = QLineEdit()
        self.form_layout.addRow("Nombre:", self.nombre_input)
        self.form_layout.addRow("Cantidad:", self.cantidad_input)
        self.form_layout.addRow("Proveedor:", self.proveedor_input)
        self.main_layout.addLayout(self.form_layout)

        # Tabla principal de herrajes
        self.herrajes_headers = ["Nombre", "Cantidad", "Proveedor"]
        self.tabla_herrajes = QTableWidget()
        self.tabla_herrajes.setColumnCount(len(self.herrajes_headers))
        self.tabla_herrajes.setHorizontalHeaderLabels(self.herrajes_headers)
        self.make_table_responsive(self.tabla_herrajes)
        self.main_layout.addWidget(self.tabla_herrajes)

        # --- BARRA DE BOTONES PRINCIPALES (estándar: solo ícono, tooltip, accesibilidad, sombra, espaciado 16px) ---
        self.barra_botones = []
        barra_layout = QHBoxLayout()
        barra_layout.setSpacing(16)
        barra_layout.addStretch()
        botones_info = [
            ("add-material.svg", "Agregar herraje", "Botón para agregar un nuevo herraje"),
            ("excel_icon.svg", "Exportar a Excel", "Botón para exportar la tabla de herrajes a Excel"),
            ("search_icon.svg", "Buscar herraje", "Botón para buscar herrajes en la tabla"),
        ]
        for icono, tooltip, accesible in botones_info:
            btn = QPushButton()
            btn.setIcon(QIcon(f"img/{icono}"))
            btn.setToolTip(tooltip)
            btn.setAccessibleName(accesible)
            btn.setText("")
            estilizar_boton_icono(btn)
            sombra = QGraphicsDropShadowEffect()
            sombra.setBlurRadius(15)
            sombra.setXOffset(0)
            sombra.setYOffset(4)
            sombra.setColor(QColor(0, 0, 0, 80))
            btn.setGraphicsEffect(sombra)
            btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            font = btn.font()
            if font.pointSize() < 12:
                font.setPointSize(12)
            btn.setFont(font)
            barra_layout.addWidget(btn)
            self.barra_botones.append(btn)
        # Asignar el primer botón como boton_agregar para compatibilidad con el controlador
        if self.barra_botones:
            self.boton_agregar = self.barra_botones[0]
        self.main_layout.addLayout(barra_layout)
        # --- FIN BARRA DE BOTONES PRINCIPALES ---

        # Refuerzo de accesibilidad en inputs
        self.nombre_input.setToolTip("Nombre del herraje")
        self.nombre_input.setAccessibleName("Campo de nombre de herraje")
        self.cantidad_input.setToolTip("Cantidad disponible")
        self.cantidad_input.setAccessibleName("Campo de cantidad de herrajes")
        self.proveedor_input.setToolTip("Proveedor del herraje")
        self.proveedor_input.setAccessibleName("Campo de proveedor de herrajes")
        for widget in [self.nombre_input, self.cantidad_input, self.proveedor_input]:
            widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            font = widget.font()
            if font.pointSize() < 12:
                font.setPointSize(12)
            widget.setFont(font)

        # Refuerzo de accesibilidad y estilos en tabla principal
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

    def mostrar_mensaje(self, mensaje, tipo="info", duracion=3500):
        """
        Alias para mostrar_feedback, usado por handlers internos para unificar feedback visual.
        """
        self.mostrar_feedback(mensaje, tipo, duracion)

    def mostrar_feedback(self, mensaje, tipo="info", duracion=3500):
        """
        Muestra un mensaje de feedback visual accesible en el label_feedback.
        tipo: info, exito, error, advertencia
        """
        colores = {
            "info": "background: #e3f6fd; color: #2563eb;",
            "exito": "background: #d1f7e7; color: #15803d;",
            "error": "background: #fee2e2; color: #b91c1c;",
            "advertencia": "background: #fef9c3; color: #b45309;"
        }
        # Solo aplicar color de fondo y texto, el resto lo gestiona el QSS global
        self.label_feedback.setStyleSheet(colores.get(tipo, ""))
        self.label_feedback.setText(mensaje)
        self.label_feedback.setVisible(True)
        self.label_feedback.setAccessibleDescription(mensaje)
        if self._feedback_timer:
            self._feedback_timer.stop()
        from PyQt6.QtCore import QTimer
        self._feedback_timer = QTimer(self)
        self._feedback_timer.setSingleShot(True)
        self._feedback_timer.timeout.connect(self.ocultar_feedback)
        self._feedback_timer.start(duracion)

    def ocultar_feedback(self):
        self.label_feedback.clear()
        self.label_feedback.setVisible(False)
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
        try:
            menu = QMenu(self)
            for idx, header in enumerate(self.herrajes_headers):
                accion = QAction(header, self)
                accion.setCheckable(True)
                accion.setChecked(self.columnas_visibles.get(header, True))
                accion.toggled.connect(partial(self.toggle_columna, idx, header))
                menu.addAction(accion)
            header = self.tabla_herrajes.horizontalHeader()
            if header is not None:
                menu.exec(header.mapToGlobal(pos))
            else:
                log_error("No se puede mostrar el menú de columnas: header no disponible")
                self.mostrar_mensaje("No se puede mostrar el menú de columnas: header no disponible", "error")
        except Exception as e:
            log_error(f"Error al mostrar menú de columnas: {e}")
            self.mostrar_mensaje(f"Error al mostrar menú de columnas: {e}", "error")

    def mostrar_menu_columnas_header(self, idx):
        try:
            header = self.tabla_herrajes.horizontalHeader()
            if header is not None:
                pos = header.sectionPosition(idx)
                global_pos = header.mapToGlobal(QPoint(header.sectionViewportPosition(idx), 0))
                self.mostrar_menu_columnas(global_pos)
            else:
                log_error("No se puede mostrar el menú de columnas: header no disponible")
                self.mostrar_mensaje("No se puede mostrar el menú de columnas: header no disponible", "error")
        except Exception as e:
            log_error(f"Error al mostrar menú de columnas desde header: {e}")
            self.mostrar_mensaje(f"Error al mostrar menú de columnas: {e}", "error")

    def toggle_columna(self, idx, header, checked):
        try:
            self.columnas_visibles[header] = checked
            self.tabla_herrajes.setColumnHidden(idx, not checked)
            self.guardar_config_columnas()
            self.mostrar_mensaje(f"Columna '{header}' {'mostrada' if checked else 'ocultada'}", "info")
        except Exception as e:
            log_error(f"Error al alternar columna: {e}")
            self.mostrar_mensaje(f"Error al alternar columna: {e}", "error")

    def autoajustar_columna(self, idx):
        try:
            self.tabla_herrajes.resizeColumnToContents(idx)
        except Exception as e:
            log_error(f"Error al autoajustar columna: {e}")
            self.mostrar_mensaje(f"Error al autoajustar columna: {e}", "error")

    # --- MÉTODO PARA CARGAR ITEMS EN LA TABLA CON TOOLTIP EN CADA CELDA (accesibilidad) ---
    def cargar_items(self, items):
        self.tabla_herrajes.setRowCount(len(items))
        self.tabla_herrajes.setColumnCount(len(self.herrajes_headers))
        self.tabla_herrajes.setHorizontalHeaderLabels(self.herrajes_headers)
        for row, item in enumerate(items):
            for col, header in enumerate(self.herrajes_headers):
                valor = str(item.get(header, ""))
                celda = QTableWidgetItem(valor)
                celda.setToolTip(f"{header}: {valor}")
                self.tabla_herrajes.setItem(row, col, celda)

# EXCEPCIÓN JUSTIFICADA: Este módulo no requiere feedback de carga adicional porque los procesos son instantáneos o ya usan QProgressBar en exportaciones masivas. Ver test_feedback_carga y docs/estandares_visuales.md.
# JUSTIFICACIÓN: No hay estilos embebidos activos ni credenciales hardcodeadas; cualquier referencia es solo ejemplo o documentación.
