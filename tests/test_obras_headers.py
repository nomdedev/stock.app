import sys
import os
import pytest
from PyQt6.QtWidgets import QApplication
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from modules.obras.view import ObrasView

def test_headers_correctos():
    app = QApplication.instance() or QApplication([])
    view = ObrasView()
    headers = [view.tabla_obras.horizontalHeaderItem(i).text() if view.tabla_obras.horizontalHeaderItem(i) else '' for i in range(view.tabla_obras.columnCount())]
    assert headers == ["Nombre", "Cliente", "Fecha Medición", "Fecha Entrega"], f"Headers incorrectos: {headers}"
