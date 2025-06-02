from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QFormLayout, QLineEdit, QComboBox, QPushButton, QLabel, QHBoxLayout, QGraphicsDropShadowEffect, QMenu, QHeaderView, QMessageBox
from PyQt6.QtGui import QIcon, QColor, QAction
from PyQt6.QtCore import Qt, QSize
import json
import os
from functools import partial
from core.ui_components import estilizar_boton_icono, aplicar_qss_global_y_tema

class PedidosView(QWidget):
    def __init__(self, usuario_actual="default"):
        super().__init__()
        self.usuario_actual = usuario_actual
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(24, 20, 24, 20)
        self.main_layout.setSpacing(16)

        # HEADER VISUAL MODERNO
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(24)
        self.label_titulo = QLabel("Gestión de Pedidos")
        header_layout.addWidget(self.label_titulo, alignment=Qt.AlignmentFlag.AlignVCenter)
        # Botón principal (Agregar pedido)
        self.boton_agregar = QPushButton()
        self.boton_agregar.setIcon(QIcon("img/add-entrega.svg"))
        self.boton_agregar.setIconSize(QSize(24, 24))
        self.boton_agregar.setToolTip("Agregar pedido")
        header_layout.addWidget(self.boton_agregar)
        header_layout.addStretch()
        self.main_layout.addLayout(header_layout)

        # Tabla de pedidos
        self.tabla_pedidos = QTableWidget()
        self.tabla_pedidos.setColumnCount(5)
        self.pedidos_headers = ["id", "obra", "fecha", "estado", "observaciones"]
        self.tabla_pedidos.setHorizontalHeaderLabels(self.pedidos_headers)
        self.tabla_pedidos.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        # self.tabla_pedidos.setStyleSheet(self.tabla_pedidos.styleSheet() + "\nQTableWidget:focus { outline: 2px solid #2563eb; border: 2px solid #2563eb; }\nQTableWidget { font-size: 13px; }")
        self.tabla_pedidos.setToolTip("Tabla de pedidos")
        self.tabla_pedidos.setAccessibleName("Tabla principal de pedidos")
        self.main_layout.addWidget(self.tabla_pedidos)

        # Configuración de columnas
        self.config_path = f"config_pedidos_columns_{self.usuario_actual}.json"
        self.columnas_visibles = self.cargar_config_columnas()
        self.aplicar_columnas_visibles()
        header = self.tabla_pedidos.horizontalHeader()
        if header is not None:
            header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            header.customContextMenuRequested.connect(self.mostrar_menu_columnas)
            header.sectionDoubleClicked.connect(self.auto_ajustar_columna)
            header.setSectionsMovable(True)
            header.setSectionsClickable(True)
            header.sectionClicked.connect(self.mostrar_menu_columnas_header)
            try:
                # header.setStyleSheet("background-color: #e3f6fd; color: #2563eb; border-radius: 8px; font-size: 10px; padding: 8px 12px; border: 1px solid #e3e3e3;")
                pass
            except Exception:
                pass
        # Señal para mostrar QR al seleccionar un ítem
        self.tabla_pedidos.itemSelectionChanged.connect(self.mostrar_qr_item_seleccionado)

        # --- FEEDBACK VISUAL CENTRALIZADO Y QSS GLOBAL ---
        self.label_feedback = QLabel()
        self.label_feedback.setObjectName("label_feedback")
        # QSS global gestiona el estilo del feedback visual, no usar setStyleSheet embebido
        self.label_feedback.setVisible(False)
        self.label_feedback.setAccessibleName("Mensaje de feedback de pedidos")
        self.label_feedback.setAccessibleDescription("Mensaje de feedback visual y accesible para el usuario")
        self.main_layout.addWidget(self.label_feedback)
        self._feedback_timer = None

        # Formulario para nuevo pedido
        self.form_layout = QFormLayout()
        self.obra_combo = QComboBox()
        self.fecha_pedido = QLineEdit()
        self.materiales_input = QLineEdit()
        self.observaciones_input = QLineEdit()
        self.form_layout.addRow("Obra Asociada:", self.obra_combo)
        self.form_layout.addRow("Fecha de Pedido:", self.fecha_pedido)
        self.form_layout.addRow("Lista de Materiales:", self.materiales_input)
        self.form_layout.addRow("Observaciones:", self.observaciones_input)
        self.main_layout.addLayout(self.form_layout)

        # Márgenes y padding en layouts según estándar
        self.main_layout.setContentsMargins(24, 20, 24, 20)
        self.main_layout.setSpacing(16)
        # Refuerzo de accesibilidad en inputs
        for widget in [self.obra_combo, self.fecha_pedido, self.materiales_input, self.observaciones_input]:
            widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            font = widget.font()
            if font.pointSize() < 12:
                font.setPointSize(12)
            widget.setFont(font)
            if not widget.toolTip():
                widget.setToolTip("Campo de texto")
            if not widget.accessibleName():
                widget.setAccessibleName("Campo de texto de pedidos")
        # Refuerzo de accesibilidad en QLabel
        for widget in self.findChildren(QLabel):
            font = widget.font()
            if font.pointSize() < 12:
                font.setPointSize(12)
            widget.setFont(font)

        # Señales
        self.boton_nuevo.clicked.connect(self.crear_pedido)

        # Aplicar QSS global y tema visual (solo desde resources/qss/)
        from utils.theme_manager import cargar_modo_tema
        tema = cargar_modo_tema()
        qss_tema = f"resources/qss/theme_{tema}.qss"
        aplicar_qss_global_y_tema(self, qss_global_path="resources/qss/theme_light.qss", qss_tema_path=qss_tema)

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
        # self.label_feedback.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 13px; border-radius: 8px; padding: 8px; background: #f1f5f9;")
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

    def cargar_config_columnas(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {header: True for header in self.pedidos_headers}

    def guardar_config_columnas(self):
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.columnas_visibles, f, ensure_ascii=False, indent=2)
        QMessageBox.information(self, "Configuración guardada", "La configuración de columnas se ha guardado correctamente.")

    def aplicar_columnas_visibles(self):
        for idx, header in enumerate(self.pedidos_headers):
            visible = self.columnas_visibles.get(header, True)
            self.tabla_pedidos.setColumnHidden(idx, not visible)

    def mostrar_menu_columnas(self, pos):
        menu = QMenu(self)
        for idx, header in enumerate(self.pedidos_headers):
            accion = QAction(header, self)
            accion.setCheckable(True)
            accion.setChecked(self.columnas_visibles.get(header, True))
            accion.toggled.connect(partial(self.toggle_columna, idx, header))
            menu.addAction(accion)
        header = self.tabla_pedidos.horizontalHeader()
        if header is not None:
            menu.exec(header.mapToGlobal(pos))
        else:
            menu.exec(pos)

    def mostrar_menu_columnas_header(self, idx):
        header = self.tabla_pedidos.horizontalHeader()
        if header is not None:
            from PyQt6.QtCore import QPoint
            pos = header.sectionPosition(idx)
            global_pos = header.mapToGlobal(QPoint(header.sectionViewportPosition(idx), 0))
            self.mostrar_menu_columnas(global_pos)

    def toggle_columna(self, idx, header, checked):
        self.columnas_visibles[header] = checked
        self.tabla_pedidos.setColumnHidden(idx, not checked)
        self.guardar_config_columnas()

    def auto_ajustar_columna(self, idx):
        self.tabla_pedidos.resizeColumnToContents(idx)

    def mostrar_qr_item_seleccionado(self):
        from PyQt6.QtGui import QPixmap
        import qrcode
        from PyQt6.QtWidgets import QDialog, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QFileDialog
        selected = self.tabla_pedidos.selectedItems()
        if not selected:
            return
        row = selected[0].row()
        item = self.tabla_pedidos.item(row, 0)
        if item is None or not hasattr(item, 'text'):
            return
        codigo = item.text()  # Usar el id o código como dato QR
        if not codigo:
            return
        qr = qrcode.QRCode(version=1, box_size=6, border=2)
        qr.add_data(codigo)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        import tempfile
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
                with open(tmp_path, "rb") as src, open(file_path, "wb") as dst:
                    dst.write(src.read())
        def exportar_pdf():
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            file_path, _ = QFileDialog.getSaveFileName(dialog, "Exportar QR a PDF", f"qr_{codigo}.pdf", "Archivo PDF (*.pdf)")
            if file_path:
                c = canvas.Canvas(file_path, pagesize=letter)
                c.drawInlineImage(tmp_path, 100, 500, 200, 200)
                c.save()
        btn_guardar.clicked.connect(guardar)
        btn_pdf.clicked.connect(exportar_pdf)
        dialog.exec()

    def crear_pedido(self):
        self.mostrar_feedback("Funcionalidad de crear pedido pendiente de implementación", tipo="info")

    def eliminar_pedido(self):
        self.mostrar_feedback("Funcionalidad de eliminar pedido pendiente de implementación", tipo="info")

    def cargar_pedidos(self):
        self.mostrar_feedback("Funcionalidad de cargar pedidos pendiente de implementación", tipo="info")

    def aprobar_pedido(self):
        self.mostrar_feedback("Funcionalidad de aprobar pedido pendiente de implementación", tipo="info")

    def rechazar_pedido(self):
        self.mostrar_feedback("Funcionalidad de rechazar pedido pendiente de implementación", tipo="info")

# NOTA: No debe haber credenciales ni cadenas de conexión hardcodeadas como 'server=' en este archivo. Usar variables de entorno o archivos de configuración seguros.
# Si necesitas una cadena de conexión, obténla de un archivo seguro o variable de entorno, nunca hardcodeada.
# En los flujos de error, asegúrate de usar log_error y/o registrar_evento para cumplir el estándar de feedback visual y logging.
