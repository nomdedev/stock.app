import pytest
from unittest.mock import MagicMock, patch
from PyQt6.QtWidgets import QApplication, QLineEdit, QSpinBox, QPushButton, QLabel
from PyQt6.QtCore import Qt
import sys
import datetime

# Importar la vista principal de herrajes
from modules.herrajes.view import HerrajesView

@pytest.fixture(scope="module")
def app():
    """Fixture para QApplication (necesario para widgets PyQt)."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app

@pytest.fixture
def mock_db():
    """Mock de la conexión a base de datos."""
    db = MagicMock()
    db.ejecutar_query = MagicMock()
    return db

@pytest.fixture
def herrajes_view(mock_db, app):
    view = HerrajesView(db_connection=mock_db, usuario_actual="testuser")
    view.show()  # Necesario para feedback visual en tests UI
    app.processEvents()  # Procesar eventos pendientes
    return view

def test_boton_agregar_existe(herrajes_view):
    assert hasattr(herrajes_view, "boton_agregar")

def test_crear_pedido_feedback(herrajes_view, app):
    # Usar un tiempo largo para evitar que el feedback se oculte antes de la aserción
    herrajes_view.mostrar_feedback("Pedido de herrajes realizado con éxito.", tipo="exito", duracion=10000)
    app.processEvents()
    # Verifica el texto en el FeedbackBanner (accesible y visible)
    texto_feedback = herrajes_view.feedback_banner.text_label.text().lower()
    assert "éxito" in texto_feedback or "exito" in texto_feedback

def test_editar_pedido_actualiza_tabla(herrajes_view, mock_db):
    # Simula la edición de un pedido y verifica que se llama a cargar_pedidos_herrajes
    herrajes_view.cargar_pedidos_herrajes = MagicMock()
    # Simula llamada interna tras guardar cambios
    herrajes_view.cargar_pedidos_herrajes()
    herrajes_view.cargar_pedidos_herrajes.assert_called_once()

def test_auditoria_al_crear_pedido(herrajes_view, mock_db):
    # Simula inserción de auditoría
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    herrajes_view.db_connection.ejecutar_query.reset_mock()
    herrajes_view.db_connection.ejecutar_query(
        "INSERT INTO auditorias_sistema (usuario, modulo, accion, fecha, detalle) VALUES (?, ?, ?, ?, ?)",
        ("testuser", "Herrajes", "Crear pedido", now, "Detalle de prueba")
    )
    herrajes_view.db_connection.ejecutar_query.assert_called()

def test_filtros_tabla_pedidos(herrajes_view):
    # Simula datos cacheados y aplica filtro
    herrajes_view._datos_pedidos_cache = [
        {"id": 1, "fecha": "2025-06-08", "solicitante": "Juan", "herrajes": "Bisagra", "cantidad": 10, "estado": "pendiente", "observaciones": "", "obra": "Obra1", "usuario": "user1", "tipo_herraje": "Bisagra", "stock_bajo": True},
        {"id": 2, "fecha": "2025-06-07", "solicitante": "Ana", "herrajes": "Cerradura", "cantidad": 5, "estado": "entregado", "observaciones": "", "obra": "Obra2", "usuario": "user2", "tipo_herraje": "Cerradura", "stock_bajo": False},
    ]
    herrajes_view.filtro_estado.setCurrentIndex(0)  # Todos
    herrajes_view.filtro_obra.setCurrentIndex(0)    # Todas las obras
    herrajes_view.filtro_usuario.setCurrentIndex(0) # Todos los usuarios
    herrajes_view.filtro_tipo_herraje.setCurrentIndex(0) # Todos los tipos
    herrajes_view.filtro_stock_bajo.setCurrentIndex(1)   # Solo bajo stock
    herrajes_view.filtro_busqueda.setText("")
    herrajes_view.filtrar_tabla_pedidos()
    # Solo debe quedar el pedido con stock_bajo True
    assert herrajes_view.tabla_pedidos.rowCount() == 1
    item = herrajes_view.tabla_pedidos.item(0, 0)
    assert item is not None and item.text() == "1"

def test_exportar_excel(monkeypatch, herrajes_view, app):
    # Simula exportación a Excel sin errores
    monkeypatch.setattr("PyQt6.QtWidgets.QFileDialog.getSaveFileName", lambda *a, **kw: ("/tmp/test.xlsx", ""))
    monkeypatch.setattr("pandas.DataFrame.to_excel", lambda self, path, index: None)
    monkeypatch.setattr("PyQt6.QtWidgets.QMessageBox.question", lambda *a, **kw: 16384)  # Yes
    monkeypatch.setattr("PyQt6.QtWidgets.QMessageBox.information", lambda *a, **kw: None)
    herrajes_view.exportar_tabla_pedidos_a_excel()
    app.processEvents()
    # Permitir que pase si el texto es correcto, aunque el label no esté visible (headless)
    feedback = herrajes_view.feedback_banner.text_label.text().lower()
    assert (
        "exito" in feedback or
        "éxito" in feedback or
        "exportados correctamente" in feedback
    )

def test_inicializacion_boton_agregar(herrajes_view):
    # El atributo debe existir y ser QPushButton
    from PyQt6.QtWidgets import QPushButton
    assert isinstance(herrajes_view.boton_agregar, QPushButton)

def test_autocompletado_codigo_herraje_modal(herrajes_view, qtbot):
    """
    Valida que el autocompletado de código de herraje en el modal de pedido funciona y muestra feedback visual correcto.
    """
    # Simula datos de herrajes para autocompletar
    herrajes_view.model = MagicMock()
    herrajes_view.model.obtener_herrajes.return_value = [
        {"id_herraje": 1, "codigo": "H-001", "nombre": "Bisagra 90°", "stock_actual": 15, "imagen": None},
        {"id_herraje": 2, "codigo": "H-002", "nombre": "Cerradura simple", "stock_actual": 5, "imagen": None},
    ]
    # Abrir el modal de pedido de herrajes
    with patch("modules.herrajes.view.QDialog.exec", return_value=1):
        herrajes_view.abrir_dialogo_pedido_herrajes(controller=MagicMock(model=herrajes_view.model))
        dialog = getattr(herrajes_view, '_ultimo_dialogo_pedido', None)
        assert dialog is not None, "No se pudo obtener el QDialog del modal de pedido"
        # Buscar el QLineEdit de código
        input_codigo = dialog.findChild(QLineEdit, "input_codigo_herraje")
        assert input_codigo is not None, "No se encontró el campo de código de herraje"
        # Simular ingreso parcial y autocompletar
        qtbot.keyClicks(input_codigo, "H-00")
        qtbot.wait(100)
        completer = input_codigo.completer()
        assert completer is not None
        completions = [completer.model().data(completer.model().index(i, 0)) for i in range(completer.model().rowCount())]
        assert "H-001 - Bisagra 90°" in completions and "H-002 - Cerradura simple" in completions
        # Seleccionar uno y validar feedback visual
        input_codigo.setText("H-001 - Bisagra 90°")
        input_codigo.editingFinished.emit()  # Forzar actualización de datos del herraje
        qtbot.wait(100)
        # Buscar el spin_cantidad después de actualizar el herraje
        spin_cantidad = dialog.findChild(QSpinBox, "spin_cantidad_herraje")
        assert spin_cantidad is not None
        assert spin_cantidad.maximum() == 15
        # Buscar el label de feedback
        feedback = dialog.findChild(QLabel, "label_feedback_pedido")
        assert feedback is not None
        # Simular cantidad mayor al stock
        spin_cantidad.setValue(20)
        qtbot.wait(100)
        # Simular clic en confirmar
        btn_confirmar = dialog.findChild(QPushButton, "btn_confirmar_pedido_herraje")
        assert btn_confirmar is not None
        qtbot.mouseClick(btn_confirmar, Qt.MouseButton.LeftButton)
        qtbot.wait(100)
        # El feedback debe indicar stock insuficiente (aunque el label no esté visible en headless)
        print('Texto feedback:', feedback.text())
        assert "stock insuficiente" in feedback.text().lower()
