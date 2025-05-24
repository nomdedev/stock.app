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
    def __init__(self):
        super().__init__()
        aplicar_qss_global_y_tema(self, qss_global_path="style_moderno.qss", qss_tema_path="themes/light.qss")
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(24, 20, 24, 20)
        self.main_layout.setSpacing(16)

        # --- HEADER VISUAL MODERNO ---
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(12)
        icono_label = QLabel()
        icono_label.setPixmap(QIcon("img/herrajes.svg").pixmap(36, 36))
        icono_label.setFixedSize(40, 40)
        icono_label.setToolTip("Icono de Herrajes")
        icono_label.setAccessibleName("Icono de Herrajes")
        titulo_label = QLabel("Herrajes")
        titulo_label.setStyleSheet("color: #2563eb; font-size: 22px; font-weight: 600; padding-left: 4px;")
        titulo_label.setAccessibleName("Título de módulo Herrajes")
        header_layout.addWidget(icono_label)
        header_layout.addWidget(titulo_label)
        header_layout.addStretch()
        self.main_layout.addLayout(header_layout)

        # Feedback visual centralizado y accesible
        self.label_feedback = QLabel()
        self.label_feedback.setStyleSheet("font-size: 13px; border-radius: 8px; padding: 8px; font-weight: 500;")
        self.label_feedback.setVisible(False)
        self.label_feedback.setAccessibleName("Feedback visual de Herrajes")
        self.main_layout.addWidget(self.label_feedback)

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

        # Configuración de columnas y persistencia
        self.config_path = "config_herrajes_columns.json"
        self.columnas_visibles = self.cargar_config_columnas()
        self.aplicar_columnas_visibles()

        # Menú contextual en el header y autoajuste de columna
        header = self.tabla_herrajes.horizontalHeader()
        if header is not None:
            header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            header.customContextMenuRequested.connect(self.mostrar_menu_columnas)
            header.sectionDoubleClicked.connect(self.autoajustar_columna)

        # Refuerzo visual y robustez en header de tabla principal
        header = self.tabla_herrajes.horizontalHeader() if hasattr(self.tabla_herrajes, 'horizontalHeader') else None
        if header is not None:
            try:
                header.setStyleSheet("background-color: #e3f6fd; color: #2563eb; font-weight: bold; border-radius: 8px; font-size: 13px; padding: 8px 12px; border: 1px solid #e3e3e3;")
            except Exception as e:
                # EXCEPCIÓN VISUAL: Si el header no soporta setStyleSheet, documentar aquí y en docs/estandares_visuales.md
                pass
        else:
            # EXCEPCIÓN VISUAL: No se puede aplicar refuerzo visual porque el header es None
            pass

        # Botón principal de acción (Agregar)
        botones_layout = QHBoxLayout()
        botones_layout.addStretch()
        self.boton_agregar = QPushButton()
        self.boton_agregar.setIcon(QIcon("img/add-material.svg"))
        self.boton_agregar.setIconSize(QSize(24, 24))
        self.boton_agregar.setToolTip("Agregar nuevo herraje")
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
        self.boton_agregar.setStyleSheet(self.boton_agregar.styleSheet() + "\nQPushButton:focus { outline: 2px solid #2563eb; border: 2px solid #2563eb; }")
        font = self.boton_agregar.font()
        if font.pointSize() < 12:
            font.setPointSize(12)
        self.boton_agregar.setFont(font)
        self.boton_agregar.setAccessibleName("Botón agregar herraje")
        botones_layout.addWidget(self.boton_agregar)
        self.main_layout.addLayout(botones_layout)

        # Refuerzo de accesibilidad en tabla principal
        self.tabla_herrajes.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.tabla_herrajes.setStyleSheet(self.tabla_herrajes.styleSheet() + "\nQTableWidget:focus { outline: 2px solid #2563eb; border: 2px solid #2563eb; }\nQTableWidget { font-size: 13px; }")
        # Refuerzo de accesibilidad en todos los QLineEdit de la vista principal
        for widget in self.findChildren(QLineEdit):
            widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            widget.setStyleSheet(widget.styleSheet() + "\nQLineEdit:focus { outline: 2px solid #2563eb; border: 2px solid #2563eb; }\nQLineEdit { font-size: 12px; }")
            font = widget.font()
            if font.pointSize() < 12:
                font.setPointSize(12)
            widget.setFont(font)
            if not widget.toolTip():
                widget.setToolTip("Campo de texto")
            if not widget.accessibleName():
                widget.setAccessibleName("Campo de texto de herrajes")
        # EXCEPCIÓN: Si algún botón requiere texto visible por UX, debe estar documentado aquí y en docs/estandares_visuales.md

    def mostrar_mensaje(self, mensaje, tipo="info", duracion=4000):
        colores = {
            "info": "#2563eb",
            "exito": "#22c55e",
            "advertencia": "#fbbf24",
            "error": "#ef4444"
        }
        color = colores.get(tipo, "#2563eb")
        self.label_feedback.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 13px; border-radius: 8px; padding: 8px;")
        self.label_feedback.setText(mensaje)
        self.label_feedback.setVisible(True)
        if tipo == "error":
            log_error(mensaje)
            QMessageBox.critical(self, "Error", mensaje)
        elif tipo == "advertencia":
            QMessageBox.warning(self, "Advertencia", mensaje)
        elif tipo == "exito":
            QMessageBox.information(self, "Éxito", mensaje)

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

class MaterialesView(QWidget, TableResponsiveMixin):
    def __init__(self, usuario_actual="default"):
        super().__init__()
        self.usuario_actual = usuario_actual
        self.main_layout = QVBoxLayout(self)

        # Tabla de materiales
        self.tabla_materiales = QTableWidget()
        self.make_table_responsive(self.tabla_materiales)
        self.main_layout.addWidget(self.tabla_materiales)

        # Configuración de columnas
        self.config_path = f"config_materiales_columns_{self.usuario_actual}.json"
        self.materiales_headers = ["id", "codigo", "descripcion", "cantidad", "ubicacion", "fecha_ingreso", "observaciones"]
        self.columnas_visibles = self.cargar_config_columnas()
        self.aplicar_columnas_visibles()

        # Menú contextual en el header
        header = self.tabla_materiales.horizontalHeader()
        if header is not None:
            header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            header.customContextMenuRequested.connect(self.mostrar_menu_columnas)
            header.sectionDoubleClicked.connect(self.auto_ajustar_columna)
            header.setSectionsMovable(True)
            header.setSectionsClickable(True)
            header.sectionClicked.connect(self.mostrar_menu_columnas_header)
            self.tabla_materiales.setHorizontalHeader(header)

        # Botón principal de acción (Agregar)
        botones_layout = QHBoxLayout()
        self.boton_agregar = QPushButton()
        self.boton_agregar.setIcon(QIcon("img/plus_icon.svg"))
        self.boton_agregar.setIconSize(QSize(32, 32))
        self.boton_agregar.setToolTip("Agregar nuevo material")
        self.boton_agregar.setText("")
        self.boton_agregar.setFixedSize(48, 48)
        self.boton_agregar.setStyleSheet("")
        sombra = QGraphicsDropShadowEffect()
        sombra.setBlurRadius(15)
        sombra.setXOffset(0)
        sombra.setYOffset(4)
        sombra.setColor(QColor(0, 0, 0, 50))
        self.boton_agregar.setGraphicsEffect(sombra)
        botones_layout.addWidget(self.boton_agregar)
        botones_layout.addStretch()
        self.main_layout.addLayout(botones_layout)

    def cargar_config_columnas(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {header: True for header in self.materiales_headers}

    def guardar_config_columnas(self):
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.columnas_visibles, f, ensure_ascii=False, indent=2)
        QMessageBox.information(self, "Configuración guardada", "La configuración de columnas se ha guardado correctamente.")

    def aplicar_columnas_visibles(self):
        for idx, header in enumerate(self.materiales_headers):
            visible = self.columnas_visibles.get(header, True)
            self.tabla_materiales.setColumnHidden(idx, not visible)

    def mostrar_menu_columnas(self, pos):
        menu = QMenu(self)
        for idx, header in enumerate(self.materiales_headers):
            accion = QAction(header, self)
            accion.setCheckable(True)
            accion.setChecked(self.columnas_visibles.get(header, True))
            accion.toggled.connect(partial(self.toggle_columna, idx, header))
            menu.addAction(accion)
        header = self.tabla_materiales.horizontalHeader()
        if header is not None:
            menu.exec(header.mapToGlobal(pos))
        else:
            menu.exec(pos)

    def mostrar_menu_columnas_header(self, idx):
        header = self.tabla_materiales.horizontalHeader()
        if header is not None:
            pos = header.sectionPosition(idx)
            global_pos = header.mapToGlobal(QPoint(header.sectionViewportPosition(idx), 0))
            self.mostrar_menu_columnas(global_pos)

    def toggle_columna(self, idx, header, checked):
        self.columnas_visibles[header] = checked
        self.tabla_materiales.setColumnHidden(idx, not checked)
        self.guardar_config_columnas()

    def auto_ajustar_columna(self, idx):
        self.tabla_materiales.resizeColumnToContents(idx)
