import pytest
import sqlite3
from modules.obras.model import ObrasModel, OptimisticLockError
from modules.obras.controller import ObrasController

@pytest.fixture
def db_conn():
    conn = sqlite3.connect(":memory:")
    conn.execute("""
        CREATE TABLE obras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            cliente TEXT NOT NULL,
            estado TEXT,
            fecha TEXT,
            fecha_entrega TEXT,
            rowversion BLOB DEFAULT (randomblob(8)),
            fecha_compra TEXT,
            cantidad_aberturas INTEGER,
            pago_completo INTEGER,
            pago_porcentaje REAL,
            monto_usd REAL,
            monto_ars REAL,
            fecha_medicion TEXT,
            dias_entrega INTEGER,
            usuario_creador TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE auditorias_sistema (
            usuario_id INTEGER,
            modulo TEXT,
            accion TEXT,
            detalle TEXT,
            ip TEXT,
            fecha DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    yield conn
    conn.close()

@pytest.fixture
def model(db_conn):
    class DummyConn:
        def __init__(self, c): self.connection = c
        def ejecutar_query(self, q, p=()):
            cur = self.connection.cursor()
            cur.execute(q, p)
            self.connection.commit()
            return cur.fetchall()
        def ejecutar_query_return_rowcount(self, q, p=()):
            cur = self.connection.cursor()
            cur.execute(q, p)
            self.connection.commit()
            return cur.rowcount
    return ObrasModel(DummyConn(db_conn))

@pytest.fixture
def controller(model, db_conn):
    class DummyUsuarios:
        def tiene_permiso(self, usuario, modulo, accion): return True
    class DummyAuditoria:
        def registrar_evento(self, *a, **k): pass
    usuario = {'id': 1, 'username': 'admin', 'ip': '127.0.0.1'}
    ctrl = ObrasController(model, None, db_conn, DummyUsuarios(), usuario)
    ctrl.db_conn = db_conn  # Agrega referencia directa para los tests
    return ctrl

def test_alta_obra_exitoso(controller, model):
    datos = {
        'nombre': 'Obra1',
        'cliente_id': 2,
        'fecha_medicion': '2025-06-01',
        'fecha_entrega': '2025-07-01'
    }
    id_obra = controller.alta_obra(datos)
    obras = model.listar_obras()
    assert any(o[0] == id_obra and o[1] == 'Obra1' for o in obras)
    # Auditoría
    res = controller.model.db_connection.connection.execute("SELECT * FROM auditorias_sistema WHERE modulo='Obras' AND accion LIKE 'Creó obra%' ").fetchall()
    assert res

def test_editar_obra_exitoso(controller, model):
    model.db_connection.ejecutar_query(
        "INSERT INTO obras (nombre, cliente, estado, fecha, fecha_entrega) VALUES (?,?,?,?,?)",
        ("Obra2", "Cliente2", "Medición", "2025-06-01", "2025-07-01")
    )
    fila = model.listar_obras()[0]
    id_obra, rowversion_orig = fila[0], fila[6]
    datos_mod = {'nombre': 'Obra2Edit', 'cliente': 'Cliente2', 'estado': 'Medición', 'fecha_entrega': '2025-07-02'}
    nuevo_row = controller.editar_obra(id_obra, datos_mod, rowversion_orig)
    fila2 = model.listar_obras()[0]
    assert fila2[1] == 'Obra2Edit' and fila2[6] != rowversion_orig
    res = controller.model.db_connection.connection.execute("SELECT * FROM auditorias_sistema WHERE accion LIKE 'Editó obra%' ").fetchall()
    assert res

def test_editar_obra_conflicto(controller, model):
    model.db_connection.ejecutar_query(
        "INSERT INTO obras (nombre, cliente, estado, fecha, fecha_entrega) VALUES (?,?,?,?,?)",
        ("Obra3", "Cliente3", "Medición", "2025-06-01", "2025-07-01")
    )
    fila = model.listar_obras()[0]
    id_obra, rowversion_orig = fila[0], fila[6]
    # Simular edición concurrente
    model.db_connection.ejecutar_query("UPDATE obras SET rowversion=randomblob(8) WHERE id=?", (id_obra,))
    datos_mod = {'nombre': 'Obra3Edit', 'cliente': 'Cliente3', 'estado': 'Medición', 'fecha_entrega': '2025-07-02'}
    with pytest.raises(OptimisticLockError):
        controller.editar_obra(id_obra, datos_mod, rowversion_orig)
