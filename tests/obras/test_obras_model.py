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

def test_alta_obra_exitosa(model, mocker):
    datos = {
        "nombre": "Obra Test",
        "cliente_id": "ClienteX",
        "fecha_medicion": "2025-06-01",
        "fecha_entrega": "2025-07-01"
    }
    mock_auditoria = mocker.patch("modules.auditoria.helpers._registrar_evento_auditoria")
    id_obra = model.alta_obra(datos, usuario="tester")
    obras = model.db_connection.ejecutar_query("SELECT * FROM obras WHERE id=?", (id_obra,))
    assert len(obras) == 1
    assert obras[0][1] == "Obra Test"
    assert obras[0][2] == "ClienteX"
    assert obras[0][3] is None or obras[0][3] == "Medición"  # estado
    assert obras[0][10] == "2025-06-01"  # fecha_medicion
    assert obras[0][12] == "2025-07-01"  # fecha_entrega
    mock_auditoria.assert_called_once()

def test_alta_obra_datos_invalidos(model):
    datos = {"nombre": "", "cliente_id": ""}  # Faltan campos requeridos
    with pytest.raises(ValueError):
        model.alta_obra(datos, usuario="tester")
    assert model.listar_obras() == []  # No se insertó nada

def test_alta_obra_rollback_por_excepcion(model, mocker):
    datos = {
        "nombre": "Obra Rollback",
        "cliente_id": "ClienteY",
        "fecha_medicion": "2025-06-01",
        "fecha_entrega": "2025-07-01"
    }
    mocker.patch("modules.auditoria.helpers._registrar_evento_auditoria", side_effect=Exception("Fallo auditoría"))
    with pytest.raises(Exception):
        model.alta_obra(datos, usuario="tester")
    assert model.listar_obras() == []  # Rollback efectivo

def test_alta_obra_rowversion_generado(model, mocker):
    datos = {
        "nombre": "Obra Rowversion",
        "cliente_id": "ClienteZ",
        "fecha_medicion": "2025-06-01",
        "fecha_entrega": "2025-07-01"
    }
    mocker.patch("modules.auditoria.helpers._registrar_evento_auditoria")
    id_obra = model.alta_obra(datos, usuario="tester")
    row = model.db_connection.ejecutar_query("SELECT rowversion FROM obras WHERE id=?", (id_obra,))
    assert row and isinstance(row[0][0], (bytes, bytearray)) and len(row[0][0]) == 8
