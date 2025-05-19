from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout, QGraphicsDropShadowEffect, QMenu, QHeaderView, QMessageBox, QDialog, QLineEdit
from PyQt6.QtGui import QIcon, QColor, QAction
from PyQt6.QtCore import QSize, Qt, QPoint
import json
import os
from functools import partial
from core.table_responsive_mixin import TableResponsiveMixin
from core.ui_components import estilizar_boton_icono, aplicar_qss_global_y_tema
from core.database import get_connection_string

class ObrasView(QWidget, TableResponsiveMixin):
    def __init__(self, usuario_actual="default", db_connection=None):
        super().__init__()
        self.usuario_actual = usuario_actual
        self.db_connection = db_connection
        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)

        # Título
        self.label = QLabel("Gestión de Obras")
        self.main_layout.addWidget(self.label)

        # Botón principal de acción (Agregar obra)
        botones_layout = QHBoxLayout()
        self.boton_agregar = QPushButton()
        self.boton_agregar.setIcon(QIcon("img/add-material.svg"))
        self.boton_agregar.setIconSize(QSize(24, 24))
        self.boton_agregar.setToolTip("Agregar nueva obra")
        self.boton_agregar.setText("")
        self.boton_agregar.setFixedSize(48, 48)
        self.boton_agregar.setStyleSheet("")
        sombra = QGraphicsDropShadowEffect()
        sombra.setBlurRadius(15)
        sombra.setXOffset(0)
        sombra.setYOffset(4)
        sombra.setColor(QColor(0, 0, 0, 50))
        self.boton_agregar.setGraphicsEffect(sombra)
        estilizar_boton_icono(self.boton_agregar)
        botones_layout.addWidget(self.boton_agregar)
        botones_layout.addStretch()
        self.main_layout.addLayout(botones_layout)

        # Botón para verificar obra en SQL
        self.boton_verificar_obra = QPushButton("Verificar obra en SQL")
        self.boton_verificar_obra.setIcon(QIcon("img/search_icon.svg"))
        self.boton_verificar_obra.setIconSize(QSize(20, 20))
        self.boton_verificar_obra.setToolTip("Verificar existencia de obra en la base de datos SQL")
        estilizar_boton_icono(self.boton_verificar_obra)
        self.main_layout.addWidget(self.boton_verificar_obra)

        # Obtener headers dinámicamente (fallback si no hay conexión)
        self.obras_headers = self.obtener_headers_desde_db("obras")
        if not self.obras_headers:
            self.obras_headers = ["id", "nombre", "cliente", "estado", "fecha", "fecha_entrega"]

        # Tabla principal de obras
        self.tabla_obras = QTableWidget()
        self.tabla_obras.setColumnCount(len(self.obras_headers))
        self.tabla_obras.setHorizontalHeaderLabels(self.obras_headers)
        self.make_table_responsive(self.tabla_obras)
        self.tabla_obras.setAlternatingRowColors(True)
        self.tabla_obras.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_obras.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        # Robustecer: Chequear existencia de headers antes de operar
        vh = self.tabla_obras.verticalHeader()
        if vh is not None:
            vh.setVisible(False)
        hh = self.tabla_obras.horizontalHeader()
        if hh is not None:
            hh.setHighlightSections(False)
            hh.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
            hh.sectionDoubleClicked.connect(self.autoajustar_columna)
            hh.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            hh.customContextMenuRequested.connect(self.mostrar_menu_header)
            hh.sectionClicked.connect(self.mostrar_menu_columnas_header)
        self.main_layout.addWidget(self.tabla_obras)

        # Configuración de columnas visibles por usuario
        self.config_path = f"config_obras_columns_{self.usuario_actual}.json"
        self.columnas_visibles = self.cargar_config_columnas()
        self.aplicar_columnas_visibles()

        # Menú contextual para mostrar/ocultar columnas
        self.tabla_obras.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tabla_obras.customContextMenuRequested.connect(self.mostrar_menu_columnas)

        # Feedback visual centralizado
        self.label_feedback = QLabel()
        self.main_layout.addWidget(self.label_feedback)

        # Cargar y aplicar QSS global y tema visual (NO modificar ni sobrescribir salvo justificación)
        qss_tema = None
        try:
            import json
            with open("themes/config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
            tema = config.get("tema", "claro")
            qss_tema = f"themes/{tema}.qss"
        except Exception:
            pass
        aplicar_qss_global_y_tema(self, qss_global_path="style_moderno.qss", qss_tema_path=qss_tema)

    def obtener_headers_desde_db(self, tabla):
        # Intenta obtener headers dinámicamente desde la base de datos
        if self.db_connection and all(hasattr(self.db_connection, attr) for attr in ["driver", "database", "username", "password"]):
            import pyodbc
            connection_string = get_connection_string(self.db_connection.driver, self.db_connection.database)
            query = f"SELECT TOP 0 * FROM {tabla}"
            try:
                with pyodbc.connect(connection_string, timeout=10) as conn:
                    cursor = conn.cursor()
                    cursor.execute(query)
                    return [column[0] for column in cursor.description]
            except Exception:
                pass
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
        """Muestra el menú contextual de columnas desde el header al hacer click."""
        hh = self.tabla_obras.horizontalHeader()
        if hh is not None:
            try:
                pos = hh.sectionPosition(idx)
                global_pos = hh.mapToGlobal(QPoint(hh.sectionViewportPosition(idx), 0))
                self.mostrar_menu_columnas(global_pos)
            except Exception as e:
                self.mostrar_mensaje(f"Error al mostrar menú de columnas: {e}", "error")
        else:
            self.mostrar_mensaje("No se puede mostrar el menú de columnas: header no disponible", "error")

    def cargar_headers(self, headers):
        """Permite al controlador actualizar los headers dinámicamente."""
        self.obras_headers = headers
        self.tabla_obras.setColumnCount(len(headers))
        self.tabla_obras.setHorizontalHeaderLabels(headers)
        self.columnas_visibles = self.cargar_config_columnas()
        self.aplicar_columnas_visibles()

    def cargar_tabla_obras(self, obras):
        # obras: lista de dicts con claves = headers
        self.tabla_obras.setRowCount(len(obras))
        for fila, obra in enumerate(obras):
            for columna, header in enumerate(self.obras_headers):
                valor = obra.get(header, "")
                self.tabla_obras.setItem(fila, columna, QTableWidgetItem(str(valor)))

    def mostrar_mensaje(self, mensaje, tipo="info", duracion=4000):
        """Muestra feedback visual y errores críticos con QMessageBox y color adecuado."""
        colores = {
            "info": "#2563eb",
            "exito": "#22c55e",
            "advertencia": "#fbbf24",
            "error": "#ef4444"
        }
        color = colores.get(tipo, "#2563eb")
        self.label_feedback.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 13px;")
        self.label_feedback.setText(mensaje)
        if tipo == "error":
            QMessageBox.critical(self, "Error", mensaje)
        elif tipo == "advertencia":
            QMessageBox.warning(self, "Advertencia", mensaje)
        elif tipo == "exito":
            QMessageBox.information(self, "Éxito", mensaje)
