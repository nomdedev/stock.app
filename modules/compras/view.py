from PyQt6.QtWidgets import QWidget, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QTabWidget, QLabel, QLineEdit, QHBoxLayout
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize
from modules.compras.pedidos.view import PedidosView  # Importar desde el módulo correcto

class ComprasView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.inicializar_botones()

        # Cargar el stylesheet visual moderno para Compras según el tema activo
        try:
            import json
            with open("themes/config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
            tema = config.get("tema", "claro")
            archivo_qss = f"styles/inventario_{tema}.qss"
            with open(archivo_qss, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"No se pudo cargar el archivo de estilos de Compras según el tema: {e}")

        # Crear QTabWidget para las pestañas
        self.tab_widget = QTabWidget()

        # Crear pestaña de Pedidos
        self.tab_pedidos = PedidosView()
        self.tab_widget.addTab(self.tab_pedidos, "Pedidos")

        # Agregar el QTabWidget al layout principal
        self.layout.addWidget(self.tab_widget)

    def inicializar_botones(self):
        # Botones principales como iconos
        botones_layout = QHBoxLayout()
        self.boton_nuevo = QPushButton()
        self.boton_nuevo.setIcon(QIcon("img/plus_icon.svg"))
        self.boton_nuevo.setIconSize(QSize(24, 24))
        self.boton_nuevo.setToolTip("Nuevo pedido")
        self.boton_nuevo.setText("")
        self.boton_nuevo.setFixedSize(48, 48)
        self.boton_nuevo.setStyleSheet("")
        self.boton_comparar = QPushButton()
        self.boton_comparar.setIcon(QIcon("img/search_icon.svg"))
        self.boton_comparar.setIconSize(QSize(24, 24))
        self.boton_comparar.setToolTip("Comparar presupuestos")
        self.boton_comparar.setText("")
        self.boton_comparar.setFixedSize(48, 48)
        self.boton_comparar.setStyleSheet("")
        self.boton_exportar_excel = QPushButton()
        self.boton_exportar_excel.setIcon(QIcon("img/excel_icon.svg"))
        self.boton_exportar_excel.setIconSize(QSize(24, 24))
        self.boton_exportar_excel.setToolTip("Exportar pedidos a Excel")
        self.boton_exportar_excel.setText("")
        self.boton_exportar_excel.setFixedSize(48, 48)
        self.boton_exportar_excel.setStyleSheet("")
        botones_layout.addWidget(self.boton_nuevo)
        botones_layout.addWidget(self.boton_comparar)
        botones_layout.addWidget(self.boton_exportar_excel)
        botones_layout.addStretch()
        self.layout.addLayout(botones_layout)

    def mostrar_comparacion_presupuestos(self, presupuestos):
        self.tabla_comparacion = QTableWidget()
        self.tabla_comparacion.setRowCount(len(presupuestos))
        self.tabla_comparacion.setColumnCount(3)
        self.tabla_comparacion.setHorizontalHeaderLabels(["Proveedor", "Precio Total", "Comentarios"])

        for row_idx, presupuesto in enumerate(presupuestos):
            self.tabla_comparacion.setItem(row_idx, 0, QTableWidgetItem(presupuesto[0]))
            self.tabla_comparacion.setItem(row_idx, 1, QTableWidgetItem(str(presupuesto[1])))
            self.tabla_comparacion.setItem(row_idx, 2, QTableWidgetItem(presupuesto[2]))

        self.layout.addWidget(self.tabla_comparacion)

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