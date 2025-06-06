import pytest
import sqlite3
from modules.obras.model import ObrasModel, OptimisticLockError

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

def test_listar_obras_vacia(model):
    assert model.listar_obras() == []

def test_insertar_y_listar_obra(model):
    model.db_connection.ejecutar_query(
        "INSERT INTO obras (nombre, cliente, estado, fecha, fecha_entrega) VALUES (?,?,?,?,?)",
        ("Prueba", "Cliente1", "Medición", "2025-06-01", "2025-07-01")
    )
    obras = model.listar_obras()
    assert len(obras) == 1
    fila = obras[0]
    assert fila[0] is not None and fila[1] == "Prueba" and fila[2] == "Cliente1"
    assert fila[5] == "2025-07-01"
    assert fila[6] is not None

def test_editar_obra_conflicto_rowversion(model):
    model.db_connection.ejecutar_query(
        "INSERT INTO obras (nombre, cliente, estado, fecha, fecha_entrega) VALUES (?,?,?,?,?)",
        ("Prueba", "Cliente1", "Medición", "2025-06-01", "2025-07-01")
    )
    fila = model.listar_obras()[0]
    id_obra, rowversion_orig = fila[0], fila[6]
    # Simular edición concurrente
    model.db_connection.ejecutar_query(
        "UPDATE obras SET nombre=? WHERE id=?",
        ("Otro", id_obra)
    )
    # Cambia el rowversion
    model.db_connection.ejecutar_query(
        "UPDATE obras SET rowversion=randomblob(8) WHERE id=?",
        (id_obra,)
    )
    with pytest.raises(OptimisticLockError):
        model.editar_obra(id_obra, {"nombre": "Nuevo"}, rowversion_orig)
