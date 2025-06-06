import pytest
from PyQt6.QtWidgets import QApplication, QMessageBox, QDialog, QLineEdit, QPushButton
from PyQt6.QtCore import Qt
from modules.obras.view import ObrasView
from modules.obras.produccion.view import ProduccionView
from modules.obras.controller import ObrasController as _ObrasController

class DummyModel:
    def obtener_headers_obras(self):
        return ["id", "nombre", "cliente", "estado", "fecha", "fecha_entrega"]
    def obtener_datos_obras(self):
        return [(1, "Obra Test", "Cliente Test", "nuevo", "2025-06-01", "2025-06-10")]
    def obtener_todas_las_fechas(self):
        return []
    def agregar_obra(self, datos):
        return 1  # Simula alta exitosa
    def obtener_obra_por_nombre_cliente(self, nombre, cliente):
        return (1, nombre, cliente, "nuevo", "2025-06-01", "2025-06-10")  # Simula que existe

class DummyUsuariosModel:
    def tiene_permiso(self, usuario, modulo, accion):
        return True

class DummyAuditoriaModel:
    def registrar_evento(self, *args, **kwargs):
        pass
class DummyDBConnection:
    def ejecutar_query(self, *args, **kwargs):
        return []

@pytest.fixture(scope="module")
def app():
    import sys
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    yield app

class PatchedObrasController(_ObrasController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.auditoria_model = DummyAuditoriaModel()
    def agregar_obra_dialog(self, *args, **kwargs):
        return super().agregar_obra_dialog()

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
    # Parchear SOLO en la ruta absoluta del módulo
    monkeypatch.setattr("modules.obras.view.QMessageBox.information", fake_information)
    button = getattr(view, button_attr)
    qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
    dialogs = [w for w in QApplication.topLevelWidgets() if isinstance(w, QDialog) and w.isVisible()]
    for dialog in dialogs:
        nombre = dialog.findChild(QLineEdit, "nombre_input_obra")
        cliente = dialog.findChild(QLineEdit, "cliente_input_obra")
        if nombre:
            nombre.setText("Obra Test")
        if cliente:
            cliente.setText("Cliente Test")
        btn_guardar = None
        for btn in dialog.findChildren(QPushButton):
            if btn.text().lower() in ("guardar", "verificar"):
                btn_guardar = btn
                break
        if btn_guardar:
            qtbot.mouseClick(btn_guardar, Qt.MouseButton.LeftButton)
        else:
            dialog.accept()
    qtbot.waitUntil(lambda: "title" in called, timeout=2000)
    assert "title" in called, f"No se llamó a QMessageBox.information para el botón {button_attr}. called={called}"
    assert called["title"] == expected_title

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
    # Parchear SOLO en la ruta absoluta del módulo
    monkeypatch.setattr("modules.obras.produccion.view.QMessageBox.information", fake_information)
    button = getattr(view, button_attr)
    qtbot.mouseClick(button, Qt.MouseButton.LeftButton)
    qtbot.waitUntil(lambda: "title" in called, timeout=2000)
    assert "title" in called, f"No se llamó a QMessageBox.information para el botón {button_attr}. called={called}"
    assert called["title"] == expected_title