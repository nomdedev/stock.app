from PyQt6.QtWidgets import QTableWidget, QSizePolicy, QMenu, QHeaderView
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
        horizontal_header = table.horizontalHeader()
        # ATENCIÓN: En PyQt6, QHeaderView.Stretch ya no existe. Se debe usar QHeaderView.ResizeMode.Stretch
        # Esto evita errores de AttributeError: type object 'QHeaderView' has no attribute 'Stretch'
        if table.columnCount() > 0 and horizontal_header is not None:
            horizontal_header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        vertical_header = table.verticalHeader()
        if table.rowCount() > 0 and vertical_header is not None:
            vertical_header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
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
                header_item = table.horizontalHeaderItem(i)
                col_name = header_item.text() if header_item is not None else f"Columna {i+1}"
                action = QAction(col_name, menu)
                action.setCheckable(True)
                action.setChecked(not table.isColumnHidden(i))
                def toggle_col(checked, c=i):
                    table.setColumnHidden(c, not checked)
                    save_column_config()
                action.toggled.connect(toggle_col)
                menu.addAction(action)
            if header is not None:
                menu.exec(header.mapToGlobal(pos))
            else:
                menu.exec(pos)
        horizontal_header = table.horizontalHeader()
        if horizontal_header is not None:
            horizontal_header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            horizontal_header.customContextMenuRequested.connect(show_column_menu)
            # También permitir click izquierdo usando event filter
            from PyQt6.QtCore import QObject, QEvent

            class HeaderEventFilter(QObject):
                def eventFilter(self, obj, event):
                    if event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
                        pos = event.pos()
                        show_column_menu(pos)
                        return True
                    return False

            header_event_filter = HeaderEventFilter(table)
            horizontal_header.installEventFilter(header_event_filter)
        load_column_config()
