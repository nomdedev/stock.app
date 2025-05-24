from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QHBoxLayout, QGraphicsDropShadowEffect, QTabWidget, QComboBox, QMenu, QHeaderView, QMessageBox, QDialog, QFileDialog
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
from core.ui_components import estilizar_boton_icono, aplicar_qss_global_y_tema

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
        botones_layout.addWidget(self.boton_agregar)
        botones_layout.addStretch()
        tab_usuarios_layout.addLayout(botones_layout)
        # Tabla de usuarios
        self.tabla_usuarios = QTableWidget()
        self.make_table_responsive(self.tabla_usuarios)
        tab_usuarios_layout.addWidget(self.tabla_usuarios)
        # Configuración de columnas
        self.config_path = f"config_usuarios_columns_{self.usuario_actual}.json"
        self.usuarios_headers = self.obtener_headers_fallback()
        self.columnas_visibles = self.cargar_config_columnas()
        self.aplicar_columnas_visibles()
        # Menú contextual en el header
        header = self.tabla_usuarios.horizontalHeader() if hasattr(self.tabla_usuarios, 'horizontalHeader') else None
        if header is not None:
            if hasattr(header, 'setContextMenuPolicy'):
                header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            if hasattr(header, 'customContextMenuRequested'):
                header.customContextMenuRequested.connect(self.mostrar_menu_columnas)
            if hasattr(header, 'setSectionsMovable'):
                header.setSectionsMovable(True)
            if hasattr(header, 'setSectionsClickable'):
                header.setSectionsClickable(True)
            if hasattr(header, 'sectionClicked'):
                header.sectionClicked.connect(self.mostrar_menu_columnas_header)
        else:
            # EXCEPCIÓN VISUAL: Si el header es None, no se puede aplicar menú contextual ni acciones de header.
            # Documentar en docs/estandares_visuales.md si ocurre en producción.
            pass
        # Señal para mostrar QR al seleccionar un ítem
        if hasattr(self.tabla_usuarios, 'itemSelectionChanged'):
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
        self.boton_guardar_permisos = QPushButton()
        self.boton_guardar_permisos.setIcon(QIcon("img/guardar-permisos.svg"))
        self.boton_guardar_permisos.setToolTip("Guardar permisos")
        estilizar_boton_icono(self.boton_guardar_permisos)
        tab_permisos_layout.addWidget(self.boton_guardar_permisos)

    def mostrar_tab_permisos(self, visible):
        idx = self.tabs.indexOf(self.tab_permisos)
        if visible and idx == -1:
            self.tabs.addTab(self.tab_permisos, "Permisos de módulos")
        elif not visible and idx != -1:
            self.tabs.removeTab(idx)

    def obtener_headers_desde_db(self, tabla):
        # Obtención dinámica de headers desde la base de datos (si hay controller y método disponible)
        if self.controller and hasattr(self.controller, 'obtener_headers_desde_db'):
            try:
                headers = self.controller.obtener_headers_desde_db(tabla)
                if headers:
                    return headers
            except Exception as e:
                print(f"Error obteniendo headers desde BD: {e}")
        # Fallback seguro
        return self.obtener_headers_fallback()

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
            if hasattr(self.tabla_usuarios, 'setColumnHidden'):
                self.tabla_usuarios.setColumnHidden(idx, not visible)

    def mostrar_menu_columnas(self, pos):
        menu = QMenu(self)
        for idx, header in enumerate(self.usuarios_headers):
            accion = QAction(header, self)
            accion.setCheckable(True)
            accion.setChecked(self.columnas_visibles.get(header, True))
            accion.toggled.connect(partial(self.toggle_columna, idx, header))
            menu.addAction(accion)
        header = self.tabla_usuarios.horizontalHeader()
        if header is not None:
            menu.exec(header.mapToGlobal(pos))
        else:
            menu.exec(pos)

    def mostrar_menu_columnas_header(self, idx):
        header = self.tabla_usuarios.horizontalHeader()
        if header is not None:
            pos = header.sectionPosition(idx)
            global_pos = header.mapToGlobal(QPoint(header.sectionViewportPosition(idx), 0))
            self.mostrar_menu_columnas(global_pos)

    def toggle_columna(self, idx, header, checked):
        self.columnas_visibles[header] = checked
        if hasattr(self.tabla_usuarios, 'setColumnHidden'):
            self.tabla_usuarios.setColumnHidden(idx, not checked)
        self.guardar_config_columnas()

    def mostrar_qr_item_seleccionado(self):
        # Ejemplo de acceso seguro a item
        row = self.tabla_usuarios.currentRow() if hasattr(self.tabla_usuarios, 'currentRow') else -1
        if row != -1 and hasattr(self.tabla_usuarios, 'item'):
            item = self.tabla_usuarios.item(row, 0)
            if item is not None and hasattr(item, 'text'):
                codigo = item.text()  # Usar el primer campo como dato QR
                qr = qrcode.QRCode(version=1, box_size=6, border=2)
                qr.add_data(codigo)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                    img.save(tmp)
                    tmp_path = tmp.name
                pixmap = QPixmap(tmp_path)
                dialog = QDialog(self)
                dialog.setWindowTitle(f"Código QR para {codigo}")
                vbox = QVBoxLayout(dialog)
                qr_label = QLabel()
                qr_label.setPixmap(pixmap)
                vbox.addWidget(qr_label)
                btns = QHBoxLayout()
                btn_guardar = QPushButton()
                btn_guardar.setIcon(QIcon("img/guardar-qr.svg"))
                btn_guardar.setToolTip("Guardar QR como imagen")
                estilizar_boton_icono(btn_guardar)
                btn_pdf = QPushButton()
                btn_pdf.setIcon(QIcon("img/pdf.svg"))
                btn_pdf.setToolTip("Exportar QR a PDF")
                estilizar_boton_icono(btn_pdf)
                btns.addWidget(btn_guardar)
                btns.addWidget(btn_pdf)
                vbox.addLayout(btns)
                def guardar():
                    file_path, _ = QFileDialog.getSaveFileName(dialog, "Guardar QR", f"qr_{codigo}.png", "Imagen PNG (*.png)")
                    if file_path:
                        with open(tmp_path, "rb") as src, open(file_path, "wb") as dst:
                            dst.write(src.read())
                def exportar_pdf():
                    file_path, _ = QFileDialog.getSaveFileName(dialog, "Exportar QR a PDF", f"qr_{codigo}.pdf", "Archivo PDF (*.pdf)")
                    if file_path:
                        from reportlab.pdfgen import canvas
                        from reportlab.lib.pagesizes import letter
                        c = canvas.Canvas(file_path, pagesize=letter)
                        c.drawInlineImage(tmp_path, 100, 500, 200, 200)
                        c.save()
                btn_guardar.clicked.connect(guardar)
                btn_pdf.clicked.connect(exportar_pdf)
                dialog.exec()
        # Refuerzo de accesibilidad en botones principales
        for btn in [self.boton_agregar, self.boton_guardar_permisos]:
            btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            btn.setStyleSheet(btn.styleSheet() + "\nQPushButton:focus { outline: 2px solid #2563eb; border: 2px solid #2563eb; }")
            font = btn.font()
            if font.pointSize() < 12:
                font.setPointSize(12)
            btn.setFont(font)
            if not btn.toolTip():
                btn.setToolTip("Botón de acción")
            if not btn.accessibleName():
                btn.setAccessibleName("Botón de acción de usuarios")
        # Refuerzo de accesibilidad en tablas principales
        for tabla in [self.tabla_usuarios, self.tabla_permisos_modulos]:
            tabla.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            tabla.setStyleSheet(tabla.styleSheet() + "\nQTableWidget:focus { outline: 2px solid #2563eb; border: 2px solid #2563eb; }\nQTableWidget { font-size: 13px; }")
            tabla.setToolTip("Tabla de datos")
            tabla.setAccessibleName("Tabla principal de usuarios")
            # Refuerzo visual de headers (fondo celeste pastel, texto azul pastel, bordes redondeados)
            h_header = tabla.horizontalHeader() if hasattr(tabla, 'horizontalHeader') else None
            if h_header is not None:
                h_header.setStyleSheet("background-color: #e3f6fd; color: #2563eb; font-weight: bold; border-radius: 8px; font-size: 13px; padding: 8px 12px; border: 1px solid #e3e3e3;")
        # Refuerzo de accesibilidad en QComboBox
        for widget in self.findChildren(QComboBox):
            widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            font = widget.font()
            if font.pointSize() < 12:
                font.setPointSize(12)
            widget.setFont(font)
            if not widget.toolTip():
                widget.setToolTip("Seleccionar opción")
            if not widget.accessibleName():
                widget.setAccessibleName("Selector de usuario")
        # Refuerzo de accesibilidad en QLabel
        for widget in self.findChildren(QLabel):
            font = widget.font()
            if font.pointSize() < 12:
                font.setPointSize(12)
            widget.setFont(font)
        # Márgenes y padding en layouts según estándar
        self.main_layout.setContentsMargins(24, 20, 24, 20)
        self.main_layout.setSpacing(16)
        for tab in [self.tab_usuarios, self.tab_permisos]:
            layout = tab.layout() if hasattr(tab, 'layout') else None
            if layout is not None:
                layout.setContentsMargins(24, 20, 24, 20)
                layout.setSpacing(16)
        # Documentar excepción visual si aplica
        # EXCEPCIÓN: Este módulo no usa QLineEdit en la vista principal, por lo que no aplica refuerzo en inputs.

    def showEvent(self, event):
        super().showEvent(event)
        try:
            self._reforzar_accesibilidad()
        except AttributeError:
            pass

class Usuarios(QWidget):
    def __init__(self):
        super().__init__()
        self.main_layout = QVBoxLayout()
        self.label_titulo = QLabel("Vista de Usuarios")
        self.main_layout.addWidget(self.label_titulo)
        self.setLayout(self.main_layout)
