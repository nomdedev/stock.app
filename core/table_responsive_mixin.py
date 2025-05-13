from PyQt6.QtWidgets import QTableWidget, QSizePolicy
from PyQt6.QtCore import Qt

class TableResponsiveMixin:
    def make_table_responsive(self, table: QTableWidget):
        """
        Aplica políticas de expansión y estiramiento para que la tabla
        ocupe todo el espacio disponible al maximizar o poner en fullscreen.
        """
        table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        table.horizontalHeader().setSectionResizeMode(table.horizontalHeader().ResizeMode.Stretch)
        table.verticalHeader().setSectionResizeMode(table.verticalHeader().ResizeMode.Stretch)
        # Opcional: permite que la tabla crezca con el layout
        table.setMinimumHeight(200)
        table.setMinimumWidth(400)
