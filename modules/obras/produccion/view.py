import os
import json
import tempfile
import qrcode
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QFormLayout, QTableWidget, QScrollArea, QFrame, QHBoxLayout, QSizePolicy, QGraphicsDropShadowEffect, QMenu, QFileDialog, QDialog
from PyQt6.QtGui import QIcon, QColor, QPixmap, QPainter, QAction
from PyQt6.QtCore import Qt, QSize, QPoint
from PyQt6.QtPrintSupport import QPrinter
from functools import partial
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class ProduccionView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)

        # Cargar el stylesheet visual moderno para Producción según el tema activo
        try:
            with open("themes/config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
            tema = config.get("tema", "claro")
            archivo_qss = f"themes/{tema}.qss"
            with open(archivo_qss, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"No se pudo cargar el archivo de estilos: {e}")

        self.label_titulo = QLabel("Gestión de Producción")
        self.layout.addWidget(self.label_titulo)

        self.label = self.label_titulo  # Para compatibilidad con controladores
        self.buscar_input = None  # No hay campo de búsqueda en esta vista
        self.id_item_input = None  # No hay campo de ID explícito en esta vista

        # Formulario de entrada
        self.form_layout = QFormLayout()
        self.abertura_input = QLineEdit()
        self.etapa_input = QLineEdit()
        self.estado_input = QLineEdit()
        self.form_layout.addRow("Abertura:", self.abertura_input)
        self.form_layout.addRow("Etapa:", self.etapa_input)
        self.form_layout.addRow("Estado:", self.estado_input)
        self.layout.addLayout(self.form_layout)

        # Tabla de aberturas
        self.tabla_aberturas = QTableWidget()
        self.tabla_aberturas.setColumnCount(5)
        self.tabla_aberturas.setHorizontalHeaderLabels(["ID", "Código", "Tipo", "Estado", "Fecha Inicio"])
        self.layout.addWidget(self.tabla_aberturas)

        # Configuración de columnas y persistencia para tabla_aberturas
        self.aberturas_headers = ["ID", "Código", "Tipo", "Estado", "Fecha Inicio"]
        self.config_path_aberturas = f"config_produccion_aberturas_columns.json"
        self.columnas_visibles_aberturas = self.cargar_config_columnas(self.config_path_aberturas, self.aberturas_headers)
        self.aplicar_columnas_visibles(self.tabla_aberturas, self.aberturas_headers, self.columnas_visibles_aberturas)
        header_aberturas = self.tabla_aberturas.horizontalHeader()
        header_aberturas.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        header_aberturas.customContextMenuRequested.connect(partial(self.mostrar_menu_columnas, self.tabla_aberturas, self.aberturas_headers, self.columnas_visibles_aberturas, self.config_path_aberturas))
        header_aberturas.sectionDoubleClicked.connect(partial(self.auto_ajustar_columna, self.tabla_aberturas))
        header_aberturas.setSectionsMovable(True)
        header_aberturas.setSectionsClickable(True)
        header_aberturas.sectionClicked.connect(partial(self.mostrar_menu_columnas_header, self.tabla_aberturas, self.aberturas_headers, self.columnas_visibles_aberturas, self.config_path_aberturas))
        self.tabla_aberturas.setHorizontalHeader(header_aberturas)
        self.tabla_aberturas.itemSelectionChanged.connect(partial(self.mostrar_qr_item_seleccionado, self.tabla_aberturas))

        # Tabla de etapas de fabricación (para detalles y finalizar etapa)
        self.tabla_etapas = QTableWidget()
        self.tabla_etapas.setColumnCount(5)
        self.tabla_etapas.setHorizontalHeaderLabels(["ID", "Etapa", "Estado", "Fecha Inicio", "Fecha Fin"])
        self.layout.addWidget(self.tabla_etapas)

        # Configuración de columnas y persistencia para tabla_etapas
        self.etapas_headers = ["ID", "Etapa", "Estado", "Fecha Inicio", "Fecha Fin"]
        self.config_path_etapas = f"config_produccion_etapas_columns.json"
        self.columnas_visibles_etapas = self.cargar_config_columnas(self.config_path_etapas, self.etapas_headers)
        self.aplicar_columnas_visibles(self.tabla_etapas, self.etapas_headers, self.columnas_visibles_etapas)
        header_etapas = self.tabla_etapas.horizontalHeader()
        header_etapas.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        header_etapas.customContextMenuRequested.connect(partial(self.mostrar_menu_columnas, self.tabla_etapas, self.etapas_headers, self.columnas_visibles_etapas, self.config_path_etapas))
        header_etapas.sectionDoubleClicked.connect(partial(self.auto_ajustar_columna, self.tabla_etapas))
        header_etapas.setSectionsMovable(True)
        header_etapas.setSectionsClickable(True)
        header_etapas.sectionClicked.connect(partial(self.mostrar_menu_columnas_header, self.tabla_etapas, self.etapas_headers, self.columnas_visibles_etapas, self.config_path_etapas))
        self.tabla_etapas.setHorizontalHeader(header_etapas)
        self.tabla_etapas.itemSelectionChanged.connect(partial(self.mostrar_qr_item_seleccionado, self.tabla_etapas))

        # Botón principal de acción (Agregar)
        botones_layout = QHBoxLayout()
        self.boton_agregar = QPushButton()
        self.boton_agregar.setIcon(QIcon("img/add-etapa.svg"))
        self.boton_agregar.setIconSize(QSize(24, 24))
        self.boton_agregar.setToolTip("Agregar producción")
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

        # Botón Ver Detalles
        self.boton_ver_detalles = QPushButton()
        self.boton_ver_detalles.setIcon(QIcon("img/viewdetails.svg"))
        self.boton_ver_detalles.setIconSize(QSize(24, 24))
        self.boton_ver_detalles.setToolTip("Ver detalles de la abertura seleccionada")
        self.boton_ver_detalles.setText("")
        self.boton_ver_detalles.setFixedSize(48, 48)
        self.boton_ver_detalles.setStyleSheet("")
        sombra_detalles = QGraphicsDropShadowEffect()
        sombra_detalles.setBlurRadius(15)
        sombra_detalles.setXOffset(0)
        sombra_detalles.setYOffset(4)
        sombra_detalles.setColor(QColor(0, 0, 0, 50))
        self.boton_ver_detalles.setGraphicsEffect(sombra_detalles)
        botones_layout.addWidget(self.boton_ver_detalles)

        # Botón Finalizar Etapa
        self.boton_finalizar_etapa = QPushButton()
        self.boton_finalizar_etapa.setIcon(QIcon("img/finish-check.svg"))
        self.boton_finalizar_etapa.setIconSize(QSize(24, 24))
        self.boton_finalizar_etapa.setToolTip("Finalizar etapa seleccionada")
        self.boton_finalizar_etapa.setText("")
        self.boton_finalizar_etapa.setFixedSize(48, 48)
        self.boton_finalizar_etapa.setStyleSheet("")
        sombra_finalizar = QGraphicsDropShadowEffect()
        sombra_finalizar.setBlurRadius(15)
        sombra_finalizar.setXOffset(0)
        sombra_finalizar.setYOffset(4)
        sombra_finalizar.setColor(QColor(0, 0, 0, 50))
        self.boton_finalizar_etapa.setGraphicsEffect(sombra_finalizar)
        botones_layout.addWidget(self.boton_finalizar_etapa)

        self.boton_agregar.clicked.connect(self.accion_agregar_produccion)
        self.boton_ver_detalles.clicked.connect(self.accion_ver_detalles)
        self.boton_finalizar_etapa.clicked.connect(self.accion_finalizar_etapa)

        botones_layout.addStretch()
        self.layout.addLayout(botones_layout)

        self.setLayout(self.layout)

    def agregar_grafico(self, datos):
        figura = Figure()
        canvas = FigureCanvas(figura)
        ax = figura.add_subplot(111)
        ax.bar([d[0] for d in datos], [d[1] for d in datos])
        ax.set_title("Eficiencia por Etapa")
        self.layout.addWidget(canvas)

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
        self.layout.addWidget(self.kanban_scroll)

    def agregar_tarjeta_kanban(self, etapa, tarjeta_texto):
        if etapa in self.columnas:
            tarjeta = QLabel(tarjeta_texto)
            tarjeta.setStyleSheet("background-color: lightblue; padding: 5px; margin: 5px; border: 1px solid black;")
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

    def accion_agregar_produccion(self):
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Agregar Producción", "Acción de agregar producción ejecutada.")

    def accion_ver_detalles(self):
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Ver Detalles", "Acción de ver detalles ejecutada.")

    def accion_finalizar_etapa(self):
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Finalizar Etapa", "Acción de finalizar etapa ejecutada.")

class Produccion(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.label = QLabel("Vista de Producción")
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
