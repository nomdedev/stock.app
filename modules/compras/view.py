import os
import json
import tempfile
import qrcode
from PyQt6.QtWidgets import QWidget, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QTabWidget, QLabel, QLineEdit, QHBoxLayout, QGraphicsDropShadowEffect, QMenu, QFileDialog, QDialog
from PyQt6.QtGui import QIcon, QColor, QPixmap, QPainter, QAction
from PyQt6.QtCore import QSize, Qt, QPoint
from PyQt6.QtPrintSupport import QPrinter
from functools import partial
from modules.compras.pedidos.view import PedidosView  # Importar desde el módulo correcto
from core.table_responsive_mixin import TableResponsiveMixin
from core.ui_components import estilizar_boton_icono

class ComprasView(QWidget, TableResponsiveMixin):
    def __init__(self):
        super().__init__()
        self.main_layout = QVBoxLayout(self)
        self.inicializar_botones()

        # Cargar el stylesheet visual moderno para Compras según el tema activo
        try:
            with open("themes/config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
            tema = config.get("tema", "claro")
            archivo_qss = f"themes/{tema}.qss"
            with open(archivo_qss, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"No se pudo cargar el archivo de estilos de Compras según el tema: {e}")

        # Crear QTabWidget para las pestañas
        self.tab_widget = QTabWidget()

        # Crear pestaña de Pedidos
        self.tab_pedidos = PedidosView()
        self.tab_widget.addTab(self.tab_pedidos, "Pedidos")

        # Aplicar patrón responsive a la tabla principal de Pedidos si existe
        if hasattr(self.tab_pedidos, 'tabla_pedidos'):
            self.tab_pedidos.make_table_responsive(self.tab_pedidos.tabla_pedidos)

        # Agregar el QTabWidget al layout principal
        self.main_layout.addWidget(self.tab_widget)

        # --- FEEDBACK VISUAL GLOBAL (accesible, visible siempre arriba del QTabWidget) ---
        self.label_feedback = QLabel()
        self.label_feedback.setStyleSheet("font-size: 13px; border-radius: 8px; padding: 8px; font-weight: 500; background: #f1f5f9;")
        self.label_feedback.setVisible(False)
        self.label_feedback.setAccessibleName("Feedback visual de Compras")
        self.main_layout.addWidget(self.label_feedback)
        # --- FIN FEEDBACK VISUAL GLOBAL ---

        self.comparacion_headers = ["proveedor", "precio_total", "comentarios"]
        self.config_path_comparacion = f"config_compras_comparacion_columns.json"
        self.columnas_visibles_comparacion = self.cargar_config_columnas(self.config_path_comparacion, self.comparacion_headers)

        self._feedback_timer = None  # Temporizador para feedback visual

    def inicializar_botones(self):
        # Botón principal de acción (Nuevo pedido)
        botones_layout = QHBoxLayout()
        self.boton_nuevo = QPushButton()
        self.boton_nuevo.setIcon(QIcon("img/add-entrega.svg"))
        self.boton_nuevo.setIconSize(QSize(24, 24))
        self.boton_nuevo.setToolTip("Nuevo pedido")
        self.boton_nuevo.setText("")
        self.boton_nuevo.setFixedSize(48, 48)
        self.boton_nuevo.setStyleSheet("")
        sombra = QGraphicsDropShadowEffect()
        sombra.setBlurRadius(15)
        sombra.setXOffset(0)
        sombra.setYOffset(4)
        sombra.setColor(QColor(0, 0, 0, 50))
        self.boton_nuevo.setGraphicsEffect(sombra)
        botones_layout.addWidget(self.boton_nuevo)
        botones_layout.addStretch()
        self.main_layout.addLayout(botones_layout)

        # Refuerzo de accesibilidad en botón principal
        self.boton_nuevo.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.boton_nuevo.setStyleSheet(self.boton_nuevo.styleSheet() + "\nQPushButton:focus { outline: 2px solid #2563eb; border: 2px solid #2563eb; }")
        font = self.boton_nuevo.font()
        if font.pointSize() < 12:
            font.setPointSize(12)
        self.boton_nuevo.setFont(font)
        if not self.boton_nuevo.toolTip():
            self.boton_nuevo.setToolTip("Nuevo pedido")
        # Refuerzo de accesibilidad en tabla de comparación si existe
        if hasattr(self, 'tabla_comparacion'):
            self.tabla_comparacion.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            self.tabla_comparacion.setStyleSheet(self.tabla_comparacion.styleSheet() + "\nQTableWidget:focus { outline: 2px solid #2563eb; border: 2px solid #2563eb; }\nQTableWidget { font-size: 13px; }")
        # EXCEPCIÓN: Si algún botón requiere texto visible por UX, debe estar documentado aquí y en docs/estandares_visuales.md

    def mostrar_comparacion_presupuestos(self, presupuestos):
        self.tabla_comparacion = QTableWidget()
        self.tabla_comparacion.setRowCount(len(presupuestos))
        self.tabla_comparacion.setColumnCount(3)
        self.tabla_comparacion.setHorizontalHeaderLabels(self.comparacion_headers)
        self.make_table_responsive(self.tabla_comparacion)

        for row_idx, presupuesto in enumerate(presupuestos):
            self.tabla_comparacion.setItem(row_idx, 0, QTableWidgetItem(presupuesto[0]))
            self.tabla_comparacion.setItem(row_idx, 1, QTableWidgetItem(str(presupuesto[1])))
            self.tabla_comparacion.setItem(row_idx, 2, QTableWidgetItem(presupuesto[2]))

        self.main_layout.addWidget(self.tabla_comparacion)

        # Configuración de columnas y persistencia para tabla_comparacion
        self.aplicar_columnas_visibles(self.tabla_comparacion, self.comparacion_headers, self.columnas_visibles_comparacion)
        header_comp = self.tabla_comparacion.horizontalHeader()
        if header_comp:
            header_comp.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            header_comp.customContextMenuRequested.connect(partial(self.mostrar_menu_columnas, self.tabla_comparacion, self.comparacion_headers, self.columnas_visibles_comparacion, self.config_path_comparacion))
            header_comp.sectionDoubleClicked.connect(partial(self.auto_ajustar_columna, self.tabla_comparacion))
            header_comp.setSectionsMovable(True)
            header_comp.setSectionsClickable(True)
            header_comp.sectionClicked.connect(partial(self.mostrar_menu_columnas_header, self.tabla_comparacion, self.comparacion_headers, self.columnas_visibles_comparacion, self.config_path_comparacion))
            self.tabla_comparacion.setHorizontalHeader(header_comp)
        self.tabla_comparacion.itemSelectionChanged.connect(partial(self.mostrar_qr_item_seleccionado, self.tabla_comparacion))

        # Refuerzo visual y robustez en header de tabla de comparación (si existe)
        if hasattr(self, 'tabla_comparacion'):
            header_comp = self.tabla_comparacion.horizontalHeader() if hasattr(self.tabla_comparacion, 'horizontalHeader') else None
            if header_comp is not None:
                try:
                    header_comp.setStyleSheet("background-color: #e3f6fd; color: #2563eb; border-radius: 8px; font-size: 10px; padding: 8px 12px; border: 1px solid #e3e3e3;")
                except Exception:
                    pass
            else:
                # EXCEPCIÓN VISUAL: No se puede aplicar refuerzo visual porque el header es None
                pass

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
        pil_img = img.get_image() if hasattr(img, 'get_image') else img
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            pil_img.save(tmp)
            pixmap = QPixmap(tmp.name)
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
        colores = {
            "info": "background: #e3f6fd; color: #2563eb;",
            "exito": "background: #d1f7e7; color: #15803d;",
            "advertencia": "background: #fef9c3; color: #b45309;",
            "error": "background: #fee2e2; color: #b91c1c;"
        }
        iconos = {
            "info": "ℹ️ ",
            "exito": "✅ ",
            "advertencia": "⚠️ ",
            "error": "❌ "
        }
        self.label_feedback.setStyleSheet(f"font-size: 13px; border-radius: 8px; padding: 8px; font-weight: 500; {colores.get(tipo, '')}")
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

    @property
    def label(self):
        if not hasattr(self, '_label_estado'):
            self._label_estado = QLabel()
        return self._label_estado

    @property
    def buscar_input(self):
        if not hasattr(self, '_buscar_input'):
            self._buscar_input = QLineEdit()
        return self._buscar_input

    @property
    def id_item_input(self):
        if not hasattr(self, '_id_item_input'):
            self._id_item_input = QLineEdit()
        return self._id_item_input