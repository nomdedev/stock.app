from PyQt6.QtWidgets import QWidget, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout

class ComprasView(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.inicializar_botones()

    def inicializar_botones(self):
        self.boton_comparar_presupuestos = QPushButton("Comparar Presupuestos")
        self.layout.addWidget(self.boton_comparar_presupuestos)

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