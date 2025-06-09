from PyQt6.QtWidgets import QTableWidget, QSizePolicy, QMenu, QHeaderView
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, QPoint
import os, json

class TableResponsiveMixin:
    def make_table_responsive(self, table: QTableWidget, persist_id=None):
        """
        Aplica políticas de expansión y estiramiento para que la tabla
        ocupe todo el espacio disponible al maximizar o poner en fullscreen.
        Todas las tablas quedan en modo Interactive (el usuario puede ajustar el ancho de columnas manualmente).
        Además, refuerza el estilo y visibilidad de los encabezados.
        """
        table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        horizontal_header = table.horizontalHeader()
        if horizontal_header is not None:
            horizontal_header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
            horizontal_header.setMinimumSectionSize(80)
            horizontal_header.setDefaultSectionSize(120)
            # No usar setStyleSheet aquí. El estilo visual de headers se gestiona por QSS de theme global.
            horizontal_header.setVisible(True)
            for i in range(table.columnCount()):
                horizontal_header.setSectionHidden(i, False)
        v_header = table.verticalHeader()
        if v_header is not None:
            try:
                v_header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            except Exception:
                pass
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
        def show_column_menu(pos):
            header = table.horizontalHeader()
            if header is None:
                return
            menu = QMenu(table)
            for i in range(table.columnCount()):
                item = table.horizontalHeaderItem(i)
                col_name = item.text() if item and hasattr(item, 'text') else f"Columna {i+1}"
                action = QAction(col_name, menu)
                action.setCheckable(True)
                action.setChecked(not table.isColumnHidden(i))
                def toggle_column(checked, idx=i):
                    table.setColumnHidden(idx, not checked)
                    save_column_config()
                action.toggled.connect(toggle_column)
                menu.addAction(action)
            if hasattr(header, 'mapToGlobal'):
                menu.exec(header.mapToGlobal(pos))
            else:
                menu.exec(pos)
        if horizontal_header is not None:
            horizontal_header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            horizontal_header.customContextMenuRequested.connect(show_column_menu)
        load_column_config()
