from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout, QGraphicsDropShadowEffect, QMenu, QHeaderView, QMessageBox, QDialog, QLineEdit
from PyQt6.QtGui import QIcon, QColor, QAction
from PyQt6.QtCore import QSize, Qt, QPoint
import json
import os
from functools import partial
from core.table_responsive_mixin import TableResponsiveMixin
from core.ui_components import estilizar_boton_icono

class ObrasView(QWidget, TableResponsiveMixin):
    def __init__(self, usuario_actual="default", db_connection=None):
        super().__init__()
        self.usuario_actual = usuario_actual
        self.db_connection = db_connection
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        # Título
        self.label = QLabel("Gestión de Obras")
        self.layout.addWidget(self.label)

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
        self.layout.addLayout(botones_layout)

        # Botón para verificar obra en SQL
        self.boton_verificar_obra = QPushButton("Verificar obra en SQL")
        self.boton_verificar_obra.setIcon(QIcon("img/search_icon.svg"))
        self.boton_verificar_obra.setIconSize(QSize(20, 20))
        self.boton_verificar_obra.setToolTip("Verificar existencia de obra en la base de datos SQL")
        estilizar_boton_icono(self.boton_verificar_obra)
        self.layout.addWidget(self.boton_verificar_obra)

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
        if self.tabla_obras.verticalHeader() is not None:
            self.tabla_obras.verticalHeader().setVisible(False)
        if self.tabla_obras.horizontalHeader() is not None:
            self.tabla_obras.horizontalHeader().setHighlightSections(False)
            self.tabla_obras.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
            self.tabla_obras.horizontalHeader().sectionDoubleClicked.connect(self.autoajustar_columna)
            self.tabla_obras.horizontalHeader().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            self.tabla_obras.horizontalHeader().customContextMenuRequested.connect(self.mostrar_menu_header)
            self.tabla_obras.horizontalHeader().sectionClicked.connect(self.mostrar_menu_columnas_header)
        self.layout.addWidget(self.tabla_obras)

        # Configuración de columnas visibles por usuario
        self.config_path = f"config_obras_columns_{self.usuario_actual}.json"
        self.columnas_visibles = self.cargar_config_columnas()
        self.aplicar_columnas_visibles()

        # Menú contextual para mostrar/ocultar columnas
        self.tabla_obras.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tabla_obras.customContextMenuRequested.connect(self.mostrar_menu_columnas)

        # Feedback visual centralizado
        self.label_feedback = QLabel()
        self.layout.addWidget(self.label_feedback)

        # Cargar el stylesheet visual moderno para Obras según el tema activo
        try:
            with open("themes/config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
            tema = config.get("tema", "claro")
            archivo_qss = f"themes/{tema}.qss"
            with open(archivo_qss, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"No se pudo cargar el archivo de estilos de Obras: {e}")

    def obtener_headers_desde_db(self, tabla):
        # Intenta obtener headers dinámicamente desde la base de datos
        if self.db_connection and all(hasattr(self.db_connection, attr) for attr in ["driver", "database", "username", "password"]):
            import pyodbc
            query = f"SELECT TOP 0 * FROM {tabla}"
            connection_string = (
                f"DRIVER={{{self.db_connection.driver}}};"
                f"SERVER=localhost\\SQLEXPRESS;"
                f"DATABASE={self.db_connection.database};"
                f"UID={self.db_connection.username};"
                f"PWD={self.db_connection.password};"
                f"TrustServerCertificate=yes;"
            )
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
        menu = QMenu(self)
        for idx, header in enumerate(self.obras_headers):
            accion = QAction(header, self)
            accion.setCheckable(True)
            accion.setChecked(self.columnas_visibles.get(header, True))
            accion.toggled.connect(partial(self.toggle_columna, idx, header))
            menu.addAction(accion)
        menu.exec(self.tabla_obras.horizontalHeader().mapToGlobal(pos))

    def toggle_columna(self, idx, header, checked):
        self.columnas_visibles[header] = checked
        self.tabla_obras.setColumnHidden(idx, not checked)
        self.guardar_config_columnas()
        self.mostrar_mensaje(f"Columna '{header}' {'mostrada' if checked else 'ocultada'}", "info")

    def mostrar_menu_header(self, pos):
        menu = QMenu(self)
        accion_autoajustar = QAction("Autoajustar todas las columnas", self)
        accion_autoajustar.triggered.connect(self.autoajustar_todas_columnas)
        menu.addAction(accion_autoajustar)
        menu.exec(self.tabla_obras.horizontalHeader().mapToGlobal(pos))

    def autoajustar_columna(self, idx):
        self.tabla_obras.resizeColumnToContents(idx)

    def autoajustar_todas_columnas(self):
        for idx in range(self.tabla_obras.columnCount()):
            self.tabla_obras.resizeColumnToContents(idx)

    def mostrar_menu_columnas_header(self, idx):
        header = self.tabla_obras.horizontalHeader()
        pos = header.sectionPosition(idx)
        global_pos = header.mapToGlobal(QPoint(header.sectionViewportPosition(idx), 0))
        self.mostrar_menu_columnas(global_pos)

    def cargar_headers(self, headers):
        # Permite al controlador actualizar los headers dinámicamente
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
