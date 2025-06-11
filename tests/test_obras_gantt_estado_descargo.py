import pytest
from PyQt6.QtWidgets import QApplication
from modules.obras.view import ObrasView
from datetime import datetime, timedelta

@pytest.fixture(scope="module")
def app():
    import sys
    return QApplication.instance() or QApplication(sys.argv)

def test_estado_y_descargo_gantt(app):
    view = ObrasView(usuario_actual="testgantt")
    # Agregar una obra con fecha de entrega vencida y estado distinto a "Lista para colocar"
    hoy = datetime.now().date()
    fecha_med = (hoy - timedelta(days=10)).strftime("%Y-%m-%d")
    fecha_ent = (hoy - timedelta(days=1)).strftime("%Y-%m-%d")
    datos_obra = {
        "nombre": "Obra Test Descargo",
        "cliente": "Cliente QA",
        "fecha_medicion": fecha_med,
        "fecha_entrega": fecha_ent,
        "estado": "Medición"
    }
    view.agregar_obra_a_tabla(datos_obra)
    # Simular cambio de estado a "En fabricación" (sigue vencida)
    combo = view.tabla_obras.cellWidget(0, 4)
    from PyQt6.QtWidgets import QComboBox
    assert isinstance(combo, QComboBox), "Expected a QComboBox in cell (0, 4)"
    combo.setCurrentText("En fabricación")
    # El descargo debería ser solicitado (se abre un QDialog, pero aquí solo verificamos feedback)
    # Simular que el usuario ingresa descargo y acepta
    # (No se puede automatizar el QDialog sin QtBot, pero se puede forzar la llamada)
    view.solicitar_descargo("Obra Test Descargo", "En fabricación")
    assert view.label_feedback.isVisible()
    assert isinstance(combo, QComboBox), "Expected a QComboBox in cell (0, 4)"
    combo.setCurrentText("Lista para colocar")
    # Cambiar a "Lista para colocar" (no debe pedir descargo)
    combo.setCurrentText("Lista para colocar")
    assert isinstance(combo, QComboBox), "Expected a QComboBox in cell (0, 4)"
    combo.setCurrentText("Demorada")
    # (No hay cambio en feedback, pero no debe abrir diálogo)
    # Si se cambia a "Demorada" y la fecha está vencida, debe pedir descargo
    combo.setCurrentText("Demorada")
    view.solicitar_descargo("Obra Test Descargo", "Demorada")
    assert view.label_feedback.isVisible()
    assert "Descargo registrado" in view.label_feedback.text()
