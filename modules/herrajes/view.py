from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QFormLayout, QTableWidget, QTableWidgetItem, QHBoxLayout, QGraphicsDropShadowEffect, QMenu, QHeaderView, QMessageBox
from PyQt6.QtGui import QIcon, QColor, QAction
from PyQt6.QtCore import QSize, Qt, QPoint
import json
import os
from functools import partial
from core.table_responsive_mixin import TableResponsiveMixin
from core.ui_components import estilizar_boton_icono

class HerrajesView(QWidget, TableResponsiveMixin):
    def __init__(self):
        super().__init__()
        self.main_layout = QVBoxLayout(self)

        self.label_titulo = QLabel("Gestión de Herrajes")
        self.main_layout.addWidget(self.label_titulo)

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
            if hasattr(header, 'setContextMenuPolicy'):
                header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            if hasattr(header, 'customContextMenuRequested'):
                header.customContextMenuRequested.connect(self.mostrar_menu_columnas)
            if hasattr(header, 'sectionDoubleClicked'):
                header.sectionDoubleClicked.connect(self.autoajustar_columna)

        # Botón principal de acción (Agregar)
        botones_layout = QHBoxLayout()
        self.boton_agregar = QPushButton()
        self.boton_agregar.setIcon(QIcon("img/add-material.svg"))
        self.boton_agregar.setIconSize(QSize(24, 24))
        self.boton_agregar.setToolTip("Agregar nuevo herraje")
        self.boton_agregar.setText("")
        self.boton_agregar.setFixedSize(48, 48)
        # No sobrescribir el QSS global
        sombra = QGraphicsDropShadowEffect()
        sombra.setBlurRadius(15)
        sombra.setXOffset(0)
        sombra.setYOffset(4)
        sombra.setColor(QColor(0, 0, 0, 50))
        self.boton_agregar.setGraphicsEffect(sombra)
        estilizar_boton_icono(self.boton_agregar)
        botones_layout.addWidget(self.boton_agregar)
        self.main_layout.addLayout(botones_layout)

    def cargar_config_columnas(self):
        import os, json
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {header: True for header in self.herrajes_headers}

    def guardar_config_columnas(self):
        import json
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.columnas_visibles, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def aplicar_columnas_visibles(self):
        for idx, header in enumerate(self.herrajes_headers):
            visible = self.columnas_visibles.get(header, True)
            self.tabla_herrajes.setColumnHidden(idx, not visible)

    def mostrar_menu_columnas(self, pos):
        menu = QMenu(self)
        for idx, header in enumerate(self.herrajes_headers):
            accion = QAction(header, self)
            accion.setCheckable(True)
            accion.setChecked(self.columnas_visibles.get(header, True))
            accion.toggled.connect(partial(self.toggle_columna, idx, header))
            menu.addAction(accion)
        header = self.tabla_herrajes.horizontalHeader()
        if header is not None and hasattr(header, 'mapToGlobal'):
            menu.exec(header.mapToGlobal(pos))
        else:
            menu.exec(pos)

    def toggle_columna(self, idx, header, checked):
        self.columnas_visibles[header] = checked
        self.tabla_herrajes.setColumnHidden(idx, not checked)
        self.guardar_config_columnas()

    def autoajustar_columna(self, idx):
        self.tabla_herrajes.resizeColumnToContents(idx)

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
        menu.exec(self.tabla_materiales.horizontalHeader().mapToGlobal(pos))

    def mostrar_menu_columnas_header(self, idx):
        pos = self.tabla_materiales.horizontalHeader().sectionPosition(idx)
        header = self.tabla_materiales.horizontalHeader()
        global_pos = header.mapToGlobal(QPoint(header.sectionViewportPosition(idx), 0))
        self.mostrar_menu_columnas(global_pos)

    def toggle_columna(self, idx, header, checked):
        self.columnas_visibles[header] = checked
        self.tabla_materiales.setColumnHidden(idx, not checked)
        self.guardar_config_columnas()

    def auto_ajustar_columna(self, idx):
        self.tabla_materiales.resizeColumnToContents(idx)
