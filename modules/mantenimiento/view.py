from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTabWidget, QHBoxLayout, QPushButton, QGraphicsDropShadowEffect, QTableWidget, QMenu, QFileDialog, QDialog, QMessageBox
from PyQt6.QtGui import QIcon, QColor, QPixmap, QPainter, QAction
from PyQt6.QtCore import QSize, Qt, QPoint
from PyQt6.QtPrintSupport import QPrinter
import json
import os
import tempfile
import qrcode
from functools import partial
from core.table_responsive_mixin import TableResponsiveMixin
from core.ui_components import estilizar_boton_icono, aplicar_qss_global_y_tema
from core.logger import log_error

class MantenimientoView(QWidget, TableResponsiveMixin):
    def __init__(self):
        super().__init__()
        aplicar_qss_global_y_tema(self, qss_global_path="style_moderno.qss", qss_tema_path="themes/light.qss")
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)
        self.label_feedback = QLabel()
        self.main_layout.addWidget(self.label_feedback)

        # Botón principal de acción (Agregar)
        botones_layout = QHBoxLayout()
        self.boton_agregar = QPushButton()
        self.boton_agregar.setIcon(QIcon("img/ajustar-stock.svg"))
        self.boton_agregar.setIconSize(QSize(24, 24))
        self.boton_agregar.setToolTip("Agregar tarea de mantenimiento")
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

        # Tabla de tareas
        self.tabla_tareas = QTableWidget()
        self.make_table_responsive(self.tabla_tareas)
        self.main_layout.addWidget(self.tabla_tareas)

        # Obtener headers de la tabla de forma segura
        self.tareas_headers = []
        if self.tabla_tareas.columnCount() > 0:
            for i in range(self.tabla_tareas.columnCount()):
                item = self.tabla_tareas.horizontalHeaderItem(i)
                self.tareas_headers.append(item.text() if item is not None else f"Columna {i+1}")
        if not self.tareas_headers:
            self.tareas_headers = ["id", "tarea", "responsable", "fecha", "estado"]
            self.tabla_tareas.setColumnCount(len(self.tareas_headers))
            self.tabla_tareas.setHorizontalHeaderLabels(self.tareas_headers)
        self.config_path_tareas = f"config_mantenimiento_tareas_columns.json"
        self.columnas_visibles_tareas = self.cargar_config_columnas(self.config_path_tareas, self.tareas_headers)
        self.aplicar_columnas_visibles(self.tabla_tareas, self.tareas_headers, self.columnas_visibles_tareas)
        header_tareas = self.tabla_tareas.horizontalHeader()
        if header_tareas is not None:
            header_tareas.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            header_tareas.customContextMenuRequested.connect(partial(self.mostrar_menu_columnas, self.tabla_tareas, self.tareas_headers, self.columnas_visibles_tareas, self.config_path_tareas))
            header_tareas.sectionDoubleClicked.connect(partial(self.auto_ajustar_columna, self.tabla_tareas))
            header_tareas.setSectionsMovable(True)
            header_tareas.setSectionsClickable(True)
            header_tareas.sectionClicked.connect(partial(self.mostrar_menu_columnas_header, self.tabla_tareas, self.tareas_headers, self.columnas_visibles_tareas, self.config_path_tareas))
            self.tabla_tareas.setHorizontalHeader(header_tareas)
        self.tabla_tareas.itemSelectionChanged.connect(partial(self.mostrar_qr_item_seleccionado, self.tabla_tareas))

        # Refuerzo de accesibilidad en botón principal
        self.boton_agregar.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.boton_agregar.setStyleSheet(self.boton_agregar.styleSheet() + "\nQPushButton:focus { outline: 2px solid #2563eb; border: 2px solid #2563eb; }")
        font = self.boton_agregar.font()
        if font.pointSize() < 12:
            font.setPointSize(12)
        self.boton_agregar.setFont(font)
        if not self.boton_agregar.toolTip():
            self.boton_agregar.setToolTip("Agregar tarea de mantenimiento")
        # Refuerzo de accesibilidad en tabla principal
        self.tabla_tareas.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.tabla_tareas.setStyleSheet(self.tabla_tareas.styleSheet() + "\nQTableWidget:focus { outline: 2px solid #2563eb; border: 2px solid #2563eb; }\nQTableWidget { font-size: 13px; }")
        # EXCEPCIÓN: Si algún botón requiere texto visible por UX, debe estar documentado aquí y en docs/estandares_visuales.md

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

    def cargar_config_columnas(self, config_path, headers):
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                log_error(f"Error al cargar configuración de columnas: {e}")
                self.mostrar_mensaje(f"Error al cargar configuración de columnas: {e}", "error")
        return {header: True for header in headers}

    def guardar_config_columnas(self, config_path, columnas_visibles):
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(columnas_visibles, f, ensure_ascii=False, indent=2)
            self.mostrar_mensaje("Configuración de columnas guardada", "exito")
        except Exception as e:
            log_error(f"Error al guardar configuración de columnas: {e}")
            self.mostrar_mensaje(f"Error al guardar configuración de columnas: {e}", "error")

    def aplicar_columnas_visibles(self, tabla, headers, columnas_visibles):
        try:
            for idx, header in enumerate(headers):
                visible = columnas_visibles.get(header, True)
                tabla.setColumnHidden(idx, not visible)
        except Exception as e:
            log_error(f"Error al aplicar columnas visibles: {e}")
            self.mostrar_mensaje(f"Error al aplicar columnas visibles: {e}", "error")

    def mostrar_menu_columnas(self, tabla, headers, columnas_visibles, config_path, pos):
        try:
            menu = QMenu(self)
            for idx, header in enumerate(headers):
                accion = QAction(header, self)
                accion.setCheckable(True)
                accion.setChecked(columnas_visibles.get(header, True))
                accion.toggled.connect(partial(self.toggle_columna, tabla, idx, header, columnas_visibles, config_path))
                menu.addAction(accion)
            header = tabla.horizontalHeader()
            if header is not None:
                menu.exec(header.mapToGlobal(pos))
            else:
                log_error("No se puede mostrar el menú de columnas: header no disponible")
                self.mostrar_mensaje("No se puede mostrar el menú de columnas: header no disponible", "error")
        except Exception as e:
            log_error(f"Error al mostrar menú de columnas: {e}")
            self.mostrar_mensaje(f"Error al mostrar menú de columnas: {e}", "error")

    def mostrar_menu_columnas_header(self, tabla, headers, columnas_visibles, config_path, idx):
        try:
            header = tabla.horizontalHeader()
            if header is not None:
                pos = header.sectionPosition(idx)
                global_pos = header.mapToGlobal(QPoint(header.sectionViewportPosition(idx), 0))
                self.mostrar_menu_columnas(tabla, headers, columnas_visibles, config_path, global_pos)
            else:
                log_error("No se puede mostrar el menú de columnas: header no disponible")
                self.mostrar_mensaje("No se puede mostrar el menú de columnas: header no disponible", "error")
        except Exception as e:
            log_error(f"Error al mostrar menú de columnas desde header: {e}")
            self.mostrar_mensaje(f"Error al mostrar menú de columnas: {e}", "error")

    def toggle_columna(self, tabla, idx, header, columnas_visibles, config_path, checked):
        try:
            columnas_visibles[header] = checked
            tabla.setColumnHidden(idx, not checked)
            self.guardar_config_columnas(config_path, columnas_visibles)
            self.mostrar_mensaje(f"Columna '{header}' {'mostrada' if checked else 'ocultada'}", "info")
        except Exception as e:
            log_error(f"Error al alternar columna: {e}")
            self.mostrar_mensaje(f"Error al alternar columna: {e}", "error")

    def auto_ajustar_columna(self, tabla, idx):
        try:
            tabla.resizeColumnToContents(idx)
        except Exception as e:
            log_error(f"Error al autoajustar columna: {e}")
            self.mostrar_mensaje(f"Error al autoajustar columna: {e}", "error")

    def mostrar_qr_item_seleccionado(self, tabla):
        try:
            selected = tabla.selectedItems()
            if not selected:
                return
            row = selected[0].row()
            codigo = tabla.item(row, 0).text()  # Usar el primer campo como dato QR
            if not codigo:
                self.mostrar_mensaje("No se pudo obtener el código para el QR.", "error")
                return
            qr = qrcode.QRCode(version=1, box_size=6, border=2)
            qr.add_data(codigo)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                img.save(tmp)
                tmp.flush()
                tmp_path = tmp.name
                pixmap = QPixmap(tmp_path)
        except Exception as e:
            log_error(f"Error al generar QR: {e}")
            self.mostrar_mensaje(f"Error al generar QR: {e}", "error")
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
                from reportlab.pdfgen import canvas
                from reportlab.lib.pagesizes import letter
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

    def _reforzar_accesibilidad(self):
        # Refuerzo de accesibilidad en botón principal
        btn = self.boton_agregar
        btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        btn.setStyleSheet(btn.styleSheet() + "\nQPushButton:focus { outline: 2px solid #2563eb; border: 2px solid #2563eb; }")
        font = btn.font()
        if font.pointSize() < 12:
            font.setPointSize(12)
        btn.setFont(font)
        if not btn.toolTip():
            btn.setToolTip("Agregar tarea de mantenimiento")
        if not btn.accessibleName():
            btn.setAccessibleName("Botón agregar tarea de mantenimiento")
        # Refuerzo de accesibilidad en tabla principal
        tabla = self.tabla_tareas
        tabla.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        tabla.setStyleSheet(tabla.styleSheet() + "\nQTableWidget:focus { outline: 2px solid #2563eb; border: 2px solid #2563eb; }\nQTableWidget { font-size: 13px; }")
        tabla.setToolTip("Tabla de tareas de mantenimiento")
        tabla.setAccessibleName("Tabla principal de mantenimiento")
        # Refuerzo visual y robustez en header de tabla principal
        header = self.tabla_tareas.horizontalHeader() if hasattr(self.tabla_tareas, 'horizontalHeader') else None
        if header is not None:
            try:
                header.setStyleSheet("background-color: #e3f6fd; color: #2563eb; font-weight: bold; border-radius: 8px; font-size: 13px; padding: 8px 12px; border: 1px solid #e3e3e3;")
            except Exception as e:
                # EXCEPCIÓN VISUAL: Si el header no soporta setStyleSheet, documentar aquí y en docs/estandares_visuales.md
                pass
        else:
            # EXCEPCIÓN VISUAL: No se puede aplicar refuerzo visual porque el header es None
            pass
        # Refuerzo de accesibilidad en QLabel
        for widget in self.findChildren(QLabel):
            font = widget.font()
            if font.pointSize() < 12:
                font.setPointSize(12)
            widget.setFont(font)
        # Márgenes y padding en layouts según estándar
        self.main_layout.setContentsMargins(24, 20, 24, 20)
        self.main_layout.setSpacing(16)
        # Documentar excepción visual si aplica
        # EXCEPCIÓN: Este módulo no usa QLineEdit ni QComboBox en la vista principal, por lo que no aplica refuerzo en inputs ni selectores.

    def showEvent(self, event):
        super().showEvent(event)
        try:
            self._reforzar_accesibilidad()
        except AttributeError:
            pass
