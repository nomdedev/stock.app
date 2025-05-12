import unittest
import sys
import os
import pytest
from unittest.mock import Mock
from modules.inventario.controller import InventarioController
from modules.inventario.model import InventarioModel
from modules.inventario.view import InventarioView

# Agregar el directorio raíz del proyecto al PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

class MockDB:
    def ejecutar_query(self, query, params=None):
        if "SELECT * FROM inventario_perfiles" in query:
            return [
                (1, "123456.789", "Material A", "PVC", "unidad", 100, 10, "Almacén 1", "Descripción A", "QR123", "imagen_a.jpg"),
                (2, "987654.321", "Material B", "Aluminio", "kg", 50, 5, "Almacén 2", "Descripción B", "QR987", "imagen_b.jpg")
            ]
        return []

class TestInventarioModel(unittest.TestCase):

    def setUp(self):
        self.mock_db = Mock()
        self.inventario_model = InventarioModel(self.mock_db)

    def test_generar_qr(self):
        # Simular generación de QR
        id_item = 1
        self.mock_db.ejecutar_query.side_effect = [
            [("123456.789",)],  # Resultado de la primera consulta (SELECT)
            None  # Resultado de la segunda consulta (UPDATE)
        ]

        qr_code = self.inventario_model.generar_qr(id_item)

        # Verificar que ambas consultas se realizaron correctamente
        self.mock_db.ejecutar_query.assert_any_call("SELECT codigo FROM inventario_perfiles WHERE id = ?", (id_item,))
        self.mock_db.ejecutar_query.assert_any_call("UPDATE inventario_perfiles SET qr_code = ? WHERE id = ?", ("QR-123456.789", id_item))
        self.assertEqual(qr_code, "QR-123456.789")

    def test_exportar_inventario_excel(self):
        # Simular exportación a Excel
        self.mock_db.ejecutar_query.return_value = [
            (1, "123456.789", "Material A", "PVC", "unidad", 100, 10, "Almacén 1", "Descripción A", "QR123", "imagen_a.jpg"),
            (2, "987654.321", "Material B", "Aluminio", "kg", 50, 5, "Almacén 2", "Descripción B", "QR987", "imagen_b.jpg")
        ]

        resultado = self.inventario_model.exportar_inventario("excel")

        self.assertEqual(resultado, "Inventario exportado a Excel.")

    def test_exportar_inventario_pdf(self):
        # Simular exportación a PDF
        self.mock_db.ejecutar_query.return_value = [
            (1, "123456.789", "Material A", "PVC", "unidad", 100, 10, "Almacén 1", "Descripción A", "QR123", "imagen_a.jpg"),
            (2, "987654.321", "Material B", "Aluminio", "kg", 50, 5, "Almacén 2", "Descripción B", "QR987", "imagen_b.jpg")
        ]

        resultado = self.inventario_model.exportar_inventario("pdf")

        self.assertEqual(resultado, "Inventario exportado a PDF.")

    def test_actualizar_inventario(self):
        mock_model = Mock()
        mock_view = Mock()
        controller = InventarioController(mock_model, mock_view)

        mock_model.obtener_items_por_lotes.return_value = [
            (1, "12345", "Material A", "PVC", "unidad", 10, 5, "Almacén 1", "Descripción A", "QR123", "imagen_a.jpg")
        ]
        mock_view.tabla_inventario.rowCount.return_value = 1
        mock_view.tabla_inventario.columnCount.return_value = 12

        controller.actualizar_inventario()

        mock_model.obtener_items_por_lotes.assert_called_once_with(0, 500)
        mock_view.tabla_inventario.setRowCount.assert_called_with(1)
        mock_view.tabla_inventario.setItem.assert_called()
        mock_view.label.setText.assert_not_called()  # No debe haber errores

    def test_agregar_item(self):
        mock_model = Mock()
        mock_view = Mock()
        controller = InventarioController(mock_model, mock_view)

        mock_view.obtener_datos_nuevo_item.return_value = {
            "codigo": "12345",
            "nombre": "Material A",
            "tipo_material": "PVC",
            "unidad": "unidad",
            "stock_actual": 10,
            "stock_minimo": 5,
            "ubicacion": "Almacén 1",
            "descripcion": "Descripción del material"
        }
        mock_model.obtener_item_por_codigo.return_value = None

        controller.agregar_item()

        mock_model.agregar_item.assert_called_once()
        mock_view.label.setText.assert_called_with("Ítem agregado exitosamente.")

    def test_ver_movimientos(self):
        mock_model = Mock()
        mock_view = Mock()
        controller = InventarioController(mock_model, mock_view)

        mock_view.obtener_id_item_seleccionado.return_value = 1
        mock_model.obtener_movimientos.return_value = [("Movimiento 1",), ("Movimiento 2",)]

        controller.ver_movimientos()

        mock_model.obtener_movimientos.assert_called_once_with(1)
        mock_view.mostrar_movimientos.assert_called_once_with([("Movimiento 1",), ("Movimiento 2",)])

    def test_reservar_item(self):
        mock_model = Mock()
        mock_view = Mock()
        controller = InventarioController(mock_model, mock_view)

        mock_view.obtener_datos_reserva.return_value = {
            "id_item": 1,
            "cantidad_reservada": 5,
            "referencia_obra": 101,
            "estado": "activa"
        }

        controller.reservar_item()

        mock_model.registrar_reserva.assert_called_once()
        mock_view.label.setText.assert_called_with("Reserva registrada exitosamente.")

    def test_actualizar_tabla_despues_de_reserva(self):
        mock_model = Mock()
        mock_view = Mock()
        controller = InventarioController(mock_model, mock_view)

        # Simular datos de inventario después de una reserva
        mock_model.obtener_items_por_lotes.return_value = [
            (1, "12345", "Material A", "PVC", "unidad", 10, 5, "Almacén 1", "Descripción A", "QR123", "imagen_a.jpg")
        ]

        controller.reservar_item()

        # Verificar que la tabla se actualizó
        mock_view.tabla_inventario.setRowCount.assert_called()
        mock_view.tabla_inventario.setItem.assert_called()

def test_exportar_inventario():
    db = MockDB()
    model = InventarioModel(db)

    # Caso 1: Exportar a Excel
    resultado_excel = model.exportar_inventario("excel")
    assert resultado_excel == "Inventario exportado a Excel.", f"Error: {resultado_excel}"
    assert os.path.exists("inventario.xlsx"), "El archivo Excel no fue generado."
    os.remove("inventario.xlsx")

    # Caso 2: Exportar a PDF
    resultado_pdf = model.exportar_inventario("pdf")
    assert resultado_pdf == "Inventario exportado a PDF.", f"Error: {resultado_pdf}"
    assert os.path.exists("inventario.pdf"), "El archivo PDF no fue generado."
    os.remove("inventario.pdf")

    # Caso 3: Formato no soportado
    resultado_invalido = model.exportar_inventario("csv")
    assert resultado_invalido == "Formato no soportado.", f"Error: {resultado_invalido}"

@pytest.fixture
def setup_controller():
    mock_model = Mock(spec=InventarioModel)
    mock_view = Mock(spec=InventarioView)
    controller = InventarioController(mock_model, mock_view)
    return controller

def test_boton_nuevo_item_llama_al_formulario(mocker, setup_controller):
    controller = setup_controller
    mock_method = mocker.patch.object(controller, "abrir_formulario_nuevo")
    controller.view.boton_nuevo_item.click()
    mock_method.assert_called_once()

def test_exportar_excel(mocker, setup_controller):
    controller = setup_controller
    mock_export = mocker.patch.object(controller, "exportar_excel")
    controller.view.boton_exportar_excel.click()
    mock_export.assert_called_once()

def test_exportar_pdf(mocker, setup_controller):
    controller = setup_controller
    mock_export = mocker.patch.object(controller, "exportar_pdf")
    controller.view.boton_exportar_pdf.click()
    mock_export.assert_called_once()

def test_ver_movimientos_abre_historial(mocker, setup_controller):
    controller = setup_controller
    mock_historial = mocker.patch.object(controller, "mostrar_historial")
    controller.view.boton_ver_movimientos.click()
    mock_historial.assert_called_once()

def test_reservar_item(mocker, setup_controller):
    controller = setup_controller
    mock_reserva = mocker.patch.object(controller, "reservar_item")
    controller.view.boton_reservar.click()
    mock_reserva.assert_called_once()

def test_buscar_item_activa_filtro(mocker, setup_controller):
    controller = setup_controller
    mock_filtro = mocker.patch.object(controller, "filtrar_resultados")
    controller.view.boton_buscar.click()
    mock_filtro.assert_called_once()

def test_generar_qr(mocker, setup_controller):
    controller = setup_controller
    mock_qr = mocker.patch.object(controller, "generar_codigo_qr")
    controller.view.boton_generar_qr.click()
    mock_qr.assert_called_once()

def test_actualizar_inventario(mocker, setup_controller):
    controller = setup_controller
    mock_actualizar = mocker.patch.object(controller, "cargar_datos_inventario")
    controller.view.boton_actualizar.click()
    mock_actualizar.assert_called_once()

def test_ajustar_stock_abre_dialogo(mocker, setup_controller):
    controller = setup_controller
    mock_ajuste = mocker.patch.object(controller, "abrir_ajustar_stock")
    controller.view.boton_ajustar_stock.click()
    mock_ajuste.assert_called_once()

def test_actualizar_tabla_despues_de_reserva(mocker, setup_controller):
    controller = setup_controller
    mock_actualizar = mocker.patch.object(controller, "actualizar_inventario")

    controller.reservar_item()

    mock_actualizar.assert_called_once()

if __name__ == "__main__":
    try:
        test_exportar_inventario()
        print("Pruebas del módulo de inventario pasaron correctamente.")
    except AssertionError as e:
        print(f"Test fallido: {e}")
    unittest.main()
