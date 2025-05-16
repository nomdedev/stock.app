from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QHBoxLayout, QGraphicsDropShadowEffect, QTabWidget, QComboBox, QMenu, QHeaderView, QMessageBox, QDialog, QFileDialog)
from PyQt6.QtGui import QIcon, QColor, QAction, QPixmap
from PyQt6.QtCore import QSize, Qt, QPoint
import json
import os
from functools import partial
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import tempfile
from core.table_responsive_mixin import TableResponsiveMixin
from core.ui_components import estilizar_boton_icono

class UsuariosView(QWidget, TableResponsiveMixin):
    def __init__(self, usuario_actual="default", controller=None):
        super().__init__()
        self.usuario_actual = usuario_actual
        self.controller = controller  # Permite inyectar lógica de negocio/mock para testeo
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)

        self._cargar_stylesheet()
        self._init_tabs()
        self._init_tab_usuarios()
        self._init_tab_permisos()
        self.setLayout(self.main_layout)

    def _cargar_stylesheet(self):
        """Carga el stylesheet visual moderno para Usuarios según el tema activo."""
        try:
            with open("themes/config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
            tema = config.get("tema", "claro")
            archivo_qss = f"themes/{tema}.qss"
            with open(archivo_qss, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"No se pudo cargar el archivo de estilos: {e}")

    def _init_tabs(self):
        self.tabs = QTabWidget()
        self.tab_usuarios = QWidget()
        self.tab_permisos = QWidget()
        self.tabs.addTab(self.tab_usuarios, "Usuarios")
        self.tabs.addTab(self.tab_permisos, "Permisos de módulos")
        self.main_layout.addWidget(self.tabs)

    def _init_tab_usuarios(self):
        tab_usuarios_layout = QVBoxLayout(self.tab_usuarios)
        botones_layout = QHBoxLayout()
        self.boton_agregar = QPushButton()
        self.boton_agregar.setIcon(QIcon("img/agregar-user.svg"))
        self.boton_agregar.setIconSize(QSize(20, 20))
        self.boton_agregar.setToolTip("Agregar usuario")
        self.boton_agregar.setText("")
        estilizar_boton_icono(self.boton_agregar)
        self.boton_agregar.setFixedSize(48, 48)
        sombra = QGraphicsDropShadowEffect()
        sombra.setBlurRadius(15)
        sombra.setXOffset(0)
        sombra.setYOffset(4)
        sombra.setColor(QColor(0, 0, 0, 50))
        self.boton_agregar.setGraphicsEffect(sombra)
        botones_layout.addWidget(self.boton_agregar)
        botones_layout.addStretch()
        tab_usuarios_layout.addLayout(botones_layout)
        self.tabla_usuarios = QTableWidget()
        self.make_table_responsive(self.tabla_usuarios)
        tab_usuarios_layout.addWidget(self.tabla_usuarios)
        # Configuración de columnas
        self.config_path = f"config_usuarios_columns_{self.usuario_actual}.json"
        self.usuarios_headers = self.obtener_headers_desde_db("usuarios") or self.obtener_headers_fallback()
        self.columnas_visibles = self.cargar_config_columnas()
        self.aplicar_columnas_visibles()
        # Menú contextual en el header
        header = self.tabla_usuarios.horizontalHeader()
        header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        header.customContextMenuRequested.connect(self.mostrar_menu_columnas)
        header.sectionClicked.connect(self.mostrar_menu_columnas_header)
        self.tabla_usuarios.itemSelectionChanged.connect(self.mostrar_qr_item_seleccionado)

    def _init_tab_permisos(self):
        tab_permisos_layout = QVBoxLayout(self.tab_permisos)
        self.label_permisos = QLabel("Asignar módulos permitidos a usuarios normales:")
        tab_permisos_layout.addWidget(self.label_permisos)
        self.combo_usuario = QComboBox()
        tab_permisos_layout.addWidget(self.combo_usuario)
        self.tabla_permisos_modulos = QTableWidget()
        self.make_table_responsive(self.tabla_permisos_modulos)
        tab_permisos_layout.addWidget(self.tabla_permisos_modulos)
        self.boton_guardar_permisos = QPushButton("Guardar permisos")
        estilizar_boton_icono(self.boton_guardar_permisos)
        tab_permisos_layout.addWidget(self.boton_guardar_permisos)

    def mostrar_tab_permisos(self, visible):
        idx = self.tabs.indexOf(self.tab_permisos)
        if visible and idx == -1:
            self.tabs.addTab(self.tab_permisos, "Permisos de módulos")
        elif not visible and idx != -1:
            self.tabs.removeTab(idx)

    def obtener_headers_desde_db(self, tabla):
        # Aquí deberías implementar la obtención dinámica de headers desde la base de datos, similar a InventarioView
        # Por ahora, fallback temporal:
        return None

    def obtener_headers_fallback(self):
        return ["id", "usuario", "nombre", "rol", "email", "estado"]

    def cargar_config_columnas(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error cargando configuración de columnas: {e}")
        return {header: True for header in self.usuarios_headers}

    def guardar_config_columnas(self):
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.columnas_visibles, f, ensure_ascii=False, indent=2)
            QMessageBox.information(self, "Configuración guardada", "La configuración de columnas se ha guardado correctamente.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo guardar la configuración: {e}")

    def aplicar_columnas_visibles(self):
        for idx, header in enumerate(self.usuarios_headers):
            visible = self.columnas_visibles.get(header, True)
            self.tabla_usuarios.setColumnHidden(idx, not visible)

    def mostrar_menu_columnas(self, pos):
        menu = QMenu(self)
        for idx, header in enumerate(self.usuarios_headers):
            accion = QAction(header, self)
            accion.setCheckable(True)
            accion.setChecked(self.columnas_visibles.get(header, True))
            accion.toggled.connect(partial(self.toggle_columna, idx, header))
            menu.addAction(accion)
        menu.exec(self.tabla_usuarios.horizontalHeader().mapToGlobal(pos))

    def mostrar_menu_columnas_header(self, idx):
        pos = self.tabla_usuarios.horizontalHeader().sectionPosition(idx)
        header = self.tabla_usuarios.horizontalHeader()
        global_pos = header.mapToGlobal(QPoint(header.sectionViewportPosition(idx), 0))
        self.mostrar_menu_columnas(global_pos)

    def toggle_columna(self, idx, header, checked):
        self.columnas_visibles[header] = checked
        self.tabla_usuarios.setColumnHidden(idx, not checked)
        self.guardar_config_columnas()

    def mostrar_qr_item_seleccionado(self):
        selected = self.tabla_usuarios.selectedItems()
        if not selected:
            return
        row = selected[0].row()
        codigo = self.tabla_usuarios.item(row, 0).text()  # Usar el primer campo como dato QR
        if not codigo:
            return
        qr = qrcode.QRCode(version=1, box_size=6, border=2)
        qr.add_data(codigo)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            img.save(tmp.name)
            pixmap = QPixmap(tmp.name)
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Código QR para {codigo}")
        vbox = QVBoxLayout(dialog)
        qr_label = QLabel()
        qr_label.setPixmap(pixmap)
        vbox.addWidget(qr_label)
        btns = QHBoxLayout()
        btn_guardar = QPushButton("Guardar QR como imagen")
        btn_pdf = QPushButton("Exportar QR a PDF")
        btns.addWidget(btn_guardar)
        btns.addWidget(btn_pdf)
        vbox.addLayout(btns)
        def guardar():
            file_path, _ = QFileDialog.getSaveFileName(dialog, "Guardar QR", f"qr_{codigo}.png", "Imagen PNG (*.png)")
            if file_path:
                img.save(file_path)
        def exportar_pdf():
            file_path, _ = QFileDialog.getSaveFileName(dialog, "Exportar QR a PDF", f"qr_{codigo}.pdf", "Archivo PDF (*.pdf)")
            if file_path:
                c = canvas.Canvas(file_path, pagesize=letter)
                c.drawInlineImage(tmp.name, 100, 500, 200, 200)
                c.save()
        btn_guardar.clicked.connect(guardar)
        btn_pdf.clicked.connect(exportar_pdf)
        dialog.exec()

class Usuarios(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.label_titulo = QLabel("Vista de Usuarios")
        self.layout.addWidget(self.label_titulo)
        self.setLayout(self.layout)
