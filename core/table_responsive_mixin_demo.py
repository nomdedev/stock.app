from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from core.table_responsive_mixin import TableResponsiveMixin
import sys

class DemoWindow(QMainWindow, TableResponsiveMixin):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Demo TableResponsiveMixin")
        central = QWidget()
        layout = QVBoxLayout(central)
        self.table = QTableWidget(5, 3)
        self.table.setHorizontalHeaderLabels(["Columna 1", "Columna 2", "Columna 3"])
        for i in range(5):
            for j in range(3):
                self.table.setItem(i, j, QTableWidgetItem(f"Celda {i+1},{j+1}"))
        self.make_table_responsive(self.table)
        layout.addWidget(self.table)
        self.setCentralWidget(central)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = DemoWindow()
    win.showMaximized()
    sys.exit(app.exec())
