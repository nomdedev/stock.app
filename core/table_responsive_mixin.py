from PyQt6.QtWidgets import QTableWidget, QSizePolicy, QMenu
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, QPoint
import os, json

class TableResponsiveMixin:
    def make_table_responsive(self, table: QTableWidget, persist_id=None):
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

        # Persistencia de columnas ocultas
        config_path = f".table_columns_{persist_id or table.objectName() or id(table)}.json"
        def save_column_config():
            config = {str(i): not table.isColumnHidden(i) for i in range(table.columnCount())}
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f)
        def load_column_config():
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                for i in range(table.columnCount()):
                    visible = config.get(str(i), True)
                    table.setColumnHidden(i, not visible)

        # Permitir ocultar/mostrar columnas con click izquierdo en el header
        def show_column_menu(pos):
            header = table.horizontalHeader()
            menu = QMenu(table)
            for i in range(table.columnCount()):
                col_name = table.horizontalHeaderItem(i).text() if table.horizontalHeaderItem(i) else f"Columna {i+1}"
                action = QAction(col_name, menu)
                action.setCheckable(True)
                action.setChecked(not table.isColumnHidden(i))
                def toggle_col(checked, c=i):
                    table.setColumnHidden(c, not checked)
                    save_column_config()
                action.toggled.connect(toggle_col)
                menu.addAction(action)
            menu.exec(header.mapToGlobal(pos))
        table.horizontalHeader().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        table.horizontalHeader().customContextMenuRequested.connect(show_column_menu)
        # También permitir click izquierdo
        def left_click_header(event):
            if event.button() == Qt.MouseButton.LeftButton:
                pos = event.pos()
                show_column_menu(pos)
        table.horizontalHeader().mousePressEvent = left_click_header
        load_column_config()
