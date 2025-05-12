from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QFormLayout, QLineEdit, QComboBox, QPushButton, QLabel, QHBoxLayout, QGraphicsDropShadowEffect, QMenu, QHeaderView, QMessageBox
from PyQt6.QtGui import QIcon, QColor, QAction
from PyQt6.QtCore import Qt, QSize
import json
import os
from functools import partial

class PedidosView(QWidget):
    def __init__(self, usuario_actual="default"):
        super().__init__()
        self.usuario_actual = usuario_actual
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Cargar el stylesheet visual moderno para Pedidos según el tema activo
        try:
            with open("themes/config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
            tema = config.get("tema", "claro")
            archivo_qss = f"themes/{tema}.qss"
            with open(archivo_qss, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"No se pudo cargar el archivo de estilos: {e}")

        # Tabla de pedidos
        self.tabla_pedidos = QTableWidget()
        self.tabla_pedidos.setColumnCount(5)
        self.tabla_pedidos.setHorizontalHeaderLabels([
            "id", "obra", "fecha", "estado", "observaciones"
        ])
        self.layout.addWidget(self.tabla_pedidos)

        # Configuración de columnas
        self.config_path = f"config_pedidos_columns_{self.usuario_actual}.json"
        self.pedidos_headers = ["id", "obra", "fecha", "estado", "observaciones"]
        self.columnas_visibles = self.cargar_config_columnas()
        self.aplicar_columnas_visibles()

        # Menú contextual en el header
        header = self.tabla_pedidos.horizontalHeader()
        header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        header.customContextMenuRequested.connect(self.mostrar_menu_columnas)
        header.sectionDoubleClicked.connect(self.auto_ajustar_columna)
        header.setSectionsMovable(True)
        header.setSectionsClickable(True)
        header.sectionClicked.connect(self.mostrar_menu_columnas_header)
        self.tabla_pedidos.setHorizontalHeader(header)

        # Señal para mostrar QR al seleccionar un ítem
        self.tabla_pedidos.itemSelectionChanged.connect(self.mostrar_qr_item_seleccionado)

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
        self.layout.addLayout(self.form_layout)

        # Botón principal de acción (Agregar pedido)
        self.botones_layout = QHBoxLayout()
        self.boton_nuevo = QPushButton()
        self.boton_nuevo.setIcon(QIcon("img/add-entrega.svg"))
        self.boton_nuevo.setIconSize(QSize(24, 24))
        self.boton_nuevo.setToolTip("Agregar pedido")
        self.boton_nuevo.setText("")
        self.boton_nuevo.setFixedSize(48, 48)
        self.boton_nuevo.setStyleSheet("")
        sombra = QGraphicsDropShadowEffect()
        sombra.setBlurRadius(15)
        sombra.setXOffset(0)
        sombra.setYOffset(4)
        sombra.setColor(QColor(0, 0, 0, 50))
        self.boton_nuevo.setGraphicsEffect(sombra)
        self.botones_layout.addWidget(self.boton_nuevo)
        self.botones_layout.addStretch()
        self.layout.addLayout(self.botones_layout)

        # Ajustar espaciado y alineación para asegurar visibilidad
        self.botones_layout.setSpacing(10)
        self.botones_layout.setContentsMargins(0, 10, 0, 10)
        self.layout.setSpacing(15)

        # Verificar estilos aplicados
        print("Estilos aplicados correctamente a PedidosView.")

        # Señales
        self.boton_nuevo.clicked.connect(self.crear_pedido)

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
        menu.exec(self.tabla_pedidos.horizontalHeader().mapToGlobal(pos))

    def mostrar_menu_columnas_header(self, idx):
        pos = self.tabla_pedidos.horizontalHeader().sectionPosition(idx)
        header = self.tabla_pedidos.horizontalHeader()
        global_pos = header.mapToGlobal(header.sectionViewportPosition(idx), 0)
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
        codigo = self.tabla_pedidos.item(row, 0).text()  # Usar el id o código como dato QR
        if not codigo:
            return
        qr = qrcode.QRCode(version=1, box_size=6, border=2)
        qr.add_data(codigo)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        import tempfile
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
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            file_path, _ = QFileDialog.getSaveFileName(dialog, "Exportar QR a PDF", f"qr_{codigo}.pdf", "Archivo PDF (*.pdf)")
            if file_path:
                c = canvas.Canvas(file_path, pagesize=letter)
                c.drawInlineImage(tmp.name, 100, 500, 200, 200)
                c.save()
        btn_guardar.clicked.connect(guardar)
        btn_pdf.clicked.connect(exportar_pdf)
        dialog.exec()

    def crear_pedido(self):
        pass

    def eliminar_pedido(self):
        pass

    def cargar_pedidos(self):
        pass

    def aprobar_pedido(self):
        pass

    def rechazar_pedido(self):
        pass
