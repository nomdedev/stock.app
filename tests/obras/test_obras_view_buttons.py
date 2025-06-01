import pytest
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from modules.obras.view import ObrasView
from modules.obras.produccion.view import ProduccionView

@pytest.fixture(scope="module")
def app():
    import sys
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    yield app

@pytest.mark.parametrize("button_attr, expected_title", [
    ("boton_agregar", "Agregar Obra"),
    ("boton_verificar_obra", "Verificar Obra"),
])
def test_obrasview_buttons_show_messagebox(app, button_attr, expected_title, qtbot, monkeypatch):
    view = ObrasView()
    called = {}
    def fake_information(parent, title, text):
        called["title"] = title
        called["text"] = text
        return QMessageBox.StandardButton.Ok
    monkeypatch.setattr(QMessageBox, "information", fake_information)
    button = getattr(view, button_attr)
    qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
    assert called["title"] == expected_title
    assert "ejecutada" in called["text"]

@pytest.mark.parametrize("button_attr, expected_title", [
    ("boton_agregar", "Agregar Producción"),
    ("boton_ver_detalles", "Ver Detalles"),
    ("boton_finalizar_etapa", "Finalizar Etapa"),
])
def test_produccionview_buttons_show_messagebox(app, button_attr, expected_title, qtbot, monkeypatch):
    view = ProduccionView()
    called = {}
    def fake_information(parent, title, text):
        called["title"] = title
        called["text"] = text
        return QMessageBox.StandardButton.Ok
    monkeypatch.setattr(QMessageBox, "information", fake_information)
    button = getattr(view, button_attr)
    qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
    assert called["title"] == expected_title
    assert "ejecutada" in called["text"]
