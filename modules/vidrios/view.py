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

        # Cargar y aplicar QSS global y tema visual
        qss_tema = None
        try:
            with open("themes/config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
            tema = config.get("tema", "claro")
            qss_tema = f"themes/{tema}.qss"
        except Exception:
            pass
        aplicar_qss_global_y_tema(self, qss_global_path="style_moderno.qss", qss_tema_path=qss_tema)

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

        # --- Feedback visual y accesibilidad ---
        self.label_feedback = QLabel()
        self.label_feedback.setObjectName("label_feedback")
        self.label_feedback.setStyleSheet("color: #2563eb; font-weight: bold; font-size: 13px; border-radius: 8px; padding: 8px; background: #f1f5f9;")
        self.label_feedback.setVisible(False)
        self.label_feedback.setAccessibleName("Mensaje de feedback de vidrios")
        self.label_feedback.setAccessibleDescription("Mensaje de feedback visual y accesible para el usuario")
        self.main_layout.addWidget(self.label_feedback)
        self._feedback_timer = None

        self.tabla_vidrios.itemSelectionChanged.connect(self.mostrar_qr_item_seleccionado)

        self.setLayout(self.main_layout)

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
                QMessageBox.warning(self, "Error de configuración", f"No se pudo cargar la configuración de columnas: {e}")
        return {header: True for header in self.vidrios_headers}

    def guardar_config_columnas(self):
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.columnas_visibles, f, ensure_ascii=False, indent=2)
            QMessageBox.information(self, "Configuración guardada", "La configuración de columnas se ha guardado correctamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error al guardar", f"No se pudo guardar la configuración: {e}")

    def aplicar_columnas_visibles(self):
        for idx, header in enumerate(self.vidrios_headers):
            visible = self.columnas_visibles.get(header, True)
            self.tabla_vidrios.setColumnHidden(idx, not visible)

    def mostrar_menu_columnas(self, pos):
        menu = QMenu(self)
        for idx, header in enumerate(self.vidrios_headers):
            accion = QAction(header, self)
            accion.setCheckable(True)
            accion.setChecked(self.columnas_visibles.get(header, True))
            accion.toggled.connect(partial(self.toggle_columna, idx, header))
            menu.addAction(accion)
        header = self.tabla_vidrios.horizontalHeader()
        if header is not None and hasattr(header, 'mapToGlobal'):
            menu.exec(header.mapToGlobal(pos))
        else:
            menu.exec(pos)

    def mostrar_menu_columnas_header(self, idx):
        header = self.tabla_vidrios.horizontalHeader()
        # Chequeo robusto de existencia de header y métodos
        if not header or not hasattr(header, 'sectionPosition') or not hasattr(header, 'mapToGlobal') or not hasattr(header, 'sectionViewportPosition'):
            return
        if idx < 0 or idx >= self.tabla_vidrios.columnCount():
            return
        pos = header.sectionPosition(idx)
        global_pos = header.mapToGlobal(QPoint(header.sectionViewportPosition(idx), 0))
        self.mostrar_menu_columnas(global_pos)

    def toggle_columna(self, idx, header, checked):
        self.columnas_visibles[header] = checked
        self.tabla_vidrios.setColumnHidden(idx, not checked)
        self.guardar_config_columnas()

    def auto_ajustar_columna(self, idx):
        if idx < 0 or idx >= self.tabla_vidrios.columnCount():
            return
        self.tabla_vidrios.resizeColumnToContents(idx)

    def mostrar_qr_item_seleccionado(self):
        selected = self.tabla_vidrios.selectedItems()
        if not selected:
            return
        row = selected[0].row()
        item_codigo = self.tabla_vidrios.item(row, 0)
        if item_codigo is None:
            QMessageBox.warning(self, "Error de selección", "No se pudo obtener el código para el QR.")
            return
        codigo = item_codigo.text()
        if not codigo:
            QMessageBox.warning(self, "Error de datos", "El campo de código está vacío.")
            return
        try:
            qr = qrcode.QRCode(version=1, box_size=6, border=2)
            qr.add_data(codigo)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            # Convertir a formato PIL si es necesario
            if not hasattr(img, 'save'):
                from PIL import Image
                img = img.get_image()
        except Exception as e:
            QMessageBox.critical(self, "Error al generar QR", f"No se pudo generar el código QR: {e}")
            return
        try:
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                img.save(tmp)
                tmp.flush()
                tmp_path = tmp.name
                pixmap = QPixmap(tmp_path)
        except Exception as e:
            QMessageBox.critical(self, "Error de imagen", f"No se pudo crear la imagen temporal: {e}")
            return
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Código QR para {codigo}")
        vbox = QVBoxLayout(dialog)
        qr_label = QLabel()
        qr_label.setPixmap(pixmap)
        vbox.addWidget(qr_label)
        btns = QHBoxLayout()
        btn_guardar = QPushButton("Guardar QR como imagen")
        btn_pdf = QPushButton("Exportar QR a PDF")
        estilizar_boton_icono(btn_guardar)
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
                QMessageBox.critical(dialog, "Error al guardar", f"No se pudo guardar la imagen: {e}")
        def exportar_pdf():
            try:
                file_path, _ = QFileDialog.getSaveFileName(dialog, "Exportar QR a PDF", f"qr_{codigo}.pdf", "Archivo PDF (*.pdf)")
                if file_path:
                    c = canvas.Canvas(file_path, pagesize=letter)
                    c.drawInlineImage(tmp_path, 100, 500, 200, 200)
                    c.save()
            except Exception as e:
                QMessageBox.critical(dialog, "Error al exportar PDF", f"No se pudo exportar el QR a PDF: {e}")
        btn_guardar.clicked.connect(guardar)
        btn_pdf.clicked.connect(exportar_pdf)
        dialog.exec()

    def mostrar_feedback(self, mensaje, tipo="info"):
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
        self.label_feedback.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 13px; border-radius: 8px; padding: 8px; background: #f1f5f9;")
        self.label_feedback.setText(f"{icono}{mensaje}")
        self.label_feedback.setVisible(True)
        self.label_feedback.setAccessibleDescription(f"Mensaje de feedback tipo {tipo}")
        self.label_feedback.setAccessibleName(f"Feedback {tipo}")
        # Ocultar automáticamente después de 4 segundos
        from PyQt6.QtCore import QTimer
        if hasattr(self, '_feedback_timer') and self._feedback_timer:
            self._feedback_timer.stop()
        self._feedback_timer = QTimer(self)
        self._feedback_timer.setSingleShot(True)
        self._feedback_timer.timeout.connect(self.ocultar_feedback)
        self._feedback_timer.start(4000)

    def ocultar_feedback(self):
        if hasattr(self, "label_feedback") and self.label_feedback:
            self.label_feedback.setVisible(False)
            self.label_feedback.clear()
        if hasattr(self, '_feedback_timer') and self._feedback_timer:
            self._feedback_timer.stop()

