import os
import json
import tempfile
import qrcode
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QFormLayout, QTableWidget, QScrollArea, QFrame, QHBoxLayout, QSizePolicy, QGraphicsDropShadowEffect, QMenu, QFileDialog, QDialog
from PyQt6.QtGui import QIcon, QColor, QPixmap, QPainter, QAction
from PyQt6.QtCore import Qt, QSize, QPoint
from PyQt6.QtPrintSupport import QPrinter
from functools import partial
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from core.ui_components import estilizar_boton_icono, aplicar_qss_global_y_tema

class ProduccionView(QWidget):
    def __init__(self):
        super().__init__()
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)
        # Feedback visual accesible
        self.label_feedback = QLabel()
        self.label_feedback.setObjectName("label_feedback")
        self.label_feedback.setVisible(False)
        self.label_feedback.setAccessibleName("Mensaje de feedback de producción")
        self.label_feedback.setAccessibleDescription("Mensaje de feedback visual y accesible para el usuario en Producción")
        self.main_layout.addWidget(self.label_feedback)
        self._feedback_timer = None

        # Cargar y aplicar QSS global y tema visual (solo desde resources/qss/)
        from utils.theme_manager import cargar_modo_tema
        tema = cargar_modo_tema()
        qss_tema = f"resources/qss/theme_{tema}.qss"
        aplicar_qss_global_y_tema(self, qss_global_path="resources/qss/theme_light.qss", qss_tema_path=qss_tema)

        # HEADER VISUAL MODERNO: título y botones alineados
        header_layout = QHBoxLayout()
        self.label_titulo = QLabel("Gestión de Producción")
        # El color y tamaño de fuente se gestiona por QSS global
        header_layout.addWidget(self.label_titulo, alignment=Qt.AlignmentFlag.AlignVCenter)
        header_layout.addStretch()
        # Crear botones principales como atributos de la clase
        self.boton_agregar = QPushButton()
        self.boton_ver_detalles = QPushButton()
        self.boton_finalizar_etapa = QPushButton()
        botones = [
            (self.boton_agregar, "add-etapa.svg", "Agregar producción"),
            (self.boton_ver_detalles, "viewdetails.svg", "Ver detalles de la abertura seleccionada"),
            (self.boton_finalizar_etapa, "finish-check.svg", "Finalizar etapa seleccionada")
        ]
        for boton, icono, tooltip in botones:
            boton.setIcon(QIcon(f"resources/icons/{icono}"))
            boton.setIconSize(QSize(24, 24))
            boton.setToolTip(tooltip)
            boton.setAccessibleName(tooltip)
            boton.setText("")
            boton.setFixedSize(48, 48)
            estilizar_boton_icono(boton)
            header_layout.addWidget(boton, alignment=Qt.AlignmentFlag.AlignVCenter)
        # --- CONEXIÓN DE ACCIONES A BOTONES PRINCIPALES ---
        self.boton_agregar.clicked.connect(self.accion_agregar_produccion)
        self.boton_ver_detalles.clicked.connect(self.accion_ver_detalles)
        self.boton_finalizar_etapa.clicked.connect(self.accion_finalizar_etapa)
        self.main_layout.insertLayout(0, header_layout)

        self.buscar_input = None
        self.id_item_input = None

        # Formulario de entrada
        self.form_layout = QFormLayout()
        self.abertura_input = QLineEdit()
        self.etapa_input = QLineEdit()
        self.estado_input = QLineEdit()
        self.form_layout.addRow("Abertura:", self.abertura_input)
        self.form_layout.addRow("Etapa:", self.etapa_input)
        self.form_layout.addRow("Estado:", self.estado_input)
        self.main_layout.addLayout(self.form_layout)

        # Tabla de aberturas
        self.tabla_aberturas = QTableWidget()
        self.tabla_aberturas.setColumnCount(5)
        self.tabla_aberturas.setHorizontalHeaderLabels(["ID", "Código", "Tipo", "Estado", "Fecha Inicio"])
        header_aberturas = self.tabla_aberturas.horizontalHeader()
        if header_aberturas is not None:
            header_aberturas.setObjectName("header_produccion")
        self.main_layout.addWidget(self.tabla_aberturas)
        self.aberturas_headers = ["ID", "Código", "Tipo", "Estado", "Fecha Inicio"]
        self.config_path_aberturas = f"config_produccion_aberturas_columns.json"
        self.columnas_visibles_aberturas = self.cargar_config_columnas(self.config_path_aberturas, self.aberturas_headers)
        self.aplicar_columnas_visibles(self.tabla_aberturas, self.aberturas_headers, self.columnas_visibles_aberturas)
        # El estilo de header se gestiona por QSS global
        header_aberturas = self.tabla_aberturas.horizontalHeader() if hasattr(self.tabla_aberturas, 'horizontalHeader') else None
        if header_aberturas is not None:
            try:
                pass  # QSS global gestiona el estilo visual
            except Exception:
                pass
        # Tabla de etapas de fabricación
        self.tabla_etapas = QTableWidget()
        self.tabla_etapas.setColumnCount(5)
        self.tabla_etapas.setHorizontalHeaderLabels(["ID", "Etapa", "Estado", "Fecha Inicio", "Fecha Fin"])
        header_etapas = self.tabla_etapas.horizontalHeader()
        if header_etapas is not None:
            header_etapas.setObjectName("header_produccion")
        self.main_layout.addWidget(self.tabla_etapas)
        header_etapas = self.tabla_etapas.horizontalHeader() if hasattr(self.tabla_etapas, 'horizontalHeader') else None
        if header_etapas is not None:
            try:
                pass  # QSS global gestiona el estilo visual
            except Exception:
                pass
        self.tabla_aberturas.itemSelectionChanged.connect(partial(self.mostrar_qr_item_seleccionado, self.tabla_aberturas))
        self.tabla_etapas.itemSelectionChanged.connect(partial(self.mostrar_qr_item_seleccionado, self.tabla_etapas))

        # Refuerzo de accesibilidad en botones principales
        for boton in [self.boton_agregar, self.boton_ver_detalles, self.boton_finalizar_etapa]:
            boton.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            boton.setObjectName("boton_produccion")
            # [MIGRACIÓN QSS] El estilo de focus y visual de boton_produccion se gestiona solo por QSS global
            # boton.setStyleSheet(boton.styleSheet() + "\nQPushButton:focus { outline: 2px solid #2563eb; border: 2px solid #2563eb; }")
            font = boton.font()
            if font.pointSize() < 12:
                font.setPointSize(12)
            boton.setFont(font)
            if not boton.toolTip():
                boton.setToolTip("Botón de acción")
        # Refuerzo de accesibilidad en tablas
        for tabla in [self.tabla_aberturas, self.tabla_etapas]:
            tabla.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            tabla.setObjectName("tabla_produccion")
            # [MIGRACIÓN QSS] El estilo de focus y visual de tabla_produccion se gestiona solo por QSS global
            # tabla.setStyleSheet(tabla.styleSheet() + "\nQTableWidget:focus { outline: 2px solid #2563eb; border: 2px solid #2563eb; }\nQTableWidget { font-size: 13px; }")
        # EXCEPCIÓN: Si algún botón requiere texto visible por UX, debe estar documentado aquí y en docs/estandares_visuales.md

    def agregar_grafico(self, datos):
        figura = Figure()
        canvas = FigureCanvas(figura)
        ax = figura.add_subplot(111)
        ax.bar([d[0] for d in datos], [d[1] for d in datos])
        ax.set_title("Eficiencia por Etapa")
        self.main_layout.addWidget(canvas)

    def inicializar_kanban(self):
        self.kanban_scroll = QScrollArea()
        self.kanban_scroll.setWidgetResizable(True)
        self.kanban_frame = QFrame()
        self.kanban_layout = QHBoxLayout(self.kanban_frame)

        # Columnas del Kanban
        self.columnas = {}
        etapas = ["Corte", "Soldadura", "Armado", "Burletes", "Vidrio"]
        for etapa in etapas:
            columna = QVBoxLayout()
            columna_label = QLabel(etapa)
            columna_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            columna.addWidget(columna_label)
            self.columnas[etapa] = columna

            columna_widget = QWidget()
            columna_widget.setLayout(columna)
            self.kanban_layout.addWidget(columna_widget)

        self.kanban_scroll.setWidget(self.kanban_frame)
        self.main_layout.addWidget(self.kanban_scroll)

    def agregar_tarjeta_kanban(self, etapa, tarjeta_texto):
        if etapa in self.columnas:
            tarjeta = QLabel(tarjeta_texto)
            tarjeta.setObjectName("tarjeta_kanban")
            # [MIGRACIÓN QSS] El estilo visual de tarjeta_kanban se gestiona solo por QSS global
            # tarjeta.setStyleSheet("background-color: lightblue; padding: 5px; margin: 5px; border: 1px solid black;")
            self.columnas[etapa].addWidget(tarjeta)

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
        menu.exec(tabla.horizontalHeader().mapToGlobal(pos))

    def mostrar_menu_columnas_header(self, tabla, headers, columnas_visibles, config_path, idx):
        header = tabla.horizontalHeader()
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
        main_layout = QVBoxLayout()
        main_layout.addLayout(vbox)
        self.setLayout(main_layout)
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

    def mostrar_mensaje(self, mensaje, tipo="info", duracion=4000, titulo_personalizado=None):
        """
        Muestra feedback visual crítico (QMessageBox) y en label_feedback.
        Usar para errores, advertencias o confirmaciones importantes.
        Para feedback informativo/accesible, usar mostrar_feedback.
        """
        colores = {
            "info": "#2563eb",
            "exito": "#22c55e",
            "advertencia": "#fbbf24",
            "error": "#ef4444"
        }
        color = colores.get(tipo, "#2563eb")
        self.label_feedback.setText(mensaje)
        self.label_feedback.setVisible(True)
        self.label_feedback.setAccessibleDescription(mensaje)
        self.label_feedback.setAccessibleName(f"Mensaje de feedback de producción ({tipo})")
        from PyQt6.QtWidgets import QMessageBox
        if tipo == "error":
            titulo = titulo_personalizado if titulo_personalizado else "Error"
            QMessageBox.critical(self, titulo, mensaje)
        elif tipo == "advertencia":
            titulo = titulo_personalizado if titulo_personalizado else "Advertencia"
            QMessageBox.warning(self, titulo, mensaje)
        elif tipo == "exito":
            titulo = titulo_personalizado if titulo_personalizado else "Éxito"
            QMessageBox.information(self, titulo, mensaje)
        elif tipo == "info":
            titulo = titulo_personalizado if titulo_personalizado else "Información"
            QMessageBox.information(self, titulo, mensaje)
        from PyQt6.QtCore import QTimer
        if self._feedback_timer:
            self._feedback_timer.stop()
        self._feedback_timer = QTimer(self)
        self._feedback_timer.setSingleShot(True)
        self._feedback_timer.timeout.connect(lambda: self.label_feedback.setVisible(False))
        self._feedback_timer.start(duracion)

    def accion_agregar_produccion(self):
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Agregar Producción", "Acción de agregar producción ejecutada.")

    def accion_ver_detalles(self):
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Ver Detalles", "Acción de ver detalles ejecutada.")

    def accion_finalizar_etapa(self):
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Finalizar Etapa", "Acción de finalizar etapa ejecutada.")

# NOTA: Evitar credenciales o cadenas de conexión incrustadas de forma directa en este archivo.
# Si necesitas una cadena de conexión, obténla de un archivo seguro o variable de entorno, nunca hardcodeada.
# En los flujos de error, asegúrate de usar log_error y/o registrar_evento para cumplir el estándar de feedback visual y logging.

class Produccion(QWidget):
    def __init__(self):
        super().__init__()
        self.main_layout = QVBoxLayout()
        self.label = QLabel("Vista de Producción")
        self.main_layout.addWidget(self.label)
        self.setLayout(self.main_layout)
