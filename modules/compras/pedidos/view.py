from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QFormLayout, QScrollArea, QFrame, QTableWidget, QTableWidgetItem, QPushButton, QSizePolicy, QHBoxLayout, QMenu, QFileDialog, QDialog, QHeaderView
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
        main_layout.setContentsMargins(32, 32, 32, 32)  # Igual que InventarioView
        main_layout.setSpacing(16)

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

        # HEADER VISUAL MODERNO: título y barra de botones alineados arriba a la derecha
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(24)
        self.label_titulo = QLabel("Pedidos de Compras")
        self.label_titulo.setObjectName("label_titulo_pedidos")
        header_layout.addWidget(self.label_titulo, alignment=Qt.AlignmentFlag.AlignVCenter)
        header_layout.addStretch()
        # --- ORDEN DE BOTONES DE ACCIÓN EN PEDIDOSVIEW ---
        # El orden y estructura de la barra de botones debe mantenerse igual a InventarioView para coherencia visual.
        # Si se modifica, actualizar también en checklist_botones_accion.txt y documentar el cambio aquí con fecha y motivo.
        # Última revisión: 08/06/2025. Orden actual:
        # 1. Crear nuevo pedido
        # 2. Ver detalles del pedido
        # 3. Cargar presupuesto
        # 4. Emitir remito
        #
        # NOTA: El orden de los botones principales está documentado aquí y en checklist_botones_accion.txt.
        # No modificar sin actualizar ambos lugares y dejar comentario de justificación y fecha.
        icon_dir = os.path.join(os.path.dirname(__file__), '../../resources/icons')
        self.boton_crear = QPushButton()
        self.boton_ver_detalles = QPushButton()
        self.boton_cargar_presupuesto = QPushButton()
        self.boton_emitir_remito = QPushButton()
        botones = [
            (self.boton_crear, "add-entrega.svg", "Crear nuevo pedido"),
            (self.boton_ver_detalles, "search_icon.svg", "Ver detalles del pedido"),
            (self.boton_cargar_presupuesto, "excel_icon.svg", "Cargar presupuesto"),
            (self.boton_emitir_remito, "factura.svg", "Emitir remito")
        ]
        # El orden de los botones está documentado arriba y en checklist_botones_accion.txt para evitar cambios accidentales.
        for boton, icono, tooltip in botones:
            boton.setObjectName(f"boton_{icono.split('.')[0]}")
            icon_path = os.path.join(icon_dir, icono)
            boton.setIcon(QIcon(icon_path))
            boton.setIconSize(QSize(24, 24))
            boton.setToolTip(tooltip)
            boton.setText("")
            estilizar_boton_icono(boton)
            header_layout.addWidget(boton, alignment=Qt.AlignmentFlag.AlignVCenter)
        main_layout.insertLayout(0, header_layout)

        # Tabla principal de pedidos
        self.pedidos_headers = ["id", "proveedor", "fecha", "estado", "total"]
        self.tabla_pedidos = QTableWidget()
        self.tabla_pedidos.setObjectName("tabla_pedidos")
        self.tabla_pedidos.setColumnCount(len(self.pedidos_headers))
        self.tabla_pedidos.setHorizontalHeaderLabels(self.pedidos_headers)
        self.make_table_responsive(self.tabla_pedidos)
        self.tabla_pedidos.setAlternatingRowColors(True)

        # Configuración de columnas visibles (debe ir antes de conectar señales que usan columnas_visibles_pedidos)
        self.config_path_pedidos = f"config_compras_pedidos_columns.json"
        self.columnas_visibles_pedidos = self.cargar_config_columnas(self.config_path_pedidos, self.pedidos_headers)

        self.tabla_pedidos.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_pedidos.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        v_header = self.tabla_pedidos.verticalHeader()
        if v_header is not None:
            v_header.setVisible(False)
        h_header = self.tabla_pedidos.horizontalHeader()
        if h_header is not None:
            h_header.setProperty("header", True)
            h_header.setHighlightSections(False)
            h_header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
            h_header.setMinimumSectionSize(80)
            h_header.setDefaultSectionSize(120)
            h_header.setSectionsMovable(True)
            h_header.setSectionsClickable(True)
            h_header.setObjectName("header_pedidos")
            h_header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            h_header.customContextMenuRequested.connect(partial(self.mostrar_menu_columnas, self.tabla_pedidos, self.pedidos_headers, self.columnas_visibles_pedidos, self.config_path_pedidos))
            h_header.sectionDoubleClicked.connect(partial(self.auto_ajustar_columna, self.tabla_pedidos))
            h_header.sectionClicked.connect(partial(self.mostrar_menu_columnas_header, self.tabla_pedidos, self.pedidos_headers, self.columnas_visibles_pedidos, self.config_path_pedidos))
        self.tabla_pedidos.setMinimumHeight(520)
        self.tabla_pedidos.setMaximumHeight(900)
        main_layout.addWidget(self.tabla_pedidos)
        main_layout.addStretch()

        self.aplicar_columnas_visibles(self.tabla_pedidos, self.pedidos_headers, self.columnas_visibles_pedidos)
        self.tabla_pedidos.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tabla_pedidos.customContextMenuRequested.connect(partial(self.mostrar_menu_columnas, self.tabla_pedidos, self.pedidos_headers, self.columnas_visibles_pedidos, self.config_path_pedidos))
        self.tabla_pedidos.itemSelectionChanged.connect(partial(self.mostrar_qr_item_seleccionado, self.tabla_pedidos))

        # Accesibilidad y estilos de botones y labels
        for btn in [self.boton_crear, self.boton_ver_detalles, self.boton_cargar_presupuesto, self.boton_emitir_remito]:
            btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            font = btn.font()
            if font.pointSize() < 12:
                font.setPointSize(12)
            btn.setFont(font)
            if not btn.toolTip():
                btn.setToolTip("Botón de acción")
            if not btn.accessibleName():
                btn.setAccessibleName("Botón de acción de pedidos")
        self.tabla_pedidos.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.tabla_pedidos.setToolTip("Tabla de pedidos")
        self.tabla_pedidos.setAccessibleName("Tabla principal de pedidos")
        for widget in self.findChildren(QLabel):
            font = widget.font()
            if font.pointSize() < 12:
                font.setPointSize(12)
            widget.setFont(font)

        # Márgenes y padding en layouts según estándar (ya aplicados arriba)
        # main_layout.setContentsMargins(32, 32, 32, 32)
        # main_layout.setSpacing(16)
        # No hay buscador en la vista principal

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

    def mostrar_feedback(self, mensaje, tipo="info"):
        from PyQt6.QtWidgets import QMessageBox
        if tipo == "error":
            QMessageBox.critical(self, "Error", mensaje)
        elif tipo == "advertencia":
            QMessageBox.warning(self, "Advertencia", mensaje)
        else:
            QMessageBox.information(self, "Información", mensaje)

    def mostrar_menu_columnas_header(self, tabla, headers, columnas_visibles, config_path, idx):
        from PyQt6.QtCore import QPoint
        try:
            header = tabla.horizontalHeader()
            if header is not None and all(hasattr(header, m) for m in ['sectionPosition', 'mapToGlobal', 'sectionViewportPosition']):
                if idx < 0 or idx >= tabla.columnCount():
                    self.mostrar_feedback("Índice de columna fuera de rango", "error")
                    return
                pos = header.sectionPosition(idx)
                global_pos = header.mapToGlobal(QPoint(header.sectionViewportPosition(idx), 0))
                self.mostrar_menu_columnas(tabla, headers, columnas_visibles, config_path, global_pos)
            else:
                self.mostrar_feedback("No se puede mostrar el menú de columnas: header no disponible o incompleto", "error")
        except Exception as e:
            self.mostrar_feedback(f"Error al mostrar menú de columnas: {e}", "error")

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

    def mostrar_dialogo_cargar_presupuesto(self):
        """
        Diálogo moderno y accesible para cargar presupuesto, con paddings, tooltips y sombra en botones.
        """
        dialog = QDialog(self)
        dialog.setWindowTitle("Cargar presupuesto")
        dialog.setObjectName("dialogo_cargar_presupuesto")
        vbox = QVBoxLayout(dialog)
        vbox.setContentsMargins(24, 24, 24, 24)
        vbox.setSpacing(16)
        label = QLabel("Selecciona el archivo de presupuesto a cargar:")
        label.setAccessibleName("Label seleccionar archivo presupuesto")
        vbox.addWidget(label)
        input_archivo = QLineEdit()
        input_archivo.setPlaceholderText("Ruta del archivo .xlsx o .csv")
        input_archivo.setToolTip("Selecciona o ingresa la ruta del archivo de presupuesto")
        vbox.addWidget(input_archivo)
        btns = QHBoxLayout()
        btn_examinar = QPushButton("Examinar")
        btn_examinar.setToolTip("Buscar archivo de presupuesto")
        estilizar_boton_icono(btn_examinar)
        sombra_examinar = QGraphicsDropShadowEffect()
        sombra_examinar.setBlurRadius(12)
        sombra_examinar.setXOffset(0)
        sombra_examinar.setYOffset(2)
        sombra_examinar.setColor(QColor(0, 0, 0, 40))
        btn_examinar.setGraphicsEffect(sombra_examinar)
        btn_cargar = QPushButton("Cargar")
        btn_cargar.setToolTip("Cargar presupuesto seleccionado")
        estilizar_boton_icono(btn_cargar)
        sombra_cargar = QGraphicsDropShadowEffect()
        sombra_cargar.setBlurRadius(12)
        sombra_cargar.setXOffset(0)
        sombra_cargar.setYOffset(2)
        sombra_cargar.setColor(QColor(0, 0, 0, 40))
        btn_cargar.setGraphicsEffect(sombra_cargar)
        btns.addWidget(btn_examinar)
        btns.addWidget(btn_cargar)
        vbox.addLayout(btns)
        def examinar():
            file_path, _ = QFileDialog.getOpenFileName(dialog, "Seleccionar archivo de presupuesto", "", "Archivos Excel (*.xlsx);;Archivos CSV (*.csv)")
            if file_path:
                input_archivo.setText(file_path)
        btn_examinar.clicked.connect(examinar)
        def cargar():
            # Aquí se debe implementar la lógica real de carga
            dialog.accept()
        btn_cargar.clicked.connect(cargar)
        dialog.exec()

    def mostrar_dialogo_crear_pedido(self, proveedores=None):
        """
        Diálogo para crear pedido con búsqueda rápida de proveedores (autocompletado).
        """
        dialog = QDialog(self)
        dialog.setWindowTitle("Crear nuevo pedido")
        dialog.setObjectName("dialogo_crear_pedido")
        vbox = QVBoxLayout(dialog)
        vbox.setContentsMargins(24, 24, 24, 24)
        vbox.setSpacing(16)
        label = QLabel("Proveedor:")
        vbox.addWidget(label)
        input_proveedor = QLineEdit()
        input_proveedor.setPlaceholderText("Buscar proveedor...")
        input_proveedor.setToolTip("Escribe para buscar proveedores existentes")
        if proveedores:
            from PyQt6.QtWidgets import QCompleter
            completer = QCompleter(proveedores)
            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            input_proveedor.setCompleter(completer)
        vbox.addWidget(input_proveedor)
        btns = QHBoxLayout()
        btn_crear = QPushButton("Crear")
        btn_crear.setToolTip("Crear pedido con proveedor seleccionado")
        estilizar_boton_icono(btn_crear)
        sombra_crear = QGraphicsDropShadowEffect()
        sombra_crear.setBlurRadius(12)
        sombra_crear.setXOffset(0)
        sombra_crear.setYOffset(2)
        sombra_crear.setColor(QColor(0, 0, 0, 40))
        btn_crear.setGraphicsEffect(sombra_crear)
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setToolTip("Cancelar creación de pedido")
        estilizar_boton_icono(btn_cancelar)
        sombra_cancelar = QGraphicsDropShadowEffect()
        sombra_cancelar.setBlurRadius(12)
        sombra_cancelar.setXOffset(0)
        sombra_cancelar.setYOffset(2)
        sombra_cancelar.setColor(QColor(0, 0, 0, 40))
        btn_cancelar.setGraphicsEffect(sombra_cancelar)
        btns.addWidget(btn_crear)
        btns.addWidget(btn_cancelar)
        vbox.addLayout(btns)
        btn_cancelar.clicked.connect(dialog.reject)
        btn_crear.clicked.connect(lambda: dialog.accept())
        dialog.exec()
# Todas las líneas setStyleSheet comentadas corresponden a estilos migrados a QSS global. Ver docs/estandares_visuales.md
