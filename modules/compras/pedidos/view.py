from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QFormLayout, QScrollArea, QFrame, QTableWidget, QTableWidgetItem, QPushButton, QSizePolicy, QHBoxLayout, QMenu, QFileDialog, QDialog
from PyQt6.QtCore import Qt, QSize, QPoint
from PyQt6 import QtGui, QtCore
from PyQt6.QtGui import QPixmap, QAction, QIcon
from PyQt6.QtPrintSupport import QPrinter
from PyQt6.QtGui import QPainter
from core.ui_components import CustomButton, estilizar_boton_icono
from core.table_responsive_mixin import TableResponsiveMixin
import json
import os
import tempfile
import qrcode
from functools import partial

class Pedidos(QWidget):
    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout()
        self.label_titulo = QLabel("Vista de Pedidos")
        main_layout.addWidget(self.label_titulo)
        self.setLayout(main_layout)

class PedidosView(QWidget, TableResponsiveMixin):
    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Cargar el stylesheet visual moderno para Pedidos según el tema activo
        try:
            with open("themes/config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
            tema = config.get("theme", "theme_light")
            archivo_qss = f"resources/qss/{tema}.qss"
            with open(archivo_qss, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"No se pudo cargar el archivo de estilos de Pedidos según el tema: {e}")

        # HEADER VISUAL MODERNO: título y botones alineados
        header_layout = QHBoxLayout()
        self.label_titulo = QLabel("Pedidos de Compras")
        self.label_titulo.setObjectName("label_titulo_pedidos")  # Para QSS global
        # self.label_titulo.setStyleSheet("color: #2563eb; font-size: 18px; font-weight: bold; padding: 0 0 0 0;")  # Migrado a QSS global
        header_layout.addWidget(self.label_titulo, alignment=Qt.AlignmentFlag.AlignVCenter)
        header_layout.addStretch()
        # Crear botones principales como atributos de la clase
        self.boton_crear = QPushButton()
        self.boton_ver_detalles = QPushButton()
        self.boton_cargar_presupuesto = QPushButton()
        botones = [
            (self.boton_crear, "add-entrega.svg", "Crear nuevo pedido"),
            (self.boton_ver_detalles, "search_icon.svg", "Ver detalles del pedido"),
            (self.boton_cargar_presupuesto, "excel_icon.svg", "Cargar presupuesto")
        ]
        for boton, icono, tooltip in botones:
            boton.setObjectName(f"boton_{icono.split('.')[0]}")  # Para QSS global
            # boton.setStyleSheet("border-radius: 12px; background: #f1f5f9; color: #2563eb; min-width: 48px; min-height: 48px; margin-left: 16px;")  # Migrado a QSS global
            estilizar_boton_icono(boton)
            header_layout.addWidget(boton, alignment=Qt.AlignmentFlag.AlignVCenter)
        main_layout.insertLayout(0, header_layout)

        # Tabla principal de pedidos (si existe)
        self.tabla_pedidos = QTableWidget()
        self.tabla_pedidos.setObjectName("tabla_pedidos")  # Para QSS global
        self.make_table_responsive(self.tabla_pedidos)
        main_layout.addWidget(self.tabla_pedidos)

        # Si tienes una tabla principal, aplica el patrón universal
        if hasattr(self, 'tabla_pedidos'):
            self.make_table_responsive(self.tabla_pedidos)
            col_count = self.tabla_pedidos.columnCount()
            self.pedidos_headers = []
            for i in range(col_count):
                header_item = self.tabla_pedidos.horizontalHeaderItem(i)
                if header_item is not None and hasattr(header_item, 'text'):
                    self.pedidos_headers.append(header_item.text())
                else:
                    self.pedidos_headers.append(f"Columna {i+1}")
            if not self.pedidos_headers or any(h is None for h in self.pedidos_headers):
                self.pedidos_headers = ["id", "proveedor", "fecha", "estado", "total"]
                self.tabla_pedidos.setColumnCount(len(self.pedidos_headers))
                self.tabla_pedidos.setHorizontalHeaderLabels(self.pedidos_headers)
            self.config_path_pedidos = f"config_compras_pedidos_columns.json"
            self.columnas_visibles_pedidos = self.cargar_config_columnas(self.config_path_pedidos, self.pedidos_headers)
            self.aplicar_columnas_visibles(self.tabla_pedidos, self.pedidos_headers, self.columnas_visibles_pedidos)
            header_pedidos = self.tabla_pedidos.horizontalHeader() if hasattr(self.tabla_pedidos, 'horizontalHeader') else None
            if header_pedidos is not None:
                try:
                    header_pedidos.setObjectName("header_pedidos")  # Para QSS global
                    # header_pedidos.setStyleSheet("background-color: #e3f6fd; color: #2563eb; border-radius: 8px; font-size: 10px; padding: 8px 12px; border: 1px solid #e3e3e3;")  # Migrado a QSS global
                except Exception:
                    pass
                header_pedidos.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
                header_pedidos.customContextMenuRequested.connect(partial(self.mostrar_menu_columnas, self.tabla_pedidos, self.pedidos_headers, self.columnas_visibles_pedidos, self.config_path_pedidos))
                header_pedidos.sectionDoubleClicked.connect(partial(self.auto_ajustar_columna, self.tabla_pedidos))
                header_pedidos.setSectionsMovable(True)
                header_pedidos.setSectionsClickable(True)
                header_pedidos.sectionClicked.connect(partial(self.mostrar_menu_columnas_header, self.tabla_pedidos, self.pedidos_headers, self.columnas_visibles_pedidos, self.config_path_pedidos))
                self.tabla_pedidos.setHorizontalHeader(header_pedidos)
            self.tabla_pedidos.itemSelectionChanged.connect(partial(self.mostrar_qr_item_seleccionado, self.tabla_pedidos))
        self.setLayout(main_layout)

        # Refuerzo de accesibilidad en botones principales
        for btn in [self.boton_crear, self.boton_ver_detalles, self.boton_cargar_presupuesto]:
            # btn.setStyleSheet(btn.styleSheet() + "\nQPushButton:focus { outline: 2px solid #2563eb; border: 2px solid #2563eb; }")  # Migrado a QSS global
            btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            btn.setStyleSheet(btn.styleSheet() + "\nQPushButton:focus { outline: 2px solid #2563eb; border: 2px solid #2563eb; }")
            font = btn.font()
            if font.pointSize() < 12:
                font.setPointSize(12)
            btn.setFont(font)
            if not btn.toolTip():
                btn.setToolTip("Botón de acción")
            if not btn.accessibleName():
                btn.setAccessibleName("Botón de acción de pedidos")
        # Refuerzo de accesibilidad en tabla principal
        self.tabla_pedidos.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        # self.tabla_pedidos.setStyleSheet(self.tabla_pedidos.styleSheet() + "\nQTableWidget:focus { outline: 2px solid #2563eb; border: 2px solid #2563eb; }\nQTableWidget { font-size: 13px; }")  # Migrado a QSS global
        self.tabla_pedidos.setToolTip("Tabla de pedidos")
        self.tabla_pedidos.setAccessibleName("Tabla principal de pedidos")
        h_header = self.tabla_pedidos.horizontalHeader() if hasattr(self.tabla_pedidos, 'horizontalHeader') else None
        if h_header is not None:
            # h_header.setStyleSheet("background-color: #e3f6fd; color: #2563eb; font-weight: bold; border-radius: 8px; font-size: 13px; padding: 8px 12px; border: 1px solid #e3e3e3;")  # Migrado a QSS global
            pass
        # Refuerzo de accesibilidad en QLabel
        for widget in self.findChildren(QLabel):
            font = widget.font()
            if font.pointSize() < 12:
                font.setPointSize(12)
            widget.setFont(font)
        # Márgenes y padding en layouts según estándar
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(16)
        # EXCEPCIÓN: Este módulo no usa QLineEdit ni QComboBox en la vista principal, por lo que no aplica refuerzo en inputs ni selectores.

    def resaltar_items_bajo_stock(self, items):
        for item in items:
            if item.stock is not None and item.stock < item.stock_minimo:
                item.resaltar()

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
        item = tabla.item(row, 0)
        if item is None or not hasattr(item, 'text'):
            return
        codigo = item.text()
        if not codigo:
            return
        qr = qrcode.QRCode(version=1, box_size=6, border=2)
        qr.add_data(codigo)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        # Convertir a PIL si es necesario
        try:
            pil_img = img.get_image()
        except AttributeError:
            pil_img = img  # Ya es PIL
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            with open(tmp.name, "wb") as f:
                pil_img.save(f)
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
                    pil_img.save(f)
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
# Todas las líneas setStyleSheet comentadas corresponden a estilos migrados a QSS global. Ver docs/estandares_visuales.md
