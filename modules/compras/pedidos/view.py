from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QFormLayout, QScrollArea, QFrame, QTableWidget, QTableWidgetItem, QPushButton, QSizePolicy, QHBoxLayout, QMenu, QFileDialog, QDialog
from PyQt6.QtCore import Qt, QSize, QPoint
from PyQt6 import QtGui, QtCore
from PyQt6.QtGui import QPixmap, QAction
from PyQt6.QtPrintSupport import QPrinter
from PyQt6.QtGui import QPainter
from core.ui_components import CustomButton
from core.table_responsive_mixin import TableResponsiveMixin
import json
import os
import tempfile
import qrcode
from functools import partial

class Pedidos(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.label_titulo = QLabel("Vista de Pedidos")
        self.layout.addWidget(self.label_titulo)
        self.setLayout(self.layout)

class PedidosView(QWidget, TableResponsiveMixin):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)

        # Cargar el stylesheet visual moderno para Pedidos según el tema activo
        try:
            with open("themes/config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
            tema = config.get("tema", "claro")
            archivo_qss = f"themes/{tema}.qss"
            with open(archivo_qss, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"No se pudo cargar el archivo de estilos de Pedidos según el tema: {e}")

        # Botones principales como iconos
        botones_layout = QHBoxLayout()
        self.boton_crear = QPushButton()
        self.boton_ver_detalles = QPushButton()
        self.boton_cargar_presupuesto = QPushButton()
        botones = [
            (self.boton_crear, "add-entrega.svg", "Crear nuevo pedido"),
            (self.boton_ver_detalles, "search_icon.svg", "Ver detalles del pedido"),
            (self.boton_cargar_presupuesto, "excel_icon.svg", "Cargar presupuesto"),
        ]
        for boton, icono, tooltip in botones:
            boton.setIcon(QtGui.QIcon(f"img/{icono}"))
            boton.setIconSize(QSize(24, 24))
            boton.setToolTip(tooltip)
            boton.setText("")
            boton.setFixedSize(48, 48)
            boton.setStyleSheet("")
            botones_layout.addWidget(boton)
        self.layout.addLayout(botones_layout)

        # Tabla principal de pedidos (si existe)
        self.tabla_pedidos = QTableWidget()
        self.make_table_responsive(self.tabla_pedidos)
        self.layout.addWidget(self.tabla_pedidos)

        # Si tienes una tabla principal, aplica el patrón universal
        if hasattr(self, 'tabla_pedidos'):
            self.make_table_responsive(self.tabla_pedidos)
            self.pedidos_headers = [self.tabla_pedidos.horizontalHeaderItem(i).text() if self.tabla_pedidos.columnCount() > 0 else f"Columna {i+1}" for i in range(self.tabla_pedidos.columnCount())]
            if not self.pedidos_headers:
                self.pedidos_headers = ["id", "proveedor", "fecha", "estado", "total"]
                self.tabla_pedidos.setColumnCount(len(self.pedidos_headers))
                self.tabla_pedidos.setHorizontalHeaderLabels(self.pedidos_headers)
            self.config_path_pedidos = f"config_compras_pedidos_columns.json"
            self.columnas_visibles_pedidos = self.cargar_config_columnas(self.config_path_pedidos, self.pedidos_headers)
            self.aplicar_columnas_visibles(self.tabla_pedidos, self.pedidos_headers, self.columnas_visibles_pedidos)
            header_pedidos = self.tabla_pedidos.horizontalHeader()
            header_pedidos.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            header_pedidos.customContextMenuRequested.connect(partial(self.mostrar_menu_columnas, self.tabla_pedidos, self.pedidos_headers, self.columnas_visibles_pedidos, self.config_path_pedidos))
            header_pedidos.sectionDoubleClicked.connect(partial(self.auto_ajustar_columna, self.tabla_pedidos))
            header_pedidos.setSectionsMovable(True)
            header_pedidos.setSectionsClickable(True)
            header_pedidos.sectionClicked.connect(partial(self.mostrar_menu_columnas_header, self.tabla_pedidos, self.pedidos_headers, self.columnas_visibles_pedidos, self.config_path_pedidos))
            self.tabla_pedidos.setHorizontalHeader(header_pedidos)
            self.tabla_pedidos.itemSelectionChanged.connect(partial(self.mostrar_qr_item_seleccionado, self.tabla_pedidos))

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
