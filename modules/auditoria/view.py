from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QTableWidget, QSizePolicy, QHBoxLayout, QGraphicsDropShadowEffect, QMenu, QFileDialog, QDialog
from PyQt6.QtCore import Qt, QSize, QPoint
from PyQt6.QtGui import QIcon, QColor, QPixmap, QAction
from PyQt6.QtPrintSupport import QPrinter
from PyQt6.QtGui import QPainter
import json
import os
import tempfile
import qrcode
from functools import partial
from core.table_responsive_mixin import TableResponsiveMixin
from core.ui_components import estilizar_boton_icono

class AuditoriaView(QWidget, TableResponsiveMixin):
    def __init__(self):
        super().__init__()
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)

        # --- FEEDBACK VISUAL GLOBAL (accesible, visible siempre arriba de la tabla) ---
        self.label_feedback = QLabel()
        # QSS global gestiona el estilo del feedback visual, no usar setStyleSheet embebido
        self.label_feedback.setProperty("feedback", True)
        self.label_feedback.setVisible(False)
        self.label_feedback.setAccessibleName("Feedback visual de Auditoría")
        self.main_layout.addWidget(self.label_feedback)
        # --- FIN FEEDBACK VISUAL GLOBAL ---

        self._feedback_timer = None  # Temporizador para feedback visual

        # Aplicar QSS global y tema visual (solo desde resources/qss/)
        from utils.theme_manager import cargar_modo_tema
        tema = cargar_modo_tema()
        qss_tema = f"resources/qss/theme_{tema}.qss"
        from core.ui_components import aplicar_qss_global_y_tema
        aplicar_qss_global_y_tema(self, qss_global_path="resources/qss/theme_light.qss", qss_tema_path=qss_tema)

        # --- HEADER VISUAL MODERNO: título y barra de botones alineados ---
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(24)
        self.label_titulo = QLabel("Gestión de Auditoría")
        header_layout.addWidget(self.label_titulo, alignment=Qt.AlignmentFlag.AlignVCenter)
        # Botón principal (Agregar registro)
        self.boton_agregar = QPushButton()
        self.boton_agregar.setIcon(QIcon("resources/icons/add-material.svg"))
        self.boton_agregar.setIconSize(QSize(24, 24))
        self.boton_agregar.setToolTip("Agregar registro")
        header_layout.addWidget(self.boton_agregar)
        header_layout.addStretch()
        self.main_layout.addLayout(header_layout)
        # --- FIN HEADER VISUAL MODERNO ---

        # Botón principal de acción (Ver logs)
        botones_layout = QHBoxLayout()
        self.boton_ver_logs = QPushButton()
        self.boton_ver_logs.setIcon(QIcon("resources/icons/search_icon.svg"))
        self.boton_ver_logs.setIconSize(QSize(24, 24))
        self.boton_ver_logs.setToolTip("Ver logs de auditoría")
        self.boton_ver_logs.setText("")
        self.boton_ver_logs.setFixedSize(48, 48)
        # QSS global: el estilo de botones se define en themes/light.qss y dark.qss
        self.boton_ver_logs.setProperty("accion", True)
        sombra = QGraphicsDropShadowEffect()
        sombra.setBlurRadius(15)
        sombra.setXOffset(0)
        sombra.setYOffset(4)
        sombra.setColor(QColor(0, 0, 0, 160))
        self.boton_ver_logs.setGraphicsEffect(sombra)
        estilizar_boton_icono(self.boton_ver_logs)
        botones_layout.addWidget(self.boton_ver_logs)
        botones_layout.addStretch()
        self.main_layout.addLayout(botones_layout)

        # Tabla de logs (placeholder)
        self.tabla_logs = QTableWidget()
        self.make_table_responsive(self.tabla_logs)
        # QSS global: el estilo de tabla y focus se define en themes/light.qss y dark.qss
        self.tabla_logs.setProperty("tabla_auditoria", True)
        self.main_layout.addWidget(self.tabla_logs)

        # Corrección: obtener headers de forma segura
        self.logs_headers = []
        for i in range(self.tabla_logs.columnCount()):
            item = self.tabla_logs.horizontalHeaderItem(i)
            if item is not None:
                self.logs_headers.append(item.text())
            else:
                self.logs_headers.append(f"Columna {i+1}")
        if not self.logs_headers:
            self.logs_headers = ["id", "usuario", "fecha", "acción", "detalle"]
            self.tabla_logs.setColumnCount(len(self.logs_headers))
            self.tabla_logs.setHorizontalHeaderLabels(self.logs_headers)
        self.config_path_logs = f"config_auditoria_logs_columns.json"
        self.columnas_visibles_logs = self.cargar_config_columnas(self.config_path_logs, self.logs_headers)
        self.aplicar_columnas_visibles(self.tabla_logs, self.logs_headers, self.columnas_visibles_logs)
        header_logs = self.tabla_logs.horizontalHeader()
        if header_logs is not None:
            header_logs.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            header_logs.customContextMenuRequested.connect(partial(self.mostrar_menu_columnas, self.tabla_logs, self.logs_headers, self.columnas_visibles_logs, self.config_path_logs))
            header_logs.sectionDoubleClicked.connect(partial(self.auto_ajustar_columna, self.tabla_logs))
            header_logs.setSectionsMovable(True)
            header_logs.setSectionsClickable(True)
            header_logs.sectionClicked.connect(partial(self.mostrar_menu_columnas_header, self.tabla_logs, self.logs_headers, self.columnas_visibles_logs, self.config_path_logs))
            self.tabla_logs.setHorizontalHeader(header_logs)
        self.tabla_logs.itemSelectionChanged.connect(partial(self.mostrar_qr_item_seleccionado, self.tabla_logs))

        # Refuerzo de accesibilidad en botones principales
        self.boton_ver_logs.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        # QSS global: el focus de botones se define en themes/light.qss y dark.qss
        self.boton_ver_logs.setProperty("focusable", True)
        font = self.boton_ver_logs.font()
        if font.pointSize() < 12:
            font.setPointSize(12)
        self.boton_ver_logs.setFont(font)
        if not self.boton_ver_logs.toolTip():
            self.boton_ver_logs.setToolTip("Ver logs de auditoría")
        if not self.boton_ver_logs.accessibleName():
            self.boton_ver_logs.setAccessibleName("Botón ver logs de auditoría")
        # Refuerzo de accesibilidad en tabla principal
        self.tabla_logs.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.tabla_logs.setProperty("focusable", True)
        self.tabla_logs.setToolTip("Tabla de logs de auditoría")
        self.tabla_logs.setAccessibleName("Tabla principal de auditoría")
        # Refuerzo visual y robustez en header de tabla principal
        header = self.tabla_logs.horizontalHeader() if hasattr(self.tabla_logs, 'horizontalHeader') else None
        # Eliminado setStyleSheet directo en header para unificar estilo visual global y evitar doble fondo/conflictos
        # Si se requiere refuerzo visual, hacerlo solo vía QSS global (themes/*.qss)
        # if header is not None:
        #     try:
        #         header.setStyleSheet("background-color: #e3f6fd; color: #2563eb; border-radius: 8px; font-size: 10px; padding: 8px 12px; border: 1px solid #e3e3e3;")
        #     except Exception as e:
        #         # EXCEPCIÓN VISUAL: Si el header no soporta setStyleSheet, documentar aquí y en docs/estandares_visuales.md
        #         pass
        # else:
        #     # EXCEPCIÓN VISUAL: No se puede aplicar refuerzo visual porque el header es None
        #     pass
        # Refuerzo de accesibilidad en QLabel
        for widget in self.findChildren(QLabel):
            font = widget.font()
            if font.pointSize() < 12:
                font.setPointSize(12)
            widget.setFont(font)
        # Márgenes y padding en layouts según estándar
        self.main_layout.setContentsMargins(24, 20, 24, 20)
        self.main_layout.setSpacing(16)
        # EXCEPCIÓN: Este módulo no usa QLineEdit ni QComboBox en la vista principal, por lo que no aplica refuerzo en inputs ni selectores.

        self.setLayout(self.main_layout)

    def cargar_config_columnas(self, config_path, headers):
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {header: True for header in headers}

    def guardar_config_columnas(self, config_path, columnas_visibles):
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(columnas_visibles, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def aplicar_columnas_visibles(self, tabla, headers, columnas_visibles):
        for idx, header in enumerate(headers):
            visible = columnas_visibles.get(header, True)
            tabla.setColumnHidden(idx, not visible)

    def mostrar_menu_columnas(self, tabla, headers, columnas_visibles, config_path, pos):
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
            menu.exec(pos)

    def mostrar_menu_columnas_header(self, tabla, headers, columnas_visibles, config_path, idx):
        header = tabla.horizontalHeader()
        if header is not None:
            pos = header.sectionPosition(idx)
            global_pos = header.mapToGlobal(QPoint(header.sectionViewportPosition(idx), 0))
            self.mostrar_menu_columnas(tabla, headers, columnas_visibles, config_path, global_pos)

    def toggle_columna(self, tabla, idx, header, columnas_visibles, config_path, checked):
        columnas_visibles[header] = checked
        tabla.setColumnHidden(idx, not checked)
        self.guardar_config_columnas(config_path, columnas_visibles)

    def auto_ajustar_columna(self, tabla, idx):
        tabla.resizeColumnToContents(idx)

    def mostrar_qr_item_seleccionado(self, tabla):
        selected = tabla.selectedItems()
        if not selected:
            return
        row = selected[0].row()
        codigo = tabla.item(row, 0).text()  # Usar el primer campo como dato QR
        if not codigo:
            return
        qr = qrcode.QRCode(version=1, box_size=6, border=2)
        qr.add_data(codigo)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            with open(tmp.name, "wb") as f:
                img.save(f)
            pixmap = QPixmap(tmp.name)
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Código QR para {codigo}")
        vbox = QVBoxLayout(dialog)
        qr_label = QLabel()
        qr_label.setPixmap(pixmap)
        vbox.addWidget(qr_label)
        btns = QHBoxLayout()
        btn_guardar = QPushButton()
        btn_guardar.setIcon(QIcon("resources/icons/guardar-qr.svg"))
        btn_guardar.setToolTip("Guardar QR como imagen")
        estilizar_boton_icono(btn_guardar)
        btn_pdf = QPushButton()
        btn_pdf.setIcon(QIcon("resources/icons/pdf.svg"))
        btn_pdf.setToolTip("Exportar QR a PDF")
        estilizar_boton_icono(btn_pdf)
        btns.addWidget(btn_guardar)
        btns.addWidget(btn_pdf)
        vbox.addLayout(btns)
        def guardar():
            file_path, _ = QFileDialog.getSaveFileName(dialog, "Guardar QR", f"qr_{codigo}.png", "Imagen PNG (*.png)")
            if file_path:
                with open(file_path, "wb") as f:
                    img.save(f)
        def exportar_pdf():
            file_path, _ = QFileDialog.getSaveFileName(dialog, "Exportar QR a PDF", f"qr_{codigo}.pdf", "Archivo PDF (*.pdf)")
            if file_path:
                printer = QPrinter(QPrinter.PrinterMode.HighResolution)
                printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
                printer.setOutputFileName(file_path)
                painter = QPainter(printer)
                pixmap_scaled = pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio)
                painter.drawPixmap(100, 100, pixmap_scaled)
                painter.end()
        btn_guardar.clicked.connect(guardar)
        btn_pdf.clicked.connect(exportar_pdf)
        dialog.exec()

    def mostrar_feedback(self, mensaje, tipo="info", duracion=4000):
        """
        Muestra feedback visual accesible y autolimpia tras un tiempo. Unifica con mostrar_mensaje.
        """
        # QSS global: el color y formato de feedback se define en themes/light.qss y dark.qss
        self.label_feedback.setProperty("feedback_tipo", tipo)
        iconos = {
            "info": "ℹ️ ",
            "exito": "✅ ",
            "advertencia": "⚠️ ",
            "error": "❌ "
        }
        self.label_feedback.setText(f"{iconos.get(tipo, 'ℹ️ ')}{mensaje}")
        self.label_feedback.setVisible(True)
        self.label_feedback.setAccessibleDescription(mensaje)
        if self._feedback_timer:
            self._feedback_timer.stop()
        from PyQt6.QtCore import QTimer
        self._feedback_timer = QTimer(self)
        self._feedback_timer.setSingleShot(True)
        self._feedback_timer.timeout.connect(self.ocultar_feedback)
        self._feedback_timer.start(duracion)

    def mostrar_mensaje(self, mensaje, tipo="info", duracion=4000):
        """
        Alias para mostrar_feedback, para compatibilidad con otros módulos.
        """
        self.mostrar_feedback(mensaje, tipo, duracion)

    def ocultar_feedback(self):
        self.label_feedback.clear()
        self.label_feedback.setVisible(False)
        self.label_feedback.setAccessibleDescription("")

class Auditoria(QWidget):
    def __init__(self):
        super().__init__()
        self.main_layout = QVBoxLayout()
        self.label_titulo = QLabel("Vista de Auditoría")
        self.main_layout.addWidget(self.label_titulo)
        self.setLayout(self.main_layout)
