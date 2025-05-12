from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QTableWidget, QGraphicsDropShadowEffect, QMenu, QHeaderView, QMessageBox
from PyQt6.QtGui import QIcon, QColor, QAction
from PyQt6.QtCore import QSize, Qt
import json
import os
from functools import partial

class LogisticaView(QWidget):
    def __init__(self, usuario_actual="default"):
        super().__init__()
        self.usuario_actual = usuario_actual
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)

        # Cargar el stylesheet visual moderno para Logística según el tema activo
        try:
            with open("themes/config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
            tema = config.get("tema", "claro")
            archivo_qss = f"themes/{tema}.qss"
            with open(archivo_qss, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"No se pudo cargar el archivo de estilos: {e}")

        # Botón principal de acción (Agregar)
        botones_layout = QHBoxLayout()
        self.boton_agregar = QPushButton()
        self.boton_agregar.setIcon(QIcon("img/hoja-de-ruta.svg"))  # Icono específico de logística
        self.boton_agregar.setIconSize(QSize(24, 24))
        self.boton_agregar.setToolTip("Agregar envío")
        self.boton_agregar.setText("")
        self.boton_agregar.setFixedSize(48, 48)
        self.boton_agregar.setStyleSheet("")
        sombra = QGraphicsDropShadowEffect()
        sombra.setBlurRadius(15)
        sombra.setXOffset(0)
        sombra.setYOffset(4)
        sombra.setColor(QColor(0, 0, 0, 160))
        self.boton_agregar.setGraphicsEffect(sombra)
        botones_layout.addWidget(self.boton_agregar)
        botones_layout.addStretch()
        self.layout.addLayout(botones_layout)

        # Tabla de envíos
        self.tabla_envios = QTableWidget()
        self.layout.addWidget(self.tabla_envios)

        # Configuración de columnas
        self.config_path = f"config_envios_columns_{self.usuario_actual}.json"
        self.envios_headers = ["id", "destino", "fecha_envio", "estado", "observaciones"] if self.tabla_envios.columnCount() == 5 else [f"col_{i}" for i in range(self.tabla_envios.columnCount())]
        self.columnas_visibles = self.cargar_config_columnas()
        self.aplicar_columnas_visibles()

        # Menú contextual en el header
        header = self.tabla_envios.horizontalHeader()
        header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        header.customContextMenuRequested.connect(self.mostrar_menu_columnas)
        header.sectionDoubleClicked.connect(self.auto_ajustar_columna)
        header.setSectionsMovable(True)
        header.setSectionsClickable(True)
        header.sectionClicked.connect(self.mostrar_menu_columnas_header)
        self.tabla_envios.setHorizontalHeader(header)

        self.setLayout(self.layout)

    def cargar_config_columnas(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {header: True for header in self.envios_headers}

    def guardar_config_columnas(self):
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.columnas_visibles, f, ensure_ascii=False, indent=2)
        QMessageBox.information(self, "Configuración guardada", "La configuración de columnas se ha guardado correctamente.")

    def aplicar_columnas_visibles(self):
        for idx, header in enumerate(self.envios_headers):
            visible = self.columnas_visibles.get(header, True)
            self.tabla_envios.setColumnHidden(idx, not visible)

    def mostrar_menu_columnas(self, pos):
        menu = QMenu(self)
        for idx, header in enumerate(self.envios_headers):
            accion = QAction(header, self)
            accion.setCheckable(True)
            accion.setChecked(self.columnas_visibles.get(header, True))
            accion.toggled.connect(partial(self.toggle_columna, idx, header))
            menu.addAction(accion)
        menu.exec(self.tabla_envios.horizontalHeader().mapToGlobal(pos))

    def mostrar_menu_columnas_header(self, idx):
        pos = self.tabla_envios.horizontalHeader().sectionPosition(idx)
        header = self.tabla_envios.horizontalHeader()
        global_pos = header.mapToGlobal(header.sectionViewportPosition(idx), 0)
        self.mostrar_menu_columnas(global_pos)

    def toggle_columna(self, idx, header, checked):
        self.columnas_visibles[header] = checked
        self.tabla_envios.setColumnHidden(idx, not checked)
        self.guardar_config_columnas()

    def auto_ajustar_columna(self, idx):
        self.tabla_envios.resizeColumnToContents(idx)

    @property
    def label(self):
        if not hasattr(self, '_label_estado'):
            self._label_estado = QLabel()
        return self._label_estado

    @property
    def buscar_input(self):
        if not hasattr(self, '_buscar_input'):
            self._buscar_input = QLineEdit()
        return self._buscar_input

    @property
    def id_item_input(self):
        if not hasattr(self, '_id_item_input'):
            self._id_item_input = QLineEdit()
        return self._id_item_input
