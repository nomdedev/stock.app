from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QFormLayout, QTableWidget, QTableWidgetItem, QDateEdit, QHBoxLayout, QGraphicsDropShadowEffect, QMenu, QHeaderView, QMessageBox, QDialog, QFileDialog
from PyQt6.QtGui import QIcon, QColor, QAction, QPixmap
from PyQt6.QtCore import QSize, Qt, QPoint
import json
import os
from functools import partial
import qrcode
import tempfile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from core.table_responsive_mixin import TableResponsiveMixin
from core.ui_components import estilizar_boton_icono, aplicar_qss_global_y_tema
from core.logger import log_error

class VidriosView(QWidget, TableResponsiveMixin):
    """
    Vista robusta para gestión de vidrios.
    Cumple los estándares de layout, QSS, headers, robustez y feedback definidos en el README.
    - Usa main_layout y setLayout.
    - Valida headers y celdas antes de acceder.
    - No usa box-shadow en QSS (usa QGraphicsDropShadowEffect en botones).
    - Exportación QR robusta.
    """
    def __init__(self, usuario_actual="default", headers_dinamicos=None):
        super().__init__()
        aplicar_qss_global_y_tema(self, qss_global_path="style_moderno.qss", qss_tema_path="themes/light.qss")
        self.usuario_actual = usuario_actual
        # Inicializar headers ANTES de cualquier uso
        self.vidrios_headers = headers_dinamicos if headers_dinamicos else ["tipo", "ancho", "alto", "cantidad", "proveedor", "fecha_entrega"]
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)
        self.setWindowTitle("Gestión de Vidrios")

        # Encabezado
        self.label_titulo = QLabel("Gestión de Vidrios")
        self.main_layout.addWidget(self.label_titulo)

        # Formulario de entrada
        self.form_layout = self.create_form_layout()
        self.main_layout.addLayout(self.form_layout)

        # Tabla para mostrar los vidrios
        self.tabla_vidrios = self.create_table()
        self.make_table_responsive(self.tabla_vidrios)
        self.main_layout.addWidget(self.tabla_vidrios)

        # Configuración de columnas y headers dinámicos
        self.config_path = f"config_vidrios_columns_{self.usuario_actual}.json"
        self.columnas_visibles = self.cargar_config_columnas()
        self.aplicar_columnas_visibles()

        # Menú contextual en el header (robusto)
        header = self.tabla_vidrios.horizontalHeader()
        if header is not None:
            header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            if hasattr(header, 'customContextMenuRequested'):
                header.customContextMenuRequested.connect(self.mostrar_menu_columnas)
            if hasattr(header, 'sectionDoubleClicked'):
                header.sectionDoubleClicked.connect(self.auto_ajustar_columna)
            if hasattr(header, 'setSectionsMovable'):
                header.setSectionsMovable(True)
            if hasattr(header, 'setSectionsClickable'):
                header.setSectionsClickable(True)
            if hasattr(header, 'sectionClicked'):
                header.sectionClicked.connect(self.mostrar_menu_columnas_header)

        # Botones principales como iconos (con sombra real)
        botones_layout = QHBoxLayout()
        self.boton_agregar = QPushButton()
        self.boton_agregar.setIcon(QIcon("img/add-material.svg"))
        self.boton_agregar.setIconSize(QSize(20, 20))
        self.boton_agregar.setToolTip("Agregar vidrio")
        self.boton_agregar.setText("")
        self.boton_agregar.setFixedSize(48, 48)
        sombra = QGraphicsDropShadowEffect()
        sombra.setBlurRadius(12)
        sombra.setColor(QColor(37,99,235,40))
        sombra.setOffset(0, 2)
        self.boton_agregar.setGraphicsEffect(sombra)
        self.boton_buscar = QPushButton()
        self.boton_buscar.setIcon(QIcon("img/search_icon.svg"))
        self.boton_buscar.setIconSize(QSize(20, 20))
        self.boton_buscar.setToolTip("Buscar vidrio")
        self.boton_buscar.setText("")
        self.boton_buscar.setFixedSize(48, 48)
        sombra2 = QGraphicsDropShadowEffect()
        sombra2.setBlurRadius(12)
        sombra2.setColor(QColor(37,99,235,40))
        sombra2.setOffset(0, 2)
        self.boton_buscar.setGraphicsEffect(sombra2)
        self.boton_exportar_excel = QPushButton()
        self.boton_exportar_excel.setIcon(QIcon("img/excel_icon.svg"))
        self.boton_exportar_excel.setIconSize(QSize(24, 24))
        self.boton_exportar_excel.setToolTip("Exportar vidrios a Excel")
        self.boton_exportar_excel.setText("")
        self.boton_exportar_excel.setFixedSize(48, 48)
        sombra3 = QGraphicsDropShadowEffect()
        sombra3.setBlurRadius(12)
        sombra3.setColor(QColor(37,99,235,40))
        sombra3.setOffset(0, 2)
        self.boton_exportar_excel.setGraphicsEffect(sombra3)
        estilizar_boton_icono(self.boton_agregar)
        estilizar_boton_icono(self.boton_buscar)
        estilizar_boton_icono(self.boton_exportar_excel)
        botones_layout.addWidget(self.boton_agregar)
        botones_layout.addWidget(self.boton_buscar)
        botones_layout.addWidget(self.boton_exportar_excel)
        botones_layout.addStretch()
        self.main_layout.addLayout(botones_layout)

        # Feedback visual
        self.label_feedback = QLabel()
        self.main_layout.addWidget(self.label_feedback)

        self.tabla_vidrios.itemSelectionChanged.connect(self.mostrar_qr_item_seleccionado)

        self.setLayout(self.main_layout)

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
            log_error(mensaje)
            QMessageBox.critical(self, "Error", mensaje)
        elif tipo == "advertencia":
            QMessageBox.warning(self, "Advertencia", mensaje)
        elif tipo == "exito":
            QMessageBox.information(self, "Éxito", mensaje)

    def create_form_layout(self):
        form_layout = QFormLayout()
        self.tipo_input = QLineEdit()
        self.ancho_input = QLineEdit()
        self.alto_input = QLineEdit()
        self.cantidad_input = QLineEdit()
        self.proveedor_input = QLineEdit()
        self.fecha_entrega_input = QDateEdit()
        self.fecha_entrega_input.setCalendarPopup(True)
        form_layout.addRow("Tipo:", self.tipo_input)
        form_layout.addRow("Ancho:", self.ancho_input)
        form_layout.addRow("Alto:", self.alto_input)
        form_layout.addRow("Cantidad:", self.cantidad_input)
        form_layout.addRow("Proveedor:", self.proveedor_input)
        form_layout.addRow("Fecha de Entrega:", self.fecha_entrega_input)
        return form_layout

    def create_table(self):
        table = QTableWidget()
        table.setColumnCount(len(self.vidrios_headers))
        table.setHorizontalHeaderLabels(self.vidrios_headers)
        return table

    def cargar_config_columnas(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                log_error(f"Error al cargar configuración de columnas: {e}")
                self.mostrar_mensaje(f"Error al cargar configuración de columnas: {e}", "error")
        return {header: True for header in self.vidrios_headers}

    def guardar_config_columnas(self):
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.columnas_visibles, f, ensure_ascii=False, indent=2)
            self.mostrar_mensaje("Configuración de columnas guardada", "exito")
        except Exception as e:
            log_error(f"Error al guardar configuración de columnas: {e}")
            self.mostrar_mensaje(f"Error al guardar configuración de columnas: {e}", "error")

    def aplicar_columnas_visibles(self):
        try:
            for idx, header in enumerate(self.vidrios_headers):
                visible = self.columnas_visibles.get(header, True)
                self.tabla_vidrios.setColumnHidden(idx, not visible)
        except Exception as e:
            log_error(f"Error al aplicar columnas visibles: {e}")
            self.mostrar_mensaje(f"Error al aplicar columnas visibles: {e}", "error")

    def mostrar_menu_columnas(self, pos):
        try:
            menu = QMenu(self)
            for idx, header in enumerate(self.vidrios_headers):
                accion = QAction(header, self)
                accion.setCheckable(True)
                accion.setChecked(self.columnas_visibles.get(header, True))
                accion.toggled.connect(partial(self.toggle_columna, idx, header))
                menu.addAction(accion)
            header = self.tabla_vidrios.horizontalHeader()
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
            header = self.tabla_vidrios.horizontalHeader()
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
            self.tabla_vidrios.setColumnHidden(idx, not checked)
            self.guardar_config_columnas()
            self.mostrar_mensaje(f"Columna '{header}' {'mostrada' if checked else 'ocultada'}", "info")
        except Exception as e:
            log_error(f"Error al alternar columna: {e}")
            self.mostrar_mensaje(f"Error al alternar columna: {e}", "error")

    def auto_ajustar_columna(self, idx):
        try:
            if idx < 0 or idx >= self.tabla_vidrios.columnCount():
                self.mostrar_mensaje("Índice de columna inválido", "error")
                log_error(f"Índice de columna inválido: {idx}")
                return
            self.tabla_vidrios.resizeColumnToContents(idx)
        except Exception as e:
            log_error(f"Error al autoajustar columna: {e}")
            self.mostrar_mensaje(f"Error al autoajustar columna: {e}", "error")

    def mostrar_qr_item_seleccionado(self):
        selected = self.tabla_vidrios.selectedItems()
        if not selected:
            return
        row = selected[0].row()
        item_codigo = self.tabla_vidrios.item(row, 0)
        if item_codigo is None:
            self.mostrar_mensaje("No se pudo obtener el código para el QR.", "error")
            return
        codigo = item_codigo.text()
        if not codigo:
            self.mostrar_mensaje("El campo de código está vacío.", "error")
            return
        try:
            qr = qrcode.QRCode(version=1, box_size=6, border=2)
            qr.add_data(codigo)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            if not hasattr(img, 'save'):
                from PIL import Image
                img = img.get_image()
        except Exception as e:
            log_error(f"Error al generar QR: {e}")
            self.mostrar_mensaje(f"Error al generar QR: {e}", "error")
            return
        try:
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                img.save(tmp)
                tmp.flush()
                tmp_path = tmp.name
                pixmap = QPixmap(tmp_path)
        except Exception as e:
            log_error(f"Error al crear imagen temporal: {e}")
            self.mostrar_mensaje(f"Error al crear imagen temporal: {e}", "error")
            return
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
            try:
                file_path, _ = QFileDialog.getSaveFileName(dialog, "Guardar QR", f"qr_{codigo}.png", "Imagen PNG (*.png)")
                if file_path:
                    with open(tmp_path, "rb") as src, open(file_path, "wb") as dst:
                        dst.write(src.read())
            except Exception as e:
                log_error(f"Error al guardar imagen QR: {e}")
                self.mostrar_mensaje(f"Error al guardar imagen QR: {e}", "error")
        def exportar_pdf():
            try:
                file_path, _ = QFileDialog.getSaveFileName(dialog, "Exportar QR a PDF", f"qr_{codigo}.pdf", "Archivo PDF (*.pdf)")
                if file_path:
                    c = canvas.Canvas(file_path, pagesize=letter)
                    c.drawInlineImage(tmp_path, 100, 500, 200, 200)
                    c.save()
            except Exception as e:
                log_error(f"Error al exportar QR a PDF: {e}")
                self.mostrar_mensaje(f"Error al exportar QR a PDF: {e}", "error")
        btn_guardar.clicked.connect(guardar)
        btn_pdf.clicked.connect(exportar_pdf)
        dialog.exec()
