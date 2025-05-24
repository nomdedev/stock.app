from PyQt6.QtWidgets import QMainWindow, QFileDialog, QTableWidget, QTableWidgetItem, QMessageBox, QLabel, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QTabWidget
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
import pandas as pd

class ConfiguracionView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Configuración del sistema")
        self.setMinimumSize(800, 600)
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(32, 32, 32, 32)
        main_layout.setSpacing(24)

        # QTabWidget principal
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("QTabWidget::pane { border-radius: 12px; background: #f1f5f9; } QTabBar::tab { min-width: 160px; min-height: 36px; font-size: 14px; font-weight: 600; border-radius: 8px; padding: 8px 24px; margin-right: 8px; } QTabBar::tab:selected { background: #e3f6fd; color: #2563eb; }")

        # --- Pestaña General ---
        self.tab_general = QWidget()
        layout_general = QVBoxLayout(self.tab_general)
        label_general = QLabel("Configuración general del sistema (próximamente)")
        label_general.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_general.addWidget(label_general)
        self.tabs.addTab(self.tab_general, "General")

        # --- Pestaña Conexión ---
        self.tab_conexion = QWidget()
        layout_conexion = QVBoxLayout(self.tab_conexion)
        label_conexion = QLabel("Configuración de conexión a base de datos (próximamente)")
        label_conexion.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_conexion.addWidget(label_conexion)
        self.tabs.addTab(self.tab_conexion, "Conexión")

        # --- Pestaña Permisos ---
        self.tab_permisos = QWidget()
        layout_permisos = QVBoxLayout(self.tab_permisos)
        label_permisos = QLabel("Gestión de permisos de usuario (próximamente)")
        label_permisos.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_permisos.addWidget(label_permisos)
        self.tabs.addTab(self.tab_permisos, "Permisos")

        # --- Pestaña Importar Inventario ---
        self.tab_importar = QWidget()
        layout_importar = QVBoxLayout(self.tab_importar)
        layout_importar.setContentsMargins(0, 0, 0, 0)
        layout_importar.setSpacing(12)
        label_titulo = QLabel("Importar Inventario desde CSV/Excel")
        label_titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #2563eb;")
        layout_importar.addWidget(label_titulo)
        file_row = QHBoxLayout()
        self.csv_file_input = QLabel("Ningún archivo seleccionado")
        self.csv_file_input.setStyleSheet("background: #e3f6fd; border-radius: 8px; padding: 8px 16px; color: #2563eb;")
        self.boton_seleccionar_csv = QPushButton()
        self.boton_seleccionar_csv.setIcon(QIcon("img/excel_icon.svg"))
        self.boton_seleccionar_csv.setToolTip("Seleccionar archivo CSV/Excel")
        self.boton_seleccionar_csv.setFixedSize(36, 36)
        self.boton_seleccionar_csv.setStyleSheet("border-radius: 8px; background: #e3f6fd;")
        file_row.addWidget(self.csv_file_input)
        file_row.addWidget(self.boton_seleccionar_csv)
        file_row.addStretch()
        layout_importar.addLayout(file_row)
        self.preview_table = QTableWidget()
        self.preview_table.setMinimumHeight(160)
        self.preview_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.preview_table.setStyleSheet("background: #fff9f3; color: #2563eb; border-radius: 8px;")
        layout_importar.addWidget(self.preview_table)
        self.mensaje_label = QLabel()
        self.mensaje_label.setWordWrap(True)
        self.mensaje_label.setStyleSheet("font-size: 13px; padding: 8px 0;")
        layout_importar.addWidget(self.mensaje_label)
        self.boton_importar_csv = QPushButton()
        self.boton_importar_csv.setIcon(QIcon("img/finish-check.svg"))
        self.boton_importar_csv.setToolTip("Importar inventario a la base de datos")
        self.boton_importar_csv.setText("")
        self.boton_importar_csv.setFixedSize(48, 48)
        self.boton_importar_csv.setEnabled(False)
        self.boton_importar_csv.setStyleSheet("border-radius: 12px; background: #d1f7e7;")
        layout_importar.addWidget(self.boton_importar_csv)
        layout_importar.addStretch()
        self.tab_importar.setLayout(layout_importar)
        self.tabs.addTab(self.tab_importar, "Importar Inventario")

        main_layout.addWidget(self.tabs)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Refuerzo de accesibilidad en botones principales
        for btn in [self.boton_seleccionar_csv, self.boton_importar_csv]:
            btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            btn.setStyleSheet(btn.styleSheet() + "\nQPushButton:focus { outline: 2px solid #2563eb; border: 2px solid #2563eb; }")
            font = btn.font()
            if font.pointSize() < 12:
                font.setPointSize(12)
            btn.setFont(font)
            if not btn.toolTip():
                btn.setToolTip("Botón de acción")
            if not btn.accessibleName():
                btn.setAccessibleName("Botón de acción de configuración")
        # Refuerzo de accesibilidad en tabla de preview
        self.preview_table.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.preview_table.setStyleSheet(self.preview_table.styleSheet() + "\nQTableWidget:focus { outline: 2px solid #2563eb; border: 2px solid #2563eb; }\nQTableWidget { font-size: 13px; }")
        self.preview_table.setToolTip("Tabla de previsualización de inventario")
        self.preview_table.setAccessibleName("Tabla de preview de configuración")
        # Refuerzo visual y robustez en header de tabla de preview
        h_header = self.preview_table.horizontalHeader() if hasattr(self.preview_table, 'horizontalHeader') else None
        if h_header is not None:
            try:
                h_header.setStyleSheet("background-color: #e3f6fd; color: #2563eb; font-weight: bold; border-radius: 8px; font-size: 13px; padding: 8px 12px; border: 1px solid #e3e3e3;")
            except Exception as e:
                # EXCEPCIÓN VISUAL: Si el header no soporta setStyleSheet, documentar aquí y en docs/estandares_visuales.md
                pass
        else:
            # EXCEPCIÓN VISUAL: No se puede aplicar refuerzo visual porque el header es None
            pass
        # Refuerzo de accesibilidad en QLabel
        for widget in self.findChildren(QLabel):
            font = widget.font()
            if font.pointSize() < 12:
                font.setPointSize(12)
            widget.setFont(font)
        # Márgenes y padding en layouts según estándar
        main_widget = self.centralWidget()
        layout = main_widget.layout() if main_widget is not None and hasattr(main_widget, 'layout') else None
        if layout is not None:
            layout.setContentsMargins(24, 20, 24, 20)
            layout.setSpacing(16)
        # EXCEPCIÓN: Este módulo no usa QLineEdit ni QComboBox en la vista principal, por lo que no aplica refuerzo en inputs ni selectores.

    def mostrar_mensaje(self, mensaje, tipo="info", destino="mensaje_label"):
        colores = {
            "exito": "#22c55e",
            "error": "#ef4444",
            "advertencia": "#f59e42",
            "info": "#2563eb"
        }
        iconos = {
            "exito": "✅",
            "error": "❌",
            "advertencia": "⚠️",
            "info": "ℹ️"
        }
        color = colores.get(tipo, "#2563eb")
        icono = iconos.get(tipo, "ℹ️")
        label = getattr(self, destino, None)
        if label:
            label.setText(f"<span style='color:{color};'>{icono} {mensaje}</span>")

    def mostrar_advertencias(self, advertencias):
        if advertencias:
            self.mostrar_mensaje("\n".join(advertencias), tipo="advertencia")

    def mostrar_errores(self, errores):
        if errores:
            self.mostrar_mensaje("\n".join(errores), tipo="error")

    def mostrar_exito(self, mensajes):
        if mensajes:
            self.mostrar_mensaje("\n".join(mensajes), tipo="exito")

    def mostrar_preview(self, dataframe):
        if dataframe is None or dataframe.empty:
            self.preview_table.clear()
            self.preview_table.setRowCount(0)
            self.preview_table.setColumnCount(0)
            self.preview_table.setHorizontalHeaderLabels([])
            return
        self.preview_table.setRowCount(min(10, len(dataframe)))
        self.preview_table.setColumnCount(len(dataframe.columns))
        self.preview_table.setHorizontalHeaderLabels([str(c) for c in dataframe.columns])
        for i in range(min(10, len(dataframe))):
            for j, col in enumerate(dataframe.columns):
                val = str(dataframe.iloc[i][col])
                self.preview_table.setItem(i, j, QTableWidgetItem(val))
        self.preview_table.resizeColumnsToContents()

    def confirmar_importacion(self, total_filas):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setWindowTitle("Confirmar importación")
        msg.setText(f"¿Deseas importar {total_filas} filas a la base de datos? Se realizará backup antes de modificar.")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        return msg.exec() == QMessageBox.StandardButton.Yes

    def seleccionar_archivo_csv(self):
        file, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo de inventario", "inventario", "Archivos CSV (*.csv);;Archivos Excel (*.xlsx *.xls)")
        if file:
            self.csv_file_input.setText(file)
            try:
                if file.endswith('.csv'):
                    df = pd.read_csv(file, sep=';', encoding='utf-8')
                else:
                    df = pd.read_excel(file)
            except Exception:
                df = None
            self.mostrar_preview(df)
            self.boton_importar_csv.setEnabled(df is not None and not df.empty)
        else:
            self.csv_file_input.setText("Ningún archivo seleccionado")
            self.mostrar_preview(None)
            self.boton_importar_csv.setEnabled(False)

    def conectar_eventos_importacion(self, controller):
        self.boton_seleccionar_csv.clicked.connect(self.seleccionar_archivo_csv)
        self.boton_importar_csv.clicked.connect(controller.importar_csv_inventario)