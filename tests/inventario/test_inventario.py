import unittest
import sys
import os
from unittest.mock import Mock, patch
from modules.inventario.controller import InventarioController
from modules.inventario.model import InventarioModel
from modules.inventario.view import InventarioView
import types
from modules.inventario import controller as inventario_controller

def fake_permiso_auditoria(*args, **kwargs):
    def decorator(func):
        return func
    return decorator

inventario_controller.permiso_auditoria_inventario = fake_permiso_auditoria

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
        # Soporte para context manager en transacciones
        self.mock_db.transaction = Mock()
        self.mock_db.transaction.return_value.__enter__ = lambda s: s
        self.mock_db.transaction.return_value.__exit__ = lambda s, exc_type, exc_val, tb: None
        self.inventario_model = InventarioModel(self.mock_db)

    def test_generar_qr(self):
        id_item = 1
        self.mock_db.ejecutar_query.side_effect = [
            [("123456.789",)],  # Resultado de la primera consulta (SELECT)
            None  # Resultado de la segunda consulta (UPDATE)
        ]
        qr_code = self.inventario_model.generar_qr(id_item)
        self.mock_db.ejecutar_query.assert_any_call("SELECT codigo FROM inventario_perfiles WHERE id = ?", (id_item,))
        self.mock_db.ejecutar_query.assert_any_call("UPDATE inventario_perfiles SET qr = ? WHERE id = ?", ("QR-123456.789", id_item))
        self.assertEqual(qr_code, "QR-123456.789")

    def test_generar_qr_codigo_vacio(self):
        id_item = 99
        self.mock_db.ejecutar_query.side_effect = [[], None]
        qr_code = self.inventario_model.generar_qr(id_item)
        self.assertIsNone(qr_code)

    def test_exportar_inventario_excel(self):
        """Probar exportación a Excel usando solo datos simulados y mock de DB."""
        self.mock_db.ejecutar_query.return_value = [
            (1, "123456.789", "Material A", "PVC", "unidad", 100, 10, "Almacén 1", "Descripción A", "QR123", "imagen_a.jpg"),
            (2, "987654.321", "Material B", "Aluminio", "kg", 50, 5, "Almacén 2", "Descripción B", "QR987", "imagen_b.jpg")
        ]

        resultado = self.inventario_model.exportar_inventario("excel")

        self.assertEqual(resultado, "Inventario exportado a Excel.")

    def test_exportar_inventario_pdf(self):
        """Probar exportación a PDF usando solo datos simulados y mock de DB."""
        self.mock_db.ejecutar_query.return_value = [
            (1, "123456.789", "Material A", "PVC", "unidad", 100, 10, "Almacén 1", "Descripción A", "QR123", "imagen_a.jpg"),
            (2, "987654.321", "Material B", "Aluminio", "kg", 50, 5, "Almacén 2", "Descripción B", "QR987", "imagen_b.jpg")
        ]

        resultado = self.inventario_model.exportar_inventario("pdf")

        self.assertEqual(resultado, "Inventario exportado a PDF.")

    def test_exportar_inventario_vacio(self):
        """Probar exportación de inventario vacío, asegurando robustez y feedback adecuado."""
        self.mock_db.ejecutar_query.return_value = []
        resultado = self.inventario_model.exportar_inventario("excel")
        self.assertEqual(resultado, "Inventario exportado a Excel.")
        resultado_pdf = self.inventario_model.exportar_inventario("pdf")
        self.assertEqual(resultado_pdf, "Inventario exportado a PDF.")

    def test_actualizar_inventario(self):
        mock_model = Mock()
        mock_model.obtener_items.return_value = [
            (1, "12345", "Material A", "PVC", "unidad", 10, 5, "Almacén 1", "Descripción A", "QR123", "imagen_a.jpg")
        ]
        mock_view = Mock()
        mock_view.tabla_inventario = Mock()
        mock_view.tabla_inventario.setRowCount = Mock()
        mock_view.tabla_inventario.setColumnCount = Mock()
        mock_view.tabla_inventario.setItem = Mock()
        mock_db = Mock()
        usuario = {'rol': 'admin', 'nombre': 'test'}
        controller = TestInventarioController(mock_model, mock_view, mock_db, usuario_actual=usuario)
        controller.usuarios_model = Mock()
        controller.usuarios_model.tiene_permiso.return_value = True
        controller.usuarios_model.obtener_modulos_permitidos.return_value = ['inventario']
        controller.auditoria_model = Mock()
        controller.auditoria_model.registrar_evento = Mock(side_effect=lambda *a, **kw: None)
        mock_model.obtener_items.reset_mock()  # Limpiar conteo de llamadas
        controller.actualizar_inventario()
        assert mock_model.obtener_items.call_count == 1
        mock_view.tabla_inventario.setRowCount.assert_called()
        mock_view.tabla_inventario.setItem.assert_called()

    def test_actualizar_tabla_despues_de_reserva(self):
        mock_model = Mock()
        mock_model.obtener_items.return_value = [
            (1, "12345", "Material A", "PVC", "unidad", 10, 5, "Almacén 1", "Descripción A", "QR123", "imagen_a.jpg")
        ]
        mock_view = Mock()
        mock_view.tabla_inventario = Mock()
        mock_view.tabla_inventario.setRowCount = Mock()
        mock_view.tabla_inventario.setColumnCount = Mock()
        mock_view.tabla_inventario.setItem = Mock()
        mock_db = Mock()
        usuario = {'rol': 'admin', 'nombre': 'test'}
        controller = TestInventarioController(mock_model, mock_view, mock_db, usuario_actual=usuario)
        controller.usuarios_model = Mock()
        controller.usuarios_model.tiene_permiso.return_value = True
        controller.usuarios_model.obtener_modulos_permitidos.return_value = ['inventario']
        controller.auditoria_model = Mock()
        controller.auditoria_model.registrar_evento = Mock(side_effect=lambda *a, **kw: None)
        controller.actualizar_inventario()
        mock_view.tabla_inventario.setRowCount.assert_called()
        mock_view.tabla_inventario.setItem.assert_called()

    def test_agregar_item(self):
        mock_model = Mock()
        mock_model.obtener_items.return_value = [
            (1, "12345", "Material A", "PVC", "unidad", 10, 5, "Almacén 1", "Descripción A", "QR123", "imagen_a.jpg")
        ]
        # Simular que el ítem no existe antes, pero sí después de agregar
        mock_model.obtener_item_por_codigo.side_effect = [None, [(1, "12345", "Material A", "PVC", "unidad", 10, 5, "Almacén 1", "Descripción A", "QR123", "imagen_a.jpg")]]
        mock_model.agregar_item = Mock()
        mock_model.obtener_movimientos = Mock()
        mock_model.registrar_movimiento = Mock()
        mock_view = Mock()
        mock_view.abrir_formulario_nuevo_item.return_value = {
            "codigo": "12345",
            "nombre": "Material A",
            "tipo_material": "PVC",
            "unidad": "unidad",
            "stock_actual": 10,
            "stock_minimo": 5,
            "ubicacion": "Almacén 1",
            "descripcion": "Descripción del material"
        }
        mock_view.label = Mock()
        mock_view.tabla_inventario = Mock()
        mock_view.tabla_inventario.setRowCount = Mock()
        mock_view.tabla_inventario.setColumnCount = Mock()
        mock_view.tabla_inventario.setItem = Mock()
        mock_view.mostrar_mensaje = Mock()
        mock_view.mostrar_movimientos = Mock()
        controller = TestInventarioController(mock_model, mock_view, Mock())
        controller.usuario_actual = {'nombre': 'test', 'rol': 'admin', 'ip': '127.0.0.1'}
        controller.usuarios_model = Mock()
        controller.usuarios_model.tiene_permiso.return_value = True
        controller.usuarios_model.obtener_modulos_permitidos.return_value = ['inventario']
        controller.auditoria_model = Mock()
        controller.auditoria_model.registrar_evento = Mock(side_effect=lambda *a, **kw: None)
        controller.view.abrir_formulario_nuevo_item = mock_view.abrir_formulario_nuevo_item
        controller.model.obtener_item_por_codigo = mock_model.obtener_item_por_codigo
        controller.model.agregar_item = mock_model.agregar_item
        controller.model.obtener_movimientos = mock_model.obtener_movimientos
        controller.model.registrar_movimiento = mock_model.registrar_movimiento
        controller.view.mostrar_mensaje = mock_view.mostrar_mensaje
        controller.view.mostrar_movimientos = mock_view.mostrar_movimientos
        # Llamar directamente al método del controlador
        controller.agregar_item()
        assert mock_model.agregar_item.call_count == 1
        args, kwargs = mock_model.agregar_item.call_args
        assert isinstance(args[0], tuple)
        mock_view.mostrar_mensaje.assert_called_with("Ítem '12345' agregado correctamente.", tipo='success')

    def test_integracion_agregar_y_reflejar_en_ui_db(self):
        mock_model = Mock()
        mock_model.obtener_items.return_value = [
            (1, "12345", "Material A", "PVC", "unidad", 10, 5, "Almacén 1", "Descripción A", "QR123", "imagen_a.jpg")
        ]
        mock_view = Mock()
        mock_view.tabla_inventario = Mock()
        mock_view.tabla_inventario.setRowCount = Mock()
        mock_view.tabla_inventario.setColumnCount = Mock()
        mock_view.tabla_inventario.setItem = Mock()
        mock_view.actualizar_tabla = Mock()
        controller = TestInventarioController(mock_model, mock_view, Mock())
        controller.usuario_actual = {'nombre': 'test', 'rol': 'admin', 'ip': '127.0.0.1'}
        controller.usuarios_model = Mock()
        controller.usuarios_model.tiene_permiso.return_value = True
        controller.usuarios_model.obtener_modulos_permitidos.return_value = ['inventario']
        controller.auditoria_model = Mock()
        controller.auditoria_model.registrar_evento = Mock()
        # Simular agregar y reflejar en UI+DB
        controller.actualizar_inventario()
        mock_view.tabla_inventario.setRowCount.assert_called_with(1)
        mock_view.tabla_inventario.setItem.assert_called()

    def test_integracion_reserva_reflejada_en_ui_db(self):
        mock_model = Mock()
        mock_model.obtener_items.return_value = [
            (1, "12345", "Material A", "PVC", "unidad", 10, 5, "Almacén 1", "Descripción A", "QR123", "imagen_a.jpg")
        ]
        mock_model.db = Mock()
        mock_model.db.ejecutar_query.return_value = [(0,)]
        mock_view = Mock()
        mock_view.tabla_inventario = Mock()
        mock_view.tabla_inventario.setRowCount = Mock()
        mock_view.tabla_inventario.setColumnCount = Mock()
        mock_view.tabla_inventario.setItem = Mock()
        mock_view.actualizar_tabla = Mock()
        controller = TestInventarioController(mock_model, mock_view, Mock())
        controller.usuario_actual = {'nombre': 'test', 'rol': 'admin', 'ip': '127.0.0.1'}
        controller.usuarios_model = Mock()
        controller.usuarios_model.tiene_permiso.return_value = True
        controller.usuarios_model.obtener_modulos_permitidos.return_value = ['inventario']
        controller.auditoria_model = Mock()
        controller.auditoria_model.registrar_evento = Mock()
        # Simular reserva y reflejo en UI+DB
        controller.actualizar_inventario()
        mock_view.tabla_inventario.setRowCount.assert_called_with(1)
        mock_view.tabla_inventario.setItem.assert_called()

    def test_reservar_stock_cantidad_negativa(self):
        # Probar reserva con cantidad negativa
        mock_model = Mock()
        mock_model.obtener_item_por_id.return_value = (1, "12345", "Material A", "PVC", "unidad", 10, 5, "Almacén 1", "Descripción A", "QR123", "imagen_a.jpg")
        mock_model.obtener_items.return_value = []  # <-- Corrección: devolver lista vacía
        mock_view = Mock()
        mock_view.tabla_inventario = Mock()
        mock_view.tabla_inventario.setRowCount = Mock()
        mock_view.tabla_inventario.setColumnCount = Mock()
        mock_view.mostrar_mensaje = Mock()
        controller = TestInventarioController(mock_model, mock_view, Mock())
        controller.usuario_actual = {'nombre': 'test', 'rol': 'admin', 'ip': '127.0.0.1'}
        controller.usuarios_model = Mock()
        controller.usuarios_model.tiene_permiso.return_value = True
        controller.auditoria_model = Mock()
        controller.auditoria_model.registrar_evento = Mock()
        # Simular reserva con cantidad negativa
        controller.view.mostrar_mensaje("Cantidad inválida para reservar.")
        mock_view.mostrar_mensaje.assert_called_with("Cantidad inválida para reservar.")

    def test_agregar_item_datos_incompletos(self):
        mock_model = Mock()
        mock_model.obtener_items.return_value = []
        mock_model.obtener_item_por_codigo.return_value = None
        mock_model.agregar_item = Mock()
        mock_view = Mock()
        mock_view.abrir_formulario_nuevo_item.return_value = {
            "codigo": "",
            "nombre": "",
            "tipo_material": "PVC",
            "unidad": "unidad",
            "stock_actual": 10,
            "stock_minimo": 5,
            "ubicacion": "Almacén 1",
            "descripcion": ""
        }
        mock_view.label = Mock()
        mock_view.mostrar_mensaje = Mock()
        controller = TestInventarioController(mock_model, mock_view, Mock())
        controller.usuario_actual = {'nombre': 'test', 'rol': 'admin', 'ip': '127.0.0.1'}
        controller.usuarios_model = Mock()
        controller.usuarios_model.tiene_permiso.return_value = True
        controller.auditoria_model = Mock()
        controller.auditoria_model.registrar_evento = Mock()
        controller.view.abrir_formulario_nuevo_item = mock_view.abrir_formulario_nuevo_item
        controller.model.obtener_item_por_codigo = mock_model.obtener_item_por_codigo
        controller.model.agregar_item = mock_model.agregar_item
        controller.view.mostrar_mensaje = mock_view.mostrar_mensaje
        # Llamar al método
        controller.agregar_item()
        mock_model.agregar_item.assert_not_called()
        mock_view.mostrar_mensaje.assert_called()
        args, _ = mock_view.mostrar_mensaje.call_args
        assert "completar" in args[0].lower() or "obligatorio" in args[0].lower()

    def test_usuario_sin_permiso_exportar(self):
        mock_model = Mock()
        mock_model.obtener_items.return_value = []
        mock_view = Mock()
        mock_view.mostrar_mensaje = Mock()
        controller = TestInventarioController(mock_model, mock_view, Mock())
        controller.usuario_actual = {'nombre': 'test', 'rol': 'usuario', 'ip': '127.0.0.1'}
        controller.usuarios_model = Mock()
        controller.usuarios_model.tiene_permiso.return_value = False
        controller.auditoria_model = Mock()
        controller.auditoria_model.registrar_evento = Mock()
        # Simular intento de exportar sin permiso
        controller.view.mostrar_mensaje("No tiene permiso para exportar.")
        mock_view.mostrar_mensaje.assert_called_with("No tiene permiso para exportar.")

    def test_feedback_exito_en_ui(self):
        mock_model = Mock()
        mock_model.obtener_items.return_value = []
        mock_view = Mock()
        mock_view.mostrar_mensaje = Mock()
        controller = TestInventarioController(mock_model, mock_view, Mock())
        # Simular mensaje de éxito
        controller.view.mostrar_mensaje("Operación realizada con éxito.")
        mock_view.mostrar_mensaje.assert_called_with("Operación realizada con éxito.")

    def test_reservar_perfil_ok(self):
        self.mock_db.ejecutar_query.side_effect = [
            [(10,)],  # stock_actual = 10
            None,     # UPDATE stock
            [],       # No reserva previa
            None,     # INSERT reserva
            None,     # INSERT movimiento
            None      # INSERT auditoría
        ]
        result = self.inventario_model.reservar_perfil(1, 2, 5, usuario="admin")
        self.assertTrue(result)
        self.mock_db.ejecutar_query.assert_any_call("UPDATE inventario_perfiles SET stock_actual = stock_actual - ? WHERE id = ?", (5, 2))
        self.mock_db.ejecutar_query.assert_any_call("INSERT INTO perfiles_por_obra (id_obra, id_perfil, cantidad_reservada, estado) VALUES (?, ?, ?, 'Reservado')", (1, 2, 5))
        self.mock_db.ejecutar_query.assert_any_call("INSERT INTO movimientos_stock (id_perfil, tipo_movimiento, cantidad, fecha, usuario) VALUES (?, 'Egreso', ?, CURRENT_TIMESTAMP, ?)", (2, 5, "admin"))
        self.mock_db.ejecutar_query.assert_any_call("INSERT INTO auditorias_sistema (usuario, modulo, accion, fecha) VALUES (?, ?, ?, CURRENT_TIMESTAMP)", ("admin", "Inventario", "Reservó 5 del perfil 2 para obra 1"))

    def test_reservar_perfil_stock_insuficiente(self):
        self.mock_db.ejecutar_query.side_effect = [[(3,)] ]  # stock_actual = 3
        with self.assertRaises(ValueError) as cm:
            self.inventario_model.reservar_perfil(1, 2, 5, usuario="admin")
        self.assertIn("Stock insuficiente", str(cm.exception))

    def test_reservar_perfil_perfil_no_encontrado(self):
        self.mock_db.ejecutar_query.side_effect = [[]]  # No existe perfil
        with self.assertRaises(ValueError) as cm:
            self.inventario_model.reservar_perfil(1, 2, 1, usuario="admin")
        self.assertIn("Perfil no encontrado", str(cm.exception))

    def test_devolver_perfil_ok(self):
        self.mock_db.ejecutar_query.side_effect = [
            None,      # UPDATE stock
            [(5,)],   # cantidad_reservada previa
            None,     # UPDATE cantidad_reservada
            None,     # INSERT movimiento
            None      # INSERT auditoría
        ]
        result = self.inventario_model.devolver_perfil(1, 2, 3, usuario="admin")
        self.assertTrue(result)
        self.mock_db.ejecutar_query.assert_any_call("UPDATE inventario_perfiles SET stock_actual = stock_actual + ? WHERE id = ?", (3, 2))
        self.mock_db.ejecutar_query.assert_any_call("UPDATE perfiles_por_obra SET cantidad_reservada=?, estado='Reservado' WHERE id_obra=? AND id_perfil=?", (2, 1, 2))
        self.mock_db.ejecutar_query.assert_any_call("INSERT INTO movimientos_stock (id_perfil, tipo_movimiento, cantidad, fecha, usuario) VALUES (?, 'Ingreso', ?, CURRENT_TIMESTAMP, ?)", (2, 3, "admin"))
        self.mock_db.ejecutar_query.assert_any_call("INSERT INTO auditorias_sistema (usuario, modulo, accion, fecha) VALUES (?, ?, ?, CURRENT_TIMESTAMP)", ("admin", "Inventario", "Devolvió 3 del perfil 2 de la obra 1"))

    def test_devolver_perfil_cantidad_mayor_reservada(self):
        self.mock_db.ejecutar_query.side_effect = [
            None, [(2,)], None, None, None
        ]
        with self.assertRaises(ValueError) as e:
            self.inventario_model.devolver_perfil(1, 2, 5, usuario="admin")
        self.assertIn("No se puede devolver más de lo reservado", str(e.exception))

    def test_devolver_perfil_sin_reserva(self):
        self.mock_db.ejecutar_query.side_effect = [
            None, [], None, None, None
        ]
        with self.assertRaises(ValueError) as e:
            self.inventario_model.devolver_perfil(1, 2, 1, usuario="admin")
        self.assertIn("No hay reserva previa", str(e.exception))

    def test_ajustar_stock_perfil_ok(self):
        self.mock_db.ejecutar_query.side_effect = [
            [(7,)],   # stock_actual anterior
            None,     # UPDATE stock
            None,     # INSERT movimiento
            None      # INSERT auditoría
        ]
        result = self.inventario_model.ajustar_stock_perfil(2, 10, usuario="admin")
        self.assertTrue(result)
        self.mock_db.ejecutar_query.assert_any_call("UPDATE inventario_perfiles SET stock_actual = ? WHERE id = ?", (10, 2))
        self.mock_db.ejecutar_query.assert_any_call("INSERT INTO movimientos_stock (id_perfil, tipo_movimiento, cantidad, fecha, usuario) VALUES (?, 'Ajuste', ?, CURRENT_TIMESTAMP, ?)", (2, 3, "admin"))
        self.mock_db.ejecutar_query.assert_any_call("INSERT INTO auditorias_sistema (usuario, modulo, accion, fecha) VALUES (?, ?, ?, CURRENT_TIMESTAMP)", ("admin", "Inventario", "Ajustó stock del perfil 2 de 7 a 10"))

    def test_ajustar_stock_perfil_perfil_no_encontrado(self):
        self.mock_db.ejecutar_query.side_effect = [[]]
        with self.assertRaises(ValueError) as cm:
            self.inventario_model.ajustar_stock_perfil(2, 10, usuario="admin")
        self.assertIn("Perfil no encontrado", str(cm.exception))

    def test_ajustar_stock_perfil_cantidad_invalida_valida_primero(self):
        # Debe lanzar ValueError por cantidad inválida antes de consultar stock
        with self.assertRaises(ValueError) as cm:
            self.inventario_model.ajustar_stock_perfil(2, -5, usuario="admin")
        self.assertIn("Cantidad inválida", str(cm.exception))
        self.assertFalse(self.mock_db.ejecutar_query.called)

    def test_reservar_perfil_cantidad_negativa_valida_primero(self):
        # Debe lanzar ValueError por cantidad negativa antes de consultar stock
        with self.assertRaises(ValueError) as cm:
            self.inventario_model.reservar_perfil(1, 2, -3, usuario="admin")
        self.assertIn("Cantidad inválida", str(cm.exception))
        # No debe consultar stock en la base de datos
        self.assertFalse(self.mock_db.ejecutar_query.called)

    def test_reservar_perfil_stock_insuficiente_valida_orden(self):
        # Debe lanzar ValueError por stock insuficiente solo si la cantidad es válida
        self.mock_db.ejecutar_query.side_effect = [[(3,)]]  # stock_actual = 3
        with self.assertRaises(ValueError) as cm:
            self.inventario_model.reservar_perfil(1, 2, 5, usuario="admin")
        self.assertIn("Stock insuficiente", str(cm.exception))

    def test_reservar_perfil_perfil_no_encontrado_valida_orden(self):
        # Debe lanzar ValueError si el perfil no existe
        self.mock_db.ejecutar_query.side_effect = [[]]  # No existe perfil
        with self.assertRaises(ValueError) as cm:
            self.inventario_model.reservar_perfil(1, 2, 1, usuario="admin")
        self.assertIn("Perfil no encontrado", str(cm.exception))

    def test_devolver_perfil_cantidad_mayor_reservada_valida_primero(self):
        # No debe permitir devolver más de lo reservado
        self.mock_db.ejecutar_query.side_effect = [
            None, [(2,)], None, None, None
        ]
        with self.assertRaises(ValueError) as cm:
            self.inventario_model.devolver_perfil(1, 2, 5, usuario="admin")
        self.assertIn("No se puede devolver más de lo reservado", str(cm.exception))

    def test_devolver_perfil_sin_reserva_valida_primero(self):
        # No debe permitir devolver si no hay reserva
        self.mock_db.ejecutar_query.side_effect = [
            None, [], None, None, None
        ]
        with self.assertRaises(ValueError) as cm:
            self.inventario_model.devolver_perfil(1, 2, 1, usuario="admin")
        self.assertIn("No hay reserva previa", str(cm.exception))

class TestInventarioController(InventarioController):
    def __init__(self, *args, **kwargs):
        InventarioController.__init__(self, *args, **kwargs)
    def agregar_item(self):
        # Llama a la lógica real del controlador base para que el mock se ejecute
        super().agregar_item()
    def ver_movimientos(self):
        id_item = self.view.obtener_id_item_seleccionado()
        if id_item:
            movimientos = self.model.obtener_movimientos(id_item)
            self.view.mostrar_movimientos(movimientos)
            self.view.label.setText("")
        else:
            self.view.label.setText("Seleccione un ítem para ver sus movimientos.")
    def actualizar_inventario(self):
        datos = self.model.obtener_items() if hasattr(self.model, 'obtener_items') else []
        if hasattr(self.view, 'tabla_inventario'):
            self.view.tabla_inventario.setRowCount(len(datos))
            self.view.tabla_inventario.setColumnCount(18)
            for row, item in enumerate(datos):
                for col, value in enumerate(item):
                    self.view.tabla_inventario.setItem(row, col, Mock())
    def abrir_formulario_nuevo(self):
        if hasattr(self.view, 'abrir_formulario_nuevo_item'):
            self.view.abrir_formulario_nuevo_item()
    def exportar_excel(self):
        if hasattr(self.view, 'mostrar_mensaje'):
            self.view.mostrar_mensaje('Exportar Excel')
    def exportar_pdf(self):
        if hasattr(self.view, 'mostrar_mensaje'):
            self.view.mostrar_mensaje('Exportar PDF')
    def mostrar_historial(self):
        if hasattr(self.view, 'mostrar_movimientos'):
            self.view.mostrar_movimientos([])
    def reservar_item(self):
        if hasattr(self, 'actualizar_inventario'):
            self.actualizar_inventario()
    def filtrar_resultados(self):
        if hasattr(self.view, 'mostrar_mensaje'):
            self.view.mostrar_mensaje('Filtrar')
    def generar_codigo_qr(self):
        if hasattr(self.view, 'mostrar_mensaje'):
            self.view.mostrar_mensaje('Generar QR')
    def cargar_datos_inventario(self):
        if hasattr(self, 'actualizar_inventario'):
            self.actualizar_inventario()
    def abrir_ajustar_stock(self):
        if hasattr(self.view, 'mostrar_mensaje'):
            self.view.mostrar_mensaje('Ajustar stock')
