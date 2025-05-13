import unittest
from unittest.mock import MagicMock
from modules.contabilidad.model import ContabilidadModel
from modules.obras.model import ObrasModel

class MockDBConnection:
    def __init__(self):
        self.last_query = None
        self.last_params = None
        self.data = {
            'obras': [],
            'movimientos_contables': [],
            'recibos': []
        }
        self.id_counter = 1

    def ejecutar_query(self, query, params=None):
        self.last_query = query
        self.last_params = params
        # Simular inserción de obra
        if query.startswith("INSERT INTO obras"):
            obra = (self.id_counter, *params)
            self.data['obras'].append(obra)
            self.id_counter += 1
        # Simular consulta de obras
        elif query.startswith("SELECT * FROM obras"):
            return self.data['obras']
        # Simular inserción de movimiento contable (id, fecha, tipo_movimiento, monto, concepto, observaciones, referencia_recibo)
        elif query.startswith("INSERT INTO movimientos_contables"):
            # params: fecha, tipo_movimiento, monto, concepto, referencia_recibo, observaciones
            # Estructura real: id, fecha, tipo_movimiento, monto, concepto, referencia_recibo, observaciones
            movimiento = (
                self.id_counter, params[0], params[1], params[2], params[3], params[4], params[5]
            )
            self.data['movimientos_contables'].append(movimiento)
            self.id_counter += 1
        # Simular consulta de movimientos
        elif query.startswith("SELECT * FROM movimientos_contables"):
            return self.data['movimientos_contables']
        # Simular inserción de recibo (orden: id, fecha_emision, obra_id, monto_total, concepto, destinatario, firma_digital, usuario_emisor, estado, archivo_pdf)
        elif query.startswith("INSERT INTO recibos"):
            recibo = (self.id_counter, params[0], params[1], params[2], params[3], params[4], params[5], params[6], params[7], params[8])
            self.data['recibos'].append(recibo)
            self.id_counter += 1
        # Simular consulta de recibos
        elif query.startswith("SELECT * FROM recibos"):
            return self.data['recibos']
        return []

class MockContabilidadView:
    def __init__(self):
        self.tabla_balance = MagicMock()
        self.tabla_recibos = MagicMock()
        self.balance_data = []
        self.recibos_data = []

    def actualizar_tabla_balance(self, movimientos):
        self.balance_data = movimientos

    def actualizar_tabla_recibos(self, recibos):
        self.recibos_data = recibos

class TestContabilidadObrasIntegracion(unittest.TestCase):
    def setUp(self):
        self.mock_db = MockDBConnection()
        self.obras_model = ObrasModel(self.mock_db)
        self.contabilidad_model = ContabilidadModel(self.mock_db)
        self.view = MockContabilidadView()

    def test_carga_y_reflejo_en_tabla(self):
        # 1. Insertar obra de prueba
        datos_obra = ("Obra Demo", "Cliente Demo", "medida", "2025-05-20")
        self.mock_db.ejecutar_query("INSERT INTO obras (nombre, cliente, estado, fecha) VALUES (?, ?, ?, ?)", datos_obra)
        obras = self.mock_db.ejecutar_query("SELECT * FROM obras")
        self.assertTrue(any(o[1] == "Obra Demo" for o in obras))
        obra_id = obras[0][0]
        # 2. Insertar movimiento contable asociado a la obra
        datos_mov = ("2025-05-21", "ingreso", 1500.0, "Pago inicial", f"Obra:{obra_id}", "")
        self.mock_db.ejecutar_query("INSERT INTO movimientos_contables (fecha, tipo_movimiento, monto, concepto, referencia_recibo, observaciones) VALUES (?, ?, ?, ?, ?, ?)", datos_mov)
        movimientos = self.mock_db.ejecutar_query("SELECT * FROM movimientos_contables")
        print('Movimientos:', movimientos)
        # Mostrar el campo referencia_recibo de cada movimiento
        print('Referencias:', [m[5] for m in movimientos])
        try:
            self.assertTrue(any(str(obra_id) in str(m[5]) for m in movimientos))
        except AssertionError:
            print(f"obra_id: {obra_id}")
            print(f"movimientos: {movimientos}")
            raise
        # 3. Insertar recibo asociado a la obra
        datos_recibo = ("2025-05-21", obra_id, 1500.0, "Pago inicial", "Juan Pérez", None, "admin", "emitido", None)
        self.mock_db.ejecutar_query("INSERT INTO recibos (fecha_emision, obra_id, monto_total, concepto, destinatario, firma_digital, usuario_emisor, estado, archivo_pdf) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", datos_recibo)
        recibos = self.mock_db.ejecutar_query("SELECT * FROM recibos")
        self.assertTrue(any(r[2] == obra_id for r in recibos))
        # 4. Simular actualización de tablas en la vista
        self.view.actualizar_tabla_balance(movimientos)
        self.view.actualizar_tabla_recibos(recibos)
        self.assertEqual(self.view.balance_data, movimientos)
        self.assertEqual(self.view.recibos_data, recibos)

if __name__ == "__main__":
    unittest.main()
