import unittest
from unittest.mock import Mock
from modules.vidrios.model import VidriosModel

class TestVidriosModel(unittest.TestCase):
    def setUp(self):
        self.mock_db = Mock()
        self.mock_db.transaction = Mock()
        self.mock_db.transaction.return_value.__enter__ = lambda s: s
        self.mock_db.transaction.return_value.__exit__ = lambda s, exc_type, exc_val, tb: None
        self.model = VidriosModel(self.mock_db)

    def test_reservar_vidrio_exitoso(self):
        self.mock_db.ejecutar_query.side_effect = [
            [(50,)],  # stock_actual
            None,     # UPDATE stock
            [],       # No reserva previa
            None,     # INSERT reserva
            None,     # INSERT movimiento
            None      # INSERT auditoría
        ]
        result = self.model.reservar_vidrio("test", 1, 1, 10)
        self.assertTrue(result)
        self.mock_db.ejecutar_query.assert_any_call("UPDATE vidrios SET stock_actual = stock_actual - ? WHERE id_vidrio = ?", (10, 1))
        self.mock_db.ejecutar_query.assert_any_call("INSERT INTO vidrios_por_obra (id_obra, id_vidrio, cantidad_reservada, estado) VALUES (?, ?, ?, 'Reservado')", (1, 1, 10))
        self.mock_db.ejecutar_query.assert_any_call("INSERT INTO movimientos_vidrios (id_vidrio, tipo_movimiento, cantidad, fecha, usuario) VALUES (?, 'Egreso', ?, CURRENT_TIMESTAMP, ?)", (1, 10, "test"))
        self.mock_db.ejecutar_query.assert_any_call("INSERT INTO auditorias_sistema (usuario, modulo, accion, fecha) VALUES (?, ?, ?, CURRENT_TIMESTAMP)", ("test", "Vidrios", "Reservó 10 del vidrio 1 para obra 1"))

    def test_reservar_vidrio_insuficiente(self):
        self.mock_db.ejecutar_query.side_effect = [[(5,)]]  # stock_actual = 5
        with self.assertRaises(ValueError) as cm:
            self.model.reservar_vidrio("test", 1, 1, 10)
        self.assertIn("Stock insuficiente", str(cm.exception))

    def test_reservar_vidrio_no_encontrado(self):
        self.mock_db.ejecutar_query.side_effect = [[]]
        with self.assertRaises(ValueError) as cm:
            self.model.reservar_vidrio("test", 1, 1, 1)
        self.assertIn("Vidrio no encontrado", str(cm.exception))

    def test_reservar_vidrio_cantidad_invalida(self):
        with self.assertRaises(ValueError) as cm:
            self.model.reservar_vidrio("test", 1, 1, -2)
        self.assertIn("Cantidad inválida", str(cm.exception))
        self.assertFalse(self.mock_db.ejecutar_query.called)

    def test_devolver_vidrio_exitoso(self):
        self.mock_db.ejecutar_query.side_effect = [
            None,      # UPDATE stock
            [(10,)],  # cantidad_reservada previa
            None,     # UPDATE cantidad_reservada
            None,     # INSERT movimiento
            None      # INSERT auditoría
        ]
        result = self.model.devolver_vidrio("test", 1, 1, 5)
        self.assertTrue(result)
        self.mock_db.ejecutar_query.assert_any_call("UPDATE vidrios SET stock_actual = stock_actual + ? WHERE id_vidrio = ?", (5, 1))
        self.mock_db.ejecutar_query.assert_any_call("UPDATE vidrios_por_obra SET cantidad_reservada = ?, estado = 'Reservado' WHERE id_obra = ? AND id_vidrio = ?", (5, 1, 1))
        self.mock_db.ejecutar_query.assert_any_call("INSERT INTO movimientos_vidrios (id_vidrio, tipo_movimiento, cantidad, fecha, usuario) VALUES (?, 'Ingreso', ?, CURRENT_TIMESTAMP, ?)", (1, 5, "test"))
        self.mock_db.ejecutar_query.assert_any_call("INSERT INTO auditorias_sistema (usuario, modulo, accion, fecha) VALUES (?, ?, ?, CURRENT_TIMESTAMP)", ("test", "Vidrios", "Devolvió 5 del vidrio 1 de la obra 1"))

    def test_devolver_vidrio_sin_reserva(self):
        self.mock_db.ejecutar_query.side_effect = [
            None, [], None, None, None
        ]
        with self.assertRaises(ValueError) as cm:
            self.model.devolver_vidrio("test", 1, 1, 1)
        self.assertIn("No hay reserva previa", str(cm.exception))

    def test_devolver_vidrio_cantidad_mayor_reservada(self):
        self.mock_db.ejecutar_query.side_effect = [
            None, [(2,)], None, None, None
        ]
        with self.assertRaises(ValueError) as cm:
            self.model.devolver_vidrio("test", 1, 1, 5)
        self.assertIn("No se puede devolver más de lo reservado", str(cm.exception))

    def test_ajustar_stock_vidrio_ok(self):
        self.mock_db.ejecutar_query.side_effect = [
            [(7,)],   # stock_actual anterior
            None,     # UPDATE stock
            None,     # INSERT movimiento
            None      # INSERT auditoría
        ]
        result = self.model.ajustar_stock_vidrio("test", 1, 10)
        self.assertTrue(result)
        self.mock_db.ejecutar_query.assert_any_call("UPDATE vidrios SET stock_actual = ? WHERE id_vidrio = ?", (10, 1))
        self.mock_db.ejecutar_query.assert_any_call("INSERT INTO movimientos_vidrios (id_vidrio, tipo_movimiento, cantidad, fecha, usuario) VALUES (?, 'Ajuste', ?, CURRENT_TIMESTAMP, ?)", (1, 3, "test"))
        self.mock_db.ejecutar_query.assert_any_call("INSERT INTO auditorias_sistema (usuario, modulo, accion, fecha) VALUES (?, ?, ?, CURRENT_TIMESTAMP)", ("test", "Vidrios", "Ajustó stock del vidrio 1 de 7 a 10"))

    def test_ajustar_stock_vidrio_invalido(self):
        with self.assertRaises(ValueError) as cm:
            self.model.ajustar_stock_vidrio("test", 1, -3)
        self.assertIn("Cantidad inválida", str(cm.exception))
        self.assertFalse(self.mock_db.ejecutar_query.called)

if __name__ == "__main__":
    unittest.main()
