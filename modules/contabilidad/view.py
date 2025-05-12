import os
import json
import tempfile
import qrcode
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QFormLayout, QTableWidget, QHBoxLayout, QGraphicsDropShadowEffect, QMenu, QFileDialog, QDialog, QTabWidget, QMessageBox, QTableWidgetItem, QComboBox
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QIcon, QColor, QPixmap, QPainter, QAction
from PyQt6.QtCore import QSize
from PyQt6.QtPrintSupport import QPrinter
from functools import partial
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class ContabilidadView(QWidget):
    def __init__(self, db_connection=None, obras_model=None):
        super().__init__()
        self.db_connection = db_connection
        self.obras_model = obras_model
        # Inicialización segura de headers para evitar AttributeError
        self.balance_headers = []
        self.recibos_headers = []
        self.pagos_headers = []
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(0)

        self.label_titulo = QLabel("Gestión de Contabilidad y Recibos")
        self.label_titulo.setProperty("class", "contabilidad-titulo")
        self.layout.addWidget(self.label_titulo)

        # QTabWidget para las tres pestañas
        self.tabs = QTabWidget()
        self.tabs.setObjectName("contabilidad-tabs")
        self.layout.addWidget(self.tabs)

        # --- Filtros y búsqueda rápida ---
        self.filtro_balance = QLineEdit()
        self.filtro_balance.setPlaceholderText("Buscar en movimientos...")
        self.filtro_balance.setToolTip("Filtrar movimientos por cualquier campo")
        self.filtro_balance.textChanged.connect(self.filtrar_tabla_balance)

        # --- Pestaña Balance ---
        self.tab_balance = QWidget()
        self.tab_balance_layout = QVBoxLayout()
        self.tab_balance.setLayout(self.tab_balance_layout)
        self.tab_balance_layout.addWidget(self.filtro_balance)
        self.tabla_balance = QTableWidget()
        self.tabla_balance.setObjectName("tabla_balance")
        self.tab_balance_layout.addWidget(self.tabla_balance)
        self.boton_agregar_balance = QPushButton()
        self.boton_agregar_balance.setIcon(QIcon("img/plus_icon.svg"))
        self.boton_agregar_balance.setIconSize(QSize(22, 22))
        self.boton_agregar_balance.setToolTip("Agregar movimiento contable")
        self.boton_agregar_balance.setFixedSize(38, 38)
        self.boton_agregar_balance.setStyleSheet("border-radius: 19px; background: #2563eb; color: white;")
        btn_balance_layout = QHBoxLayout()
        btn_balance_layout.addStretch()
        btn_balance_layout.addWidget(self.boton_agregar_balance)
        self.tab_balance_layout.addLayout(btn_balance_layout)
        self.tabs.addTab(self.tab_balance, "Balance")

        # --- Pestaña Seguimiento de Pagos ---
        self.tab_pagos = QWidget()
        self.tab_pagos_layout = QVBoxLayout()
        self.tab_pagos.setLayout(self.tab_pagos_layout)
        self.filtro_pagos = QLineEdit()
        self.filtro_pagos.setPlaceholderText("Buscar pagos por obra, colocador...")
        self.filtro_pagos.setToolTip("Filtrar pagos por cualquier campo")
        self.filtro_pagos.textChanged.connect(self.filtrar_tabla_pagos)
        self.tab_pagos_layout.addWidget(self.filtro_pagos)
        self.tabla_pagos = QTableWidget()
        self.tabla_pagos.setObjectName("tabla_pagos")
        self.tab_pagos_layout.addWidget(self.tabla_pagos)
        self.tabs.addTab(self.tab_pagos, "Seguimiento de Pagos")

        # --- Pestaña Recibos ---
        self.tab_recibos = QWidget()
        self.tab_recibos_layout = QVBoxLayout()
        self.tab_recibos.setLayout(self.tab_recibos_layout)
        self.filtro_recibos = QLineEdit()
        self.filtro_recibos.setPlaceholderText("Buscar recibos por obra, concepto, destinatario...")
        self.filtro_recibos.setToolTip("Filtrar recibos por cualquier campo")
        self.filtro_recibos.textChanged.connect(self.filtrar_tabla_recibos)
        self.tab_recibos_layout.addWidget(self.filtro_recibos)
        # Layout horizontal para botón agregar (arriba a la derecha)
        top_btn_layout = QHBoxLayout()
        top_btn_layout.addStretch()
        self.boton_agregar_recibo = QPushButton()
        self.boton_agregar_recibo.setIcon(QIcon("img/plus_icon.svg"))
        self.boton_agregar_recibo.setIconSize(QSize(24, 24))
        self.boton_agregar_recibo.setToolTip("Agregar nuevo recibo")
        self.boton_agregar_recibo.setFixedSize(40, 40)
        self.boton_agregar_recibo.setStyleSheet("border-radius: 20px; background: #2563eb; color: white;")
        top_btn_layout.addWidget(self.boton_agregar_recibo)
        self.tab_recibos_layout.addLayout(top_btn_layout)
        # Tabla de recibos
        self.tabla_recibos = QTableWidget()
        self.tabla_recibos.setObjectName("tabla_recibos")
        self.tab_recibos_layout.addWidget(self.tabla_recibos)
        self.tabs.addTab(self.tab_recibos, "Recibos")

        # --- Pestaña Estadísticas ---
        self.tab_estadisticas = QWidget()
        self.tab_estadisticas_layout = QVBoxLayout()
        self.tab_estadisticas.setLayout(self.tab_estadisticas_layout)
        self.label_resumen = QLabel("Resumen de Balance")
        self.tab_estadisticas_layout.addWidget(self.label_resumen)
        # Controles para filtros y tipo de gráfico
        controles_layout = QHBoxLayout()
        self.combo_tipo_grafico = QComboBox()
        self.combo_tipo_grafico.addItems([
            "Ingresos vs Egresos", "Cobros por Obra", "Pagos por Obra", "Evolución Mensual", "Desglose por Moneda"
        ])
        self.combo_tipo_grafico.setToolTip("Seleccionar tipo de gráfico estadístico")
        controles_layout.addWidget(QLabel("Tipo de gráfico:"))
        controles_layout.addWidget(self.combo_tipo_grafico)
        self.combo_anio = QComboBox()
        self.combo_anio.setToolTip("Año a analizar")
        controles_layout.addWidget(QLabel("Año:"))
        controles_layout.addWidget(self.combo_anio)
        self.combo_mes = QComboBox()
        self.combo_mes.addItems(["Todos"] + [str(m) for m in range(1, 13)])
        self.combo_mes.setToolTip("Mes a analizar")
        controles_layout.addWidget(QLabel("Mes:"))
        controles_layout.addWidget(self.combo_mes)
        self.input_dolar = QLineEdit()
        self.input_dolar.setPlaceholderText("Valor dólar oficial")
        self.input_dolar.setToolTip("Ingrese el valor del dólar para conversión")
        controles_layout.addWidget(QLabel("Dólar:"))
        controles_layout.addWidget(self.input_dolar)
        self.boton_actualizar_grafico = QPushButton("Actualizar gráfico")
        self.boton_actualizar_grafico.setToolTip("Actualizar estadísticas con los filtros seleccionados")
        controles_layout.addWidget(self.boton_actualizar_grafico)
        self.boton_estadistica_personalizada = QPushButton("Estadística Personalizada")
        self.boton_estadistica_personalizada.setToolTip("Crear y guardar una estadística personalizada")
        controles_layout.addWidget(self.boton_estadistica_personalizada)
        self.boton_estadistica_personalizada.clicked.connect(self.abrir_dialogo_estadistica_personalizada)
        # Combo para estadísticas personalizadas
        self.combo_estadistica_personalizada = QComboBox()
        self.combo_estadistica_personalizada.setToolTip("Seleccionar estadística personalizada guardada")
        self.combo_estadistica_personalizada.addItem("(Ninguna personalizada)")
        self.combo_estadistica_personalizada.currentIndexChanged.connect(self.seleccionar_estadistica_personalizada)
        controles_layout.addWidget(QLabel("Personalizada:"))
        controles_layout.addWidget(self.combo_estadistica_personalizada)
        self.tab_estadisticas_layout.addLayout(controles_layout)
        self.grafico_canvas = FigureCanvas(Figure(figsize=(6, 4)))
        self.tab_estadisticas_layout.addWidget(self.grafico_canvas)
        self.setup_exportar_grafico_btn()
        self.tabs.addTab(self.tab_estadisticas, "Estadísticas")

        # Señales para actualizar el gráfico
        self.boton_actualizar_grafico.clicked.connect(self.actualizar_grafico_estadisticas)
        self.combo_tipo_grafico.currentIndexChanged.connect(self.actualizar_grafico_estadisticas)
        self.combo_anio.currentIndexChanged.connect(self.actualizar_grafico_estadisticas)
        self.combo_mes.currentIndexChanged.connect(self.actualizar_grafico_estadisticas)
        self.input_dolar.editingFinished.connect(self.actualizar_grafico_estadisticas)

        self.setLayout(self.layout)

        # --- Sincronización dinámica de headers ---
        self.sync_headers()

        # Configuración de columnas y persistencia para cada tabla
        self.config_path_balance = f"config_contabilidad_balance_columns.json"
        self.config_path_pagos = f"config_contabilidad_pagos_columns.json"
        self.config_path_recibos = f"config_contabilidad_recibos_columns.json"
        self.columnas_visibles_balance = self.cargar_config_columnas(self.config_path_balance, self.balance_headers)
        self.columnas_visibles_pagos = self.cargar_config_columnas(self.config_path_pagos, self.pagos_headers)
        self.columnas_visibles_recibos = self.cargar_config_columnas(self.config_path_recibos, self.recibos_headers)
        self.aplicar_columnas_visibles(self.tabla_balance, self.balance_headers, self.columnas_visibles_balance)
        self.aplicar_columnas_visibles(self.tabla_pagos, self.pagos_headers, self.columnas_visibles_pagos)
        self.aplicar_columnas_visibles(self.tabla_recibos, self.recibos_headers, self.columnas_visibles_recibos)

        # Menú de columnas y QR para cada tabla
        header_balance = self.tabla_balance.horizontalHeader()
        header_balance.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        header_balance.customContextMenuRequested.connect(partial(self.mostrar_menu_columnas, self.tabla_balance, self.balance_headers, self.columnas_visibles_balance, self.config_path_balance))
        header_balance.sectionDoubleClicked.connect(partial(self.auto_ajustar_columna, self.tabla_balance))
        header_balance.setSectionsMovable(True)
        header_balance.setSectionsClickable(True)
        self.tabla_balance.setHorizontalHeader(header_balance)

        header_pagos = self.tabla_pagos.horizontalHeader()
        header_pagos.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        header_pagos.customContextMenuRequested.connect(partial(self.mostrar_menu_columnas, self.tabla_pagos, self.pagos_headers, self.columnas_visibles_pagos, self.config_path_pagos))
        header_pagos.sectionDoubleClicked.connect(partial(self.auto_ajustar_columna, self.tabla_pagos))
        header_pagos.setSectionsMovable(True)
        header_pagos.setSectionsClickable(True)
        self.tabla_pagos.setHorizontalHeader(header_pagos)

        header_recibos = self.tabla_recibos.horizontalHeader()
        header_recibos.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        header_recibos.customContextMenuRequested.connect(partial(self.mostrar_menu_columnas, self.tabla_recibos, self.recibos_headers, self.columnas_visibles_recibos, self.config_path_recibos))
        header_recibos.sectionDoubleClicked.connect(partial(self.auto_ajustar_columna, self.tabla_recibos))
        header_recibos.setSectionsMovable(True)
        header_recibos.setSectionsClickable(True)
        self.tabla_recibos.setHorizontalHeader(header_recibos)
        self.tabla_recibos.itemSelectionChanged.connect(partial(self.mostrar_qr_item_seleccionado, self.tabla_recibos))

        self.boton_agregar_recibo.clicked.connect(self.abrir_dialogo_nuevo_recibo)

    def sync_headers(self):
        # Sincroniza los headers de las tablas con la base de datos
        if self.db_connection:
            cursor = self.db_connection.get_cursor()
            cursor.execute("SELECT TOP 0 * FROM recibos")
            headers_recibos = [column[0] for column in cursor.description]
            self.tabla_recibos.setColumnCount(len(headers_recibos))
            self.tabla_recibos.setHorizontalHeaderLabels(headers_recibos)
            self.recibos_headers = headers_recibos
            cursor.execute("SELECT TOP 0 * FROM movimientos_contables")
            headers_balance = [column[0] for column in cursor.description]
            self.tabla_balance.setColumnCount(len(headers_balance))
            self.tabla_balance.setHorizontalHeaderLabels(headers_balance)
            self.balance_headers = headers_balance
        self.pagos_headers = ["Obra", "Colocador", "Total a Pagar", "Pagado", "Pendiente", "Estado"]
        self.tabla_pagos.setColumnCount(len(self.pagos_headers))
        self.tabla_pagos.setHorizontalHeaderLabels(self.pagos_headers)

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

    def abrir_dialogo_nuevo_recibo(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Agregar nuevo recibo")
        layout = QVBoxLayout(dialog)
        form = QFormLayout()
        fecha_input = QLineEdit()
        fecha_input.setPlaceholderText("YYYY-MM-DD")
        fecha_input.setToolTip("Fecha de emisión del recibo")
        obra_combo = QComboBox()
        obras = self.obtener_obras_para_selector()
        for obra in obras:
            obra_id, nombre, cliente = obra[0], obra[1], obra[2]
            obra_combo.addItem(f"{obra_id} - {nombre} ({cliente})", obra_id)
        monto_input = QLineEdit()
        monto_input.setPlaceholderText("Monto total")
        monto_input.setToolTip("Monto total del recibo")
        concepto_input = QLineEdit()
        concepto_input.setPlaceholderText("Concepto")
        concepto_input.setToolTip("Concepto del recibo")
        destinatario_input = QLineEdit()
        destinatario_input.setPlaceholderText("Destinatario")
        destinatario_input.setToolTip("Destinatario del recibo")
        form.addRow("Fecha de Emisión:", fecha_input)
        form.addRow("Obra:", obra_combo)
        form.addRow("Monto Total:", monto_input)
        form.addRow("Concepto:", concepto_input)
        form.addRow("Destinatario:", destinatario_input)
        layout.addLayout(form)
        btns = QHBoxLayout()
        btn_agregar = QPushButton("Agregar")
        btn_cancelar = QPushButton("Cancelar")
        btns.addStretch()
        btns.addWidget(btn_agregar)
        btns.addWidget(btn_cancelar)
        layout.addLayout(btns)
        def agregar_recibo():
            datos = [
                fecha_input.text(),
                obra_combo.currentData(),
                monto_input.text(),
                concepto_input.text(),
                destinatario_input.text(),
                "pendiente"
            ]
            if not all(datos[:-1]):
                QMessageBox.warning(dialog, "Campos requeridos", "Complete todos los campos.")
                return
            if hasattr(self, 'controller'):
                self.controller.agregar_recibo(datos)
            dialog.accept()
        btn_agregar.clicked.connect(agregar_recibo)
        btn_cancelar.clicked.connect(dialog.reject)
        dialog.exec()

    def abrir_dialogo_estadistica_personalizada(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Configurar Estadística Personalizada")
        layout = QVBoxLayout(dialog)
        form = QFormLayout()
        # Selección de columnas (múltiple)
        columnas = getattr(self, 'balance_headers', ["tipo", "monto", "moneda", "obra", "fecha"])
        combo_columnas = QComboBox()
        combo_columnas.addItems(columnas)
        combo_columnas.setToolTip("Seleccionar columna principal para agrupar")
        form.addRow("Columna principal:", combo_columnas)
        # Selección de columnas secundarias (filtros)
        combo_filtros = QComboBox()
        combo_filtros.addItems([c for c in columnas if c != combo_columnas.currentText()])
        combo_filtros.setToolTip("Seleccionar columna para filtrar (opcional)")
        form.addRow("Columna filtro:", combo_filtros)
        # Selección de métrica
        combo_metrica = QComboBox()
        combo_metrica.addItems(["Suma", "Promedio", "Conteo"])
        combo_metrica.setToolTip("Seleccionar métrica a aplicar")
        form.addRow("Métrica:", combo_metrica)
        # Selección de tipo de gráfico
        combo_grafico = QComboBox()
        combo_grafico.addItems(["Barra", "Torta", "Línea"])
        combo_grafico.setToolTip("Tipo de visualización")
        form.addRow("Tipo de gráfico:", combo_grafico)
        # Nombre para guardar la estadística
        nombre_input = QLineEdit()
        nombre_input.setPlaceholderText("Nombre de la estadística personalizada")
        form.addRow("Nombre:", nombre_input)
        layout.addLayout(form)
        # Botones
        btns = QHBoxLayout()
        btn_guardar = QPushButton("Guardar y Mostrar")
        btn_cancelar = QPushButton("Cancelar")
        btns.addStretch()
        btns.addWidget(btn_guardar)
        btns.addWidget(btn_cancelar)
        layout.addLayout(btns)
        def guardar_estadistica():
            columna = combo_columnas.currentText()
            filtro = combo_filtros.currentText()
            metrica = combo_metrica.currentText()
            tipo_grafico = combo_grafico.currentText()
            nombre = nombre_input.text().strip()
            if not nombre:
                QMessageBox.warning(dialog, "Nombre requerido", "Ingrese un nombre para la estadística.")
                return
            config = {"columna": columna, "filtro": filtro, "metrica": metrica, "tipo_grafico": tipo_grafico, "nombre": nombre}
            configs = []
            config_path = "estadisticas_personalizadas.json"
            if os.path.exists(config_path):
                try:
                    with open(config_path, "r", encoding="utf-8") as f:
                        configs = json.load(f)
                except Exception:
                    pass
            configs = [c for c in configs if c.get("nombre") != nombre]
            configs.append(config)
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(configs, f, ensure_ascii=False, indent=2)
            self.cargar_estadisticas_personalizadas()
            if hasattr(self, 'controller'):
                self.controller.mostrar_estadistica_personalizada(config)
            dialog.accept()
        btn_guardar.clicked.connect(guardar_estadistica)
        btn_cancelar.clicked.connect(dialog.reject)
        dialog.exec()

    def setup_exportar_grafico_btn(self):
        if not hasattr(self, 'boton_exportar_grafico'):
            self.boton_exportar_grafico = QPushButton("Exportar gráfico")
            self.boton_exportar_grafico.setToolTip("Exportar gráfico a imagen o PDF")
            self.boton_exportar_grafico.clicked.connect(self.exportar_grafico)
            self.tab_estadisticas_layout.addWidget(self.boton_exportar_grafico)

    def exportar_grafico(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Exportar gráfico", "estadistica.png", "Imagen PNG (*.png);;Archivo PDF (*.pdf)")
        if file_path:
            fig = self.grafico_canvas.figure
            if file_path.endswith('.pdf'):
                fig.savefig(file_path, format='pdf')
            else:
                fig.savefig(file_path, format='png')

    def obtener_obras_para_selector(self):
        if self.obras_model:
            return self.obras_model.obtener_obras()
        return []

    def filtrar_tabla_balance(self, texto):
        for row in range(self.tabla_balance.rowCount()):
            visible = False
            for col in range(self.tabla_balance.columnCount()):
                item = self.tabla_balance.item(row, col)
                if item and texto.lower() in item.text().lower():
                    visible = True
                    break
            self.tabla_balance.setRowHidden(row, not visible)

    def filtrar_tabla_pagos(self, texto):
        for row in range(self.tabla_pagos.rowCount()):
            visible = False
            for col in range(self.tabla_pagos.columnCount()):
                item = self.tabla_pagos.item(row, col)
                if item and texto.lower() in item.text().lower():
                    visible = True
                    break
            self.tabla_pagos.setRowHidden(row, not visible)

    def filtrar_tabla_recibos(self, texto):
        for row in range(self.tabla_recibos.rowCount()):
            visible = False
            for col in range(self.tabla_recibos.columnCount()):
                item = self.tabla_recibos.item(row, col)
                if item and texto.lower() in item.text().lower():
                    visible = True
                    break
            self.tabla_recibos.setRowHidden(row, not visible)

    def cargar_anios_estadisticas(self, lista_fechas):
        anios = sorted({str(f[:4]) for f in lista_fechas if f})
        self.combo_anio.clear()
        self.combo_anio.addItem("Todos")
        self.combo_anio.addItems(anios)

    def actualizar_grafico_estadisticas(self):
        # Este método debe ser llamado por el controlador con los datos filtrados
        tipo = self.combo_tipo_grafico.currentText()
        anio = self.combo_anio.currentText()
        mes = self.combo_mes.currentText()
        try:
            valor_dolar = float(self.input_dolar.text().replace(",", ".")) if self.input_dolar.text() else None
        except Exception:
            valor_dolar = None
        # El controlador debe proveer los datos filtrados y llamar a la función de graficado adecuada
        if hasattr(self, 'controller'):
            self.controller.mostrar_estadisticas_balance(tipo, anio, mes, valor_dolar)

    def mostrar_estadisticas_balance(self, tipo, anio, mes, valor_dolar, datos):
        # datos: lista de dicts con claves relevantes (tipo, monto, moneda, obra, fecha, etc.)
        fig = self.grafico_canvas.figure
        fig.clear()
        ax = fig.add_subplot(111)
        if tipo == "Ingresos vs Egresos":
            total_entradas = sum(float(d['monto']) * (valor_dolar if d.get('moneda', 'ARS') == 'USD' and valor_dolar else 1)
                                 for d in datos if d['tipo'].lower() == 'entrada')
            total_salidas = sum(float(d['monto']) * (valor_dolar if d.get('moneda', 'ARS') == 'USD' and valor_dolar else 1)
                                 for d in datos if d['tipo'].lower() == 'salida')
            ax.bar(['Entradas', 'Salidas'], [total_entradas, total_salidas], color=['#22c55e', '#ef4444'])
            ax.set_title('Ingresos vs Egresos (en Pesos)')
            ax.set_ylabel('Monto (ARS)')
            self.label_resumen.setText(f"Total Entradas: ${total_entradas:,.2f}   |   Total Salidas: ${total_salidas:,.2f}   |   Saldo: ${total_entradas-total_salidas:,.2f}")
        elif tipo == "Cobros por Obra":
            obras = {}
            for d in datos:
                if d['tipo'].lower() == 'entrada':
                    obra = d.get('obra', 'Sin Obra')
                    monto = float(d['monto']) * (valor_dolar if d.get('moneda', 'ARS') == 'USD' and valor_dolar else 1)
                    obras[obra] = obras.get(obra, 0) + monto
            ax.bar(obras.keys(), obras.values(), color='#2563eb')
            ax.set_title('Cobros por Obra (en Pesos)')
            ax.set_ylabel('Monto (ARS)')
            self.label_resumen.setText(f"Cobros por obra: {len(obras)} obras")
        elif tipo == "Pagos por Obra":
            obras = {}
            for d in datos:
                if d['tipo'].lower() == 'salida':
                    obra = d.get('obra', 'Sin Obra')
                    monto = float(d['monto']) * (valor_dolar if d.get('moneda', 'ARS') == 'USD' and valor_dolar else 1)
                    obras[obra] = obras.get(obra, 0) + monto
            ax.bar(obras.keys(), obras.values(), color='#ef4444')
            ax.set_title('Pagos por Obra (en Pesos)')
            ax.set_ylabel('Monto (ARS)')
            self.label_resumen.setText(f"Pagos por obra: {len(obras)} obras")
        elif tipo == "Evolución Mensual":
            import calendar
            meses = [calendar.month_abbr[m] for m in range(1, 13)]
            entradas = [0]*12
            salidas = [0]*12
            for d in datos:
                if not d.get('fecha'): continue
                fecha = d['fecha']
                m = int(fecha[5:7]) - 1
                monto = float(d['monto']) * (valor_dolar if d.get('moneda', 'ARS') == 'USD' and valor_dolar else 1)
                if d['tipo'].lower() == 'entrada':
                    entradas[m] += monto
                elif d['tipo'].lower() == 'salida':
                    salidas[m] += monto
            ax.plot(meses, entradas, label='Entradas', color='#22c55e', marker='o')
            ax.plot(meses, salidas, label='Salidas', color='#ef4444', marker='o')
            ax.set_title('Evolución Mensual')
            ax.set_ylabel('Monto (ARS)')
            ax.legend()
            self.label_resumen.setText("Evolución mensual de ingresos y egresos")
        elif tipo == "Desglose por Moneda":
            ars = sum(float(d['monto']) for d in datos if d.get('moneda', 'ARS') == 'ARS')
            usd = sum(float(d['monto']) for d in datos if d.get('moneda', 'ARS') == 'USD')
            ax.pie([ars, usd], labels=['Pesos', 'Dólares'], autopct='%1.1f%%', colors=['#2563eb', '#fbbf24'])
            ax.set_title('Desglose por Moneda')
            self.label_resumen.setText(f"Total en Pesos: ${ars:,.2f} | Total en Dólares: U$D {usd:,.2f}")
        fig.tight_layout()
        self.grafico_canvas.draw()

    def cargar_estadisticas_personalizadas(self):
        config_path = "estadisticas_personalizadas.json"
        self.combo_estadistica_personalizada.blockSignals(True)
        self.combo_estadistica_personalizada.clear()
        self.combo_estadistica_personalizada.addItem("(Ninguna personalizada)")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    configs = json.load(f)
                for c in configs:
                    self.combo_estadistica_personalizada.addItem(c.get("nombre", "Sin nombre"), c)
            except Exception:
                pass
        self.combo_estadistica_personalizada.blockSignals(False)

    def seleccionar_estadistica_personalizada(self, idx):
        if idx == 0:
            return  # No personalizada seleccionada
        config = self.combo_estadistica_personalizada.currentData()
        if config and hasattr(self, 'controller'):
            self.controller.mostrar_estadistica_personalizada(config)

    def mostrar_grafico_personalizado(self, etiquetas, valores, config):
        '''Dibuja el gráfico personalizado según la configuración y los datos.'''
        fig = self.grafico_canvas.figure
        fig.clear()
        ax = fig.add_subplot(111)
        tipo_grafico = config.get("tipo_grafico", "Barra")
        titulo = config.get("nombre", "Estadística Personalizada")
        if not etiquetas or not valores or all(v == 0 for v in valores):
            ax.text(0.5, 0.5, "Sin datos para mostrar", ha='center', va='center', fontsize=14, color='gray', transform=ax.transAxes)
            ax.set_title(titulo)
            fig.tight_layout()
            self.grafico_canvas.draw()
            self.label_resumen.setText(f"{titulo}: Sin datos para mostrar")
            return
        if tipo_grafico == "Barra":
            ax.bar(etiquetas, valores, color="#2563eb")
        elif tipo_grafico == "Torta":
            ax.pie(valores, labels=etiquetas, autopct='%1.1f%%', colors=None)
        elif tipo_grafico == "Línea":
            ax.plot(etiquetas, valores, marker='o', color="#2563eb")
        ax.set_title(titulo)
        if tipo_grafico != "Torta":
            ax.set_ylabel(config.get("metrica", ""))
            ax.set_xlabel(config.get("columna", ""))
        self.label_resumen.setText(f"{titulo}: {config.get('metrica','')} de {config.get('columna','')}")
        fig.tight_layout()
        self.grafico_canvas.draw()

    def set_controller(self, controller):
        self.controller = controller
        self.cargar_estadisticas_personalizadas()
