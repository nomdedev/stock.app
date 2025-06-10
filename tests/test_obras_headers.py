# ---
# [10/06/2025] Estrategia de tests para headers de Obras (UI)
#
# Este test verifica los headers de la tabla de obras en la UI.
# Es un test de UI, por lo que requiere PyQt y la vista real, pero NO depende de la base de datos ni de configuración de entorno.
# Si en el futuro se requiere testear integración real, hacerlo en un archivo aparte y documentar la dependencia.
#
# Última ejecución: 10/06/2025. Test PASSED si los headers coinciden con el estándar.
# ---

import sys
import os
import pytest
from PyQt6.QtWidgets import QApplication
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from modules.obras.view import ObrasView

def test_headers_correctos():
    app = QApplication.instance() or QApplication([])
    view = ObrasView()
    headers = []
    for i in range(view.tabla_obras.columnCount()):
        item = view.tabla_obras.horizontalHeaderItem(i)
        headers.append(item.text() if item is not None else '')
    # Actualizado según la estructura real de la tabla de obras
    headers_esperados = [
        "Nombre", "Cliente", "Fecha Medición", "Fecha Entrega",
        "Estado Materiales", "Estado Vidrios", "Estado Herrajes"
    ]
    assert headers == headers_esperados, f"Headers incorrectos: {headers}"
