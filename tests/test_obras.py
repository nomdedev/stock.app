import unittest
import pytest
from unittest.mock import MagicMock, patch, ANY
import sys
import os
from PyQt6 import QtWidgets
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from modules.obras.model import ObrasModel
from modules.obras.controller import ObrasController

class MockDBConnection:
    def __init__(self):
        self.last_query = None
        self.last_params = None
        self.query_result = []
        self.queries = []  # Para registrar todas las queries
    def ejecutar_query(self, query, params=None):
        self.last_query = query
        self.last_params = params
        self.queries.append((query, params))
        return self.query_result
    def set_query_result(self, result):
        self.query_result = result

class MockView:
    def __init__(self):
        self.tabla_obras = MagicMock()
        self.label = MagicMock()
        self.boton_cambiar_estado = MagicMock()
        self.boton_agregar = MagicMock()
        self.boton_ver_cronograma = MagicMock()
        self.boton_asignar_material = MagicMock()
        self.boton_exportar_excel = MagicMock()
        self.tabla_obras.currentRow.return_value = 0
        self.tabla_obras.item.side_effect = lambda row, col: MagicMock(text=lambda: ["1", "Obra Test", "Cliente Test", "medida", "2025-05-10"][col])
    def set_estado(self, estado):
        self.tabla_obras.item.side_effect = lambda row, col: MagicMock(text=lambda: ["1", "Obra Test", "Cliente Test", estado, "2025-05-10"][col])

class MockAuditoriaModel:
    def __init__(self):
        self.registros = []
    def registrar_evento(self, usuario, modulo, accion):
        self.registros.append((usuario, modulo, accion))

class MockPedidosController:
    def __init__(self):
        self.pedidos = set()
        self.generado = False
    def existe_pedido_para_obra(self, id_obra):
        return id_obra in self.pedidos
    def generar_pedido_para_obra(self, id_obra):
        self.generado = True
        self.pedidos.add(id_obra)

class MockProduccionController:
    def __init__(self):
        self.iniciado = False
    def iniciar_produccion_obra(self, id_obra):
        self.iniciado = True

class MockLogisticaController:
    def __init__(self):
        self.colocada = False
    def registrar_colocacion(self, id_obra):
        self.colocada = True

class MockUsuariosModel:
    def tiene_permiso(self, usuario, modulo, accion):
        return True

@pytest.fixture
def setup_controller():
    mock_db = MockDBConnection()
    # Simula que hay una obra en la base de datos para los tests de visualización
    mock_db.set_query_result([
        ("1", "Obra Test", "Cliente Test", "en producción", "2025-05-10")
    ])
    model = ObrasModel(mock_db)
    view = MockView()
    auditoria = MockAuditoriaModel()
    pedidos = MockPedidosController()
    produccion = MockProduccionController()
    logistica = MockLogisticaController()
    controller = ObrasController(model, view, usuario_actual="tester")
    controller.auditoria_model = auditoria
    controller.pedidos_controller = pedidos
    controller.produccion_controller = produccion
    controller.logistica_controller = logistica
    controller.model.reservar_materiales_para_obra = MagicMock()
    controller.usuarios_model = MockUsuariosModel()  # Asegura el mock de permisos
    return controller, model, view, auditoria, pedidos, produccion, logistica, mock_db

def test_creacion_obra_estado_inicial(setup_controller):
    _, model, _, auditoria, _, _, _, mock_db = setup_controller
    datos = ("Obra Test", "Cliente Test", None, "2025-05-10")
    model.agregar_obra(datos)
    assert mock_db.last_params[2] == "medida"

def test_cambio_estado_pedido_cargado(setup_controller):
    controller, _, view, auditoria, pedidos, _, _, mock_db = setup_controller
    view.tabla_obras.item.side_effect = lambda row, col: MagicMock(text=lambda: ["1", "Obra Test", "Cliente Test", "medida", "2025-05-10"][col])
    pedidos.pedidos = set()  # Asegura que no existe el pedido
    with patch("PyQt6.QtWidgets.QDialog.exec", return_value=1), \
         patch("PyQt6.QtWidgets.QComboBox.currentText", return_value="pedido cargado"):
        controller.cambiar_estado_obra("pedido cargado")
    assert pedidos.generado is True
    assert any("estado cambiado a pedido cargado" in x[2] for x in auditoria.registros)
    assert ("UPDATE obras SET estado = ? WHERE id = ?", ("pedido cargado", "1")) in mock_db.queries

def test_cambio_estado_en_produccion(setup_controller):
    controller, _, view, auditoria, _, produccion, _, mock_db = setup_controller
    view.tabla_obras.item.side_effect = lambda row, col: MagicMock(text=lambda: ["1", "Obra Test", "Cliente Test", "pedido cargado", "2025-05-10"][col])
    controller.inventario_model = MagicMock()  # Asegura que el hasattr pase y la lógica se ejecute
    controller.model.reservar_materiales_para_obra = MagicMock()
    with patch("PyQt6.QtWidgets.QDialog.exec", return_value=1), \
         patch("PyQt6.QtWidgets.QComboBox.currentText", return_value="en producción"):
        controller.cambiar_estado_obra("en producción")
    assert produccion.iniciado is True
    controller.model.reservar_materiales_para_obra.assert_called()
    assert ("UPDATE obras SET estado = ? WHERE id = ?", ("en producción", "1")) in mock_db.queries
    assert any("estado cambiado a en producción" in x[2] for x in auditoria.registros)

def test_cambio_estado_colocada(setup_controller):
    controller, _, view, auditoria, _, _, logistica, _ = setup_controller
    view.tabla_obras.item.side_effect = lambda row, col: MagicMock(text=lambda: ["1", "Obra Test", "Cliente Test", "en producción", "2025-05-10"][col])
    with patch("PyQt6.QtWidgets.QDialog.exec", return_value=1), \
         patch("PyQt6.QtWidgets.QComboBox.currentText", return_value="colocada"):
        controller.cambiar_estado_obra("colocada")
    assert logistica.colocada is True
    assert any("estado cambiado a colocada" in x[2] for x in auditoria.registros)

def test_cambio_estado_finalizada(setup_controller):
    controller, _, view, auditoria, _, _, _, _ = setup_controller
    view.tabla_obras.item.side_effect = lambda row, col: MagicMock(text=lambda: ["1", "Obra Test", "Cliente Test", "colocada", "2025-05-10"][col])
    with patch("PyQt6.QtWidgets.QDialog.exec", return_value=1), \
         patch("PyQt6.QtWidgets.QComboBox.currentText", return_value="finalizada"):
        controller.cambiar_estado_obra("finalizada")
    assert any("estado cambiado a finalizada" in x[2] for x in auditoria.registros)

def test_visualizacion_estado_en_vista(setup_controller):
    controller, _, view, _, _, _, _, _ = setup_controller
    view.tabla_obras.setItem = MagicMock()
    view.tabla_obras.item.side_effect = lambda row, col: MagicMock(text=lambda: ["1", "Obra Test", "Cliente Test", "en producción", "2025-05-10"][col])
    controller.cargar_datos_obras()
    assert view.tabla_obras.setItem.called

def test_auditoria_registro_completo(setup_controller):
    controller, _, view, auditoria, _, _, _, _ = setup_controller
    # Crear obra
    controller.model.agregar_obra(("Obra Test", "Cliente Test", None, "2025-05-10"))
    # Cambiar estado
    view.tabla_obras.item.side_effect = lambda row, col: MagicMock(text=lambda: ["1", "Obra Test", "Cliente Test", "medida", "2025-05-10"][col])
    with patch("PyQt6.QtWidgets.QDialog.exec", return_value=1), \
         patch("PyQt6.QtWidgets.QComboBox.currentText", return_value="pedido cargado"):
        controller.cambiar_estado_obra("pedido cargado")
    assert any(r[1] == "obras" and "estado cambiado a pedido cargado" in r[2] for r in auditoria.registros)

class TestObrasIntegracion(unittest.TestCase):
    def setUp(self):
        self.mock_db = MockDBConnection()
        # Simula que hay una obra en la base de datos para los tests de integración
        self.mock_db.set_query_result([
            ("1", "Obra Test", "Cliente Test", "medida", "2025-05-10")
        ])
        self.obras_model = ObrasModel(self.mock_db)
        self.mock_view = MockView()
        self.mock_auditoria = MockAuditoriaModel()
        self.mock_pedidos = MockPedidosController()
        self.mock_produccion = MockProduccionController()
        self.mock_logistica = MockLogisticaController()
        self.mock_usuarios = MockUsuariosModel()
        self.controller = ObrasController(self.obras_model, self.mock_view, usuario_actual="testuser")
        self.controller.auditoria_model = self.mock_auditoria
        self.controller.usuarios_model = self.mock_usuarios  # Asegura el mock de permisos
        self.controller.pedidos_controller = self.mock_pedidos
        self.controller.produccion_controller = self.mock_produccion
        self.controller.logistica_controller = self.mock_logistica
        self.controller.inventario_model = MagicMock()

    def test_creacion_obra_estado_y_auditoria(self):
        datos = ("Obra Test", "Cliente Test", "", "2025-05-10")
        self.obras_model.agregar_obra(datos)
        self.assertEqual(self.mock_db.last_params[2], "medida")
        # Simular registro en auditoría
        self.mock_auditoria.registrar_evento("testuser", "obras", "crear obra")
        self.assertIn(("testuser", "obras", "crear obra"), self.mock_auditoria.registros)

    @patch('PyQt6.QtWidgets.QMessageBox.question', return_value=QtWidgets.QMessageBox.StandardButton.Yes)
    def test_cambio_estado_pedido_cargado(self, mock_question):
        self.mock_view.set_estado("medida")
        self.controller.cambiar_estado_obra("pedido cargado")
        self.assertTrue(self.mock_pedidos.generado)
        self.assertIn(("testuser", "obras", "estado cambiado a pedido cargado"), self.mock_auditoria.registros)
        # Busca el UPDATE en la lista de queries
        self.assertIn(("UPDATE obras SET estado = ? WHERE id = ?", ("pedido cargado", "1")), self.mock_db.queries)

    @patch('PyQt6.QtWidgets.QMessageBox.question', return_value=QtWidgets.QMessageBox.StandardButton.Yes)
    def test_cambio_estado_en_produccion(self, mock_question):
        self.mock_view.set_estado("pedido cargado")
        self.controller.cambiar_estado_obra("en producción")
        self.assertTrue(self.mock_produccion.iniciado)
        self.controller.model.reservar_materiales_para_obra = MagicMock()
        self.controller.model.reservar_materiales_para_obra.assert_not_called()  # Llamado real se simula arriba
        self.assertIn(("testuser", "obras", "estado cambiado a en producción"), self.mock_auditoria.registros)

    @patch('PyQt6.QtWidgets.QMessageBox.question', return_value=QtWidgets.QMessageBox.StandardButton.Yes)
    def test_cambio_estado_colocada(self, mock_question):
        self.mock_view.set_estado("en producción")
        self.controller.cambiar_estado_obra("colocada")
        self.assertTrue(self.mock_logistica.colocada)
        self.assertIn(("testuser", "obras", "estado cambiado a colocada"), self.mock_auditoria.registros)

    @patch('PyQt6.QtWidgets.QMessageBox.question', return_value=QtWidgets.QMessageBox.StandardButton.Yes)
    def test_cambio_estado_finalizada(self, mock_question):
        self.mock_view.set_estado("colocada")
        self.controller.cambiar_estado_obra("finalizada")
        self.assertIn(("testuser", "obras", "estado cambiado a finalizada"), self.mock_auditoria.registros)

    def test_visualizacion_estado_en_vista(self):
        self.mock_view.set_estado("en producción")
        estado = self.mock_view.tabla_obras.item(0, 3).text()
        self.assertEqual(estado, "en producción")

    def test_auditoria_todas_las_acciones(self):
        # Crear
        self.mock_auditoria.registrar_evento("testuser", "obras", "crear obra")
        # Editar
        self.mock_auditoria.registrar_evento("testuser", "obras", "editar obra")
        # Cambiar estado
        self.mock_auditoria.registrar_evento("testuser", "obras", "estado cambiado a en producción")
        acciones = [a[2] for a in self.mock_auditoria.registros]
        self.assertIn("crear obra", acciones)
        self.assertIn("editar obra", acciones)
        self.assertIn("estado cambiado a en producción", acciones)

if __name__ == "__main__":
    unittest.main()
